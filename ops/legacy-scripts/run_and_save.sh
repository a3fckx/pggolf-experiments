#!/usr/bin/env bash
set -euo pipefail

PHASE=${1:?"Usage: $0 <phase> <experiment_name> [ENV=VAL ...]"}
EXP_NAME=${2:?"Usage: $0 <phase> <experiment_name> [ENV=VAL ...]"}
shift 2

ROOT="$HOME/experiments"
EXPDIR="$ROOT/$PHASE/$EXP_NAME"
TRAIN_SCRIPT="${TRAIN_SCRIPT:-$EXPDIR/train.py}"
IMAGE="${PGOLF_IMAGE:-pgolf-ready:latest}"
CONTAINER="pgolf_${PHASE}_${EXP_NAME}"
RUN_TS=$(date +%Y%m%dT%H%M%S)
RUN_ID="${RUN_ID:-${PHASE}_${EXP_NAME}_${RUN_TS}}"
FULL_LOG="$EXPDIR/full_log.txt"
ENV_FILE="$EXPDIR/env_overrides.txt"
CONFIG_JSON="$EXPDIR/config.json"
RESULT_JSON="$EXPDIR/result.json"

mkdir -p "$EXPDIR"

if [ ! -f "$TRAIN_SCRIPT" ]; then
  echo "train script not found: $TRAIN_SCRIPT" >&2
  exit 1
fi

if [ "$TRAIN_SCRIPT" != "$EXPDIR/train.py" ]; then
  cp "$TRAIN_SCRIPT" "$EXPDIR/train.py"
fi

printf '%s\n' "$@" > "$ENV_FILE"

python3 - <<'PY' "$CONFIG_JSON" "$EXP_NAME" "$PHASE" "$IMAGE" "$RUN_ID" "$TRAIN_SCRIPT" "$RUN_TS" "$ENV_FILE"
import json
import pathlib
import sys

config_path, exp_name, phase, image, run_id, train_script, run_ts, env_file = sys.argv[1:]
env_lines = [line.strip() for line in pathlib.Path(env_file).read_text(encoding="utf-8").splitlines() if line.strip()]
payload = {
    "experiment": exp_name,
    "phase": phase,
    "image": image,
    "run_id": run_id,
    "source_train_script": train_script,
    "started_ts": run_ts,
    "env_overrides": env_lines,
}
pathlib.Path(config_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
rm -f "$FULL_LOG"

ENV_ARGS=(
  -e PYTHONUNBUFFERED=1
  -e DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024
  -e TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model
  -e RUN_ID="$RUN_ID"
)
for arg in "$@"; do
  ENV_ARGS+=(-e "$arg")
done

echo "[$EXP_NAME] Starting at $(date -Iseconds)"
echo "[$EXP_NAME] Phase: $PHASE"
echo "[$EXP_NAME] Image: $IMAGE"
echo "[$EXP_NAME] Run ID: $RUN_ID"
echo "[$EXP_NAME] Train script: $TRAIN_SCRIPT"
echo "[$EXP_NAME] Env file: $ENV_FILE"
echo "[$EXP_NAME] Full log: $FULL_LOG"

set +e
docker run --name "$CONTAINER" \
  --device=/dev/kfd \
  --device=/dev/dri \
  --group-add video \
  --ipc=host \
  --shm-size 16G \
  -v /home/hotaisle/parameter-golf:/workspace/parameter-golf \
  -v /home/hotaisle/experiments:/workspace/experiments \
  -w "/workspace/experiments/$PHASE/$EXP_NAME" \
  "${ENV_ARGS[@]}" \
  "$IMAGE" \
  bash -lc 'python3 -u train.py' \
  2>&1 | tee "$FULL_LOG"
status=${PIPESTATUS[0]}
set -e

FLOAT_LINE=$(grep '^step:' "$FULL_LOG" | grep 'val_bpb:' | tail -1 || true)
FLOAT_BPB=$(echo "$FLOAT_LINE" | sed -n 's/.*val_bpb:\([0-9.]*\).*/\1/p')
FLOAT_LOSS=$(echo "$FLOAT_LINE" | sed -n 's/.*val_loss:\([0-9.]*\).*/\1/p')
QUANT_LINE=$(grep 'final_int8_zlib_roundtrip ' "$FULL_LOG" | tail -1 || true)
QUANT_BPB=$(echo "$QUANT_LINE" | sed -n 's/.*val_bpb:\([0-9.]*\).*/\1/p')
QUANT_LOSS=$(echo "$QUANT_LINE" | sed -n 's/.*val_loss:\([0-9.]*\).*/\1/p')
LAST_STEP_LINE=$(grep '^step:' "$FULL_LOG" | tail -1 || true)
STEPS=$(echo "$LAST_STEP_LINE" | sed -n 's/^step:\([0-9]*\)\/.*/\1/p')
TRAIN_TIME_MS=$(echo "$LAST_STEP_LINE" | sed -n 's/.*train_time:\([0-9.]*\)ms.*/\1/p')
STEP_AVG_MS=$(echo "$LAST_STEP_LINE" | sed -n 's/.*step_avg:\([0-9.]*\)ms.*/\1/p')
MODEL_PARAMS=$(grep 'model_params:' "$FULL_LOG" | tail -1 | sed -n 's/.*model_params:\([0-9]*\).*/\1/p')
ARTIFACT_BYTES=$(grep 'Serialized model int8+zlib:' "$FULL_LOG" | tail -1 | sed -n 's/.*Serialized model int8+zlib: \([0-9]*\) bytes.*/\1/p')

python3 - <<'PY' "$RESULT_JSON" "$EXP_NAME" "$PHASE" "$status" "$FLOAT_LOSS" "$FLOAT_BPB" "$QUANT_LOSS" "$QUANT_BPB" "$STEPS" "$TRAIN_TIME_MS" "$STEP_AVG_MS" "$MODEL_PARAMS" "$ARTIFACT_BYTES"
import json
import pathlib
import sys

def maybe_num(text):
    if text in ("", "None", "null"):
        return None
    if "." in text:
        return float(text)
    return int(text)

(
    result_path,
    exp_name,
    phase,
    status,
    float_loss,
    float_bpb,
    quant_loss,
    quant_bpb,
    steps,
    train_time_ms,
    step_avg_ms,
    model_params,
    artifact_bytes,
) = sys.argv[1:]

payload = {
    "experiment": exp_name,
    "phase": phase,
    "exit_status": int(status),
    "float_val_loss": maybe_num(float_loss),
    "float_val_bpb": maybe_num(float_bpb),
    "quant_val_loss": maybe_num(quant_loss),
    "quant_val_bpb": maybe_num(quant_bpb),
    "steps": maybe_num(steps),
    "train_time_ms": maybe_num(train_time_ms),
    "step_avg_ms": maybe_num(step_avg_ms),
    "model_params": maybe_num(model_params),
    "artifact_bytes": maybe_num(artifact_bytes),
}
pathlib.Path(result_path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

docker rm -f "$CONTAINER" >/dev/null 2>&1 || true

echo
echo "============================================================"
echo "  $EXP_NAME COMPLETE"
echo "  exit_status: $status"
echo "  float_val_bpb: ${FLOAT_BPB:-N/A}"
echo "  quant_val_bpb: ${QUANT_BPB:-N/A}"
echo "  steps: ${STEPS:-N/A}, step_avg_ms: ${STEP_AVG_MS:-N/A}"
echo "  params: ${MODEL_PARAMS:-N/A}, artifact_bytes: ${ARTIFACT_BYTES:-N/A}"
echo "  artifacts: $EXPDIR"
echo "============================================================"

exit "$status"
