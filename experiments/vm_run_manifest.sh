#!/usr/bin/env bash
set -euo pipefail

MANIFEST=${1:?"Usage: $0 /path/to/manifest.tsv"}
IMAGE=${PGOLF_IMAGE:-pgolf-ready:latest}
REPO_ROOT=${PGOLF_REPO_ROOT:-"$HOME/parameter-golf"}
EXP_ROOT=${PGOLF_EXP_ROOT:-"$HOME/experiments"}
DEFAULT_TRAIN_LOG_EVERY=${TRAIN_LOG_EVERY_DEFAULT:-100}
DEFAULT_VAL_LOSS_EVERY=${VAL_LOSS_EVERY_DEFAULT:-1000}

run_one() {
  local phase=$1
  local exp=$2
  local max_wallclock_seconds=$3
  local env_overrides=$4

  local expdir="$EXP_ROOT/$phase/$exp"
  local train_py="$expdir/train.py"
  local full_log="$expdir/full_log.txt"
  local status_file="$expdir/status.txt"
  local config_json="$expdir/config.json"
  local result_json="$expdir/result.json"
  local internal_logs="$expdir/internal_logs"
  local container="pgolf_${exp}"
  local run_id="${phase}_${exp}_$(date +%Y%m%dT%H%M%S)"

  if [[ ! -f "$train_py" ]]; then
    echo "[$exp] Missing train snapshot: $train_py" >&2
    return 1
  fi

  mkdir -p "$expdir" "$internal_logs"
  cat > "$config_json" <<EOF
{
  "experiment": "$exp",
  "phase": "$phase",
  "run_id": "$run_id",
  "image": "$IMAGE",
  "train_py": "$train_py",
  "max_wallclock_seconds": $max_wallclock_seconds,
  "env_overrides": "$env_overrides",
  "started": "$(date -Iseconds)"
}
EOF

  {
    echo "status:starting"
    echo "started:$(date -Iseconds)"
    echo "image:$IMAGE"
    echo "run_id:$run_id"
    echo "train_py:$train_py"
    echo "max_wallclock_seconds:$max_wallclock_seconds"
    echo "env_overrides:$env_overrides"
  } > "$status_file"

  docker rm -f "$container" >/dev/null 2>&1 || true

  local -a env_args=(
    -e PYTHONUNBUFFERED=1
    -e RUN_ID="$run_id"
    -e MAX_WALLCLOCK_SECONDS="$max_wallclock_seconds"
    -e TRAIN_LOG_EVERY="$DEFAULT_TRAIN_LOG_EVERY"
    -e VAL_LOSS_EVERY="$DEFAULT_VAL_LOSS_EVERY"
  )
  if [[ -n "$env_overrides" && "$env_overrides" != "-" ]]; then
    local -a extra_envs=()
    read -r -a extra_envs <<< "$env_overrides"
    for kv in "${extra_envs[@]}"; do
      env_args+=(-e "$kv")
    done
  fi

  echo "[$exp] starting at $(date -Iseconds)"
  echo "[$exp] image=$IMAGE wallclock=${max_wallclock_seconds}s env=[$env_overrides]"

  set +e
  docker run --name "$container" \
    --device=/dev/kfd \
    --device=/dev/dri \
    --group-add video \
    --ipc=host \
    --shm-size 16G \
    -v "$REPO_ROOT":/workspace/parameter-golf \
    -v "$EXP_ROOT":/workspace/experiments \
    -w /workspace/parameter-golf \
    "${env_args[@]}" \
    "$IMAGE" \
    bash -lc "cd /workspace/parameter-golf && python3 -u /workspace/experiments/$phase/$exp/train.py" \
    2>&1 | tee "$full_log"
  local exit_code=${PIPESTATUS[0]}
  set -e

  docker cp "$container":/workspace/parameter-golf/logs/. "$internal_logs/" >/dev/null 2>&1 || true

  local float_bpb
  local quant_bpb
  local quant_loss
  local step_avg_ms
  local steps
  local model_params

  float_bpb=$(grep "val_bpb" "$full_log" | grep "^step:" | tail -1 | sed -n 's/.*val_bpb:\([0-9.]*\).*/\1/p')
  quant_bpb=$(grep "final_int8_zlib_roundtrip " "$full_log" | tail -1 | sed -n 's/.*val_bpb:\([0-9.]*\).*/\1/p')
  quant_loss=$(grep "final_int8_zlib_roundtrip " "$full_log" | tail -1 | sed -n 's/.*val_loss:\([0-9.]*\).*/\1/p')
  step_avg_ms=$(grep "^step:" "$full_log" | tail -1 | sed -n 's/.*step_avg:\([0-9.]*\)ms.*/\1/p')
  steps=$(grep "stopping_early\|^step:" "$full_log" | tail -1 | sed -n 's/.*step:\([0-9][0-9]*\)\/.*/\1/p')
  model_params=$(grep "model_params:" "$full_log" | tail -1 | sed -n 's/.*model_params:\([0-9][0-9]*\).*/\1/p')

  cat > "$result_json" <<EOF
{
  "experiment": "$exp",
  "phase": "$phase",
  "run_id": "$run_id",
  "image": "$IMAGE",
  "max_wallclock_seconds": $max_wallclock_seconds,
  "env_overrides": "$env_overrides",
  "float_val_bpb": ${float_bpb:-null},
  "quant_val_bpb": ${quant_bpb:-null},
  "quant_val_loss": ${quant_loss:-null},
  "steps": ${steps:-null},
  "step_avg_ms": ${step_avg_ms:-null},
  "model_params": ${model_params:-null},
  "exit_code": $exit_code,
  "finished": "$(date -Iseconds)"
}
EOF

  {
    echo "status:complete"
    echo "finished:$(date -Iseconds)"
    echo "exit_code:$exit_code"
    echo "float_val_bpb:${float_bpb:-NA}"
    echo "quant_val_bpb:${quant_bpb:-NA}"
    echo "steps:${steps:-NA}"
    echo "step_avg_ms:${step_avg_ms:-NA}"
  } >> "$status_file"

  echo "[$exp] complete float=${float_bpb:-NA} quant=${quant_bpb:-NA} steps=${steps:-NA} step_avg_ms=${step_avg_ms:-NA}"

  docker rm -f "$container" >/dev/null 2>&1 || true
  return "$exit_code"
}

while IFS='|' read -r phase exp max_wallclock_seconds env_overrides; do
  if [[ -z "${phase// }" || "${phase:0:1}" == "#" ]]; then
    continue
  fi
  run_one "$phase" "$exp" "$max_wallclock_seconds" "${env_overrides:-}"
done < "$MANIFEST"
