#!/usr/bin/env bash
set -euo pipefail

PHASE=${1:?"Usage: $0 <phase> <experiment_name> <train.py> [ENV=VAL ...]"}
EXP_NAME=${2:?"Usage: $0 <phase> <experiment_name> <train.py> [ENV=VAL ...]"}
TRAIN_SRC=${3:?"Usage: $0 <phase> <experiment_name> <train.py> [ENV=VAL ...]"}
shift 3

IMAGE="${PGOLF_IMAGE:-pgolf-ready:latest}"
REPO_DIR="${PGOLF_REPO_DIR:-$HOME/parameter-golf}"
EXPERIMENTS_DIR="${PGOLF_EXPERIMENTS_DIR:-$HOME/experiments}"
EXPDIR="$EXPERIMENTS_DIR/$PHASE/$EXP_NAME"
TRAIN_PY="$EXPDIR/train.py"
FULL_LOG="$EXPDIR/full_log.txt"
RESULT_JSON="$EXPDIR/result.json"
CONFIG_JSON="$EXPDIR/config.json"
CURRENT_RUN="$EXPERIMENTS_DIR/current_run.txt"
CONTAINER="pgolf_${EXP_NAME}"
RUN_ID="${EXP_NAME}_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$EXPDIR" "$EXPDIR/logs"
cp "$TRAIN_SRC" "$TRAIN_PY"

python3 - "$CONFIG_JSON" "$PHASE" "$EXP_NAME" "$RUN_ID" "$IMAGE" "$TRAIN_PY" "$TRAIN_SRC" "$@" <<'PY'
import json
import pathlib
import sys
from datetime import datetime, timezone

path = pathlib.Path(sys.argv[1])
phase, exp_name, run_id, image, train_py, train_src, *env_overrides = sys.argv[2:]
payload = {
    "phase": phase,
    "experiment": exp_name,
    "run_id": run_id,
    "image": image,
    "train_py": train_py,
    "train_src": train_src,
    "env_overrides": env_overrides,
    "started_at_utc": datetime.now(timezone.utc).isoformat(),
}
path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

cat > "$CURRENT_RUN" <<EOF
Phase: $PHASE
Experiment: $EXP_NAME
Run ID: $RUN_ID
Image: $IMAGE
Train script: $TRAIN_PY
Full log: $FULL_LOG
Started: $(date -Iseconds)
Env overrides: $*
EOF

declare -a ENV_ARGS=(
    -e PYTHONUNBUFFERED=1
    -e RUN_ID="$RUN_ID"
    -e DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024
    -e TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model
)
for arg in "$@"; do
    ENV_ARGS+=(-e "$arg")
done

docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
: > "$FULL_LOG"

set +e
{
    echo "[runner] experiment=$EXP_NAME phase=$PHASE run_id=$RUN_ID"
    echo "[runner] image=$IMAGE"
    echo "[runner] train_py=$TRAIN_PY"
    echo "[runner] train_src=$TRAIN_SRC"
    echo "[runner] cwd=$EXPDIR"
    echo "[runner] env_overrides=$*"
    docker run --name "$CONTAINER" \
        --device=/dev/kfd \
        --device=/dev/dri \
        --group-add video \
        --ipc=host \
        --shm-size 16G \
        -v "$REPO_DIR":/workspace/parameter-golf \
        -v "$EXPERIMENTS_DIR":/workspace/experiments \
        -w "/workspace/experiments/$PHASE/$EXP_NAME" \
        "${ENV_ARGS[@]}" \
        "$IMAGE" \
        bash -lc "python3 -u /workspace/experiments/$PHASE/$EXP_NAME/train.py"
} 2>&1 | tee -a "$FULL_LOG"
status=${PIPESTATUS[0]}
set -e

docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
ln -sf full_log.txt "$EXPDIR/log.txt"

python3 - "$FULL_LOG" "$RESULT_JSON" "$PHASE" "$EXP_NAME" "$RUN_ID" "$status" "$@" <<'PY'
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

full_log = pathlib.Path(sys.argv[1])
result_json = pathlib.Path(sys.argv[2])
phase, exp_name, run_id, status_code, *env_overrides = sys.argv[3:]
text = full_log.read_text(encoding="utf-8", errors="replace")

def last_match(pattern: str):
    matches = re.findall(pattern, text, flags=re.MULTILINE)
    return matches[-1] if matches else None

float_val_bpb = last_match(r"^step:\d+/\d+ val_loss:[^ ]+ val_bpb:([^ ]+)")
float_val_loss = last_match(r"^step:\d+/\d+ val_loss:([^ ]+) val_bpb:")
quant_val_bpb = last_match(r"^final_int8_zlib_roundtrip .* val_bpb:([^ ]+)")
quant_val_loss = last_match(r"^final_int8_zlib_roundtrip val_loss:([^ ]+) val_bpb:")
steps = last_match(r"stopping_early:.*step:(\d+)/") or last_match(r"^step:(\d+)/\d+")
step_avg_ms = last_match(r"^step:\d+/\d+ .* step_avg:([^m]+)ms")
model_params = last_match(r"^model_params:(\d+)")
artifact_bytes = last_match(r"^Serialized model int8\+zlib: (\d+) bytes")

payload = {
    "phase": phase,
    "experiment": exp_name,
    "run_id": run_id,
    "status_code": int(status_code),
    "env_overrides": env_overrides,
    "float_val_loss": float(float_val_loss) if float_val_loss else None,
    "float_val_bpb": float(float_val_bpb) if float_val_bpb else None,
    "quant_val_loss": float(quant_val_loss) if quant_val_loss else None,
    "quant_val_bpb": float(quant_val_bpb) if quant_val_bpb else None,
    "steps": int(steps) if steps else None,
    "step_avg_ms": float(step_avg_ms) if step_avg_ms else None,
    "model_params": int(model_params) if model_params else None,
    "artifact_bytes": int(artifact_bytes) if artifact_bytes else None,
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
}
result_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY

cat >> "$CURRENT_RUN" <<EOF
Completed: $(date -Iseconds)
Exit code: $status
Result: $RESULT_JSON
EOF

echo ""
echo "======================================================="
echo "  $EXP_NAME COMPLETE"
echo "  exit_code: $status"
echo "  result_json: $RESULT_JSON"
echo "  full_log: $FULL_LOG"
echo "======================================================="

exit "$status"
