#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/experiments"
RUNNER="$ROOT/run_snapshot_experiment.sh"
COMPARE_SECONDS="${PHASE1_COMPARE_SECONDS:-600}"

run_one() {
  local exp_name=$1
  local train_py=$2
  shift 2

  echo ""
  echo "================================================================"
  echo "[$exp_name] batch_start $(date -Iseconds)"
  echo "================================================================"
  if "$RUNNER" phase1 "$exp_name" "$train_py" "$@"; then
    echo "[$exp_name] batch_status=ok"
  else
    echo "[$exp_name] batch_status=failed"
  fi
}

run_one exp001_11L_3xMLP_clean "$ROOT/phase1/exp001_11L_3xMLP_clean/train.py" \
  NUM_LAYERS=11 MLP_MULT=3 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp002_xsa4_clean "$ROOT/phase1/exp002_xsa4_clean/train.py" \
  XSA_LAYERS=4 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp003_ema_clean "$ROOT/phase1/exp003_ema_clean/train.py" \
  EMA_DECAY=0.997 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp004_partial_rope_clean "$ROOT/phase1/exp004_partial_rope_clean/train.py" \
  ROPE_DIM=16 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp005_ln_scale_clean "$ROOT/phase1/exp005_ln_scale_clean/train.py" \
  LN_SCALE_ENABLED=1 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp006_smeargate_clean "$ROOT/phase1/exp006_smeargate_clean/train.py" \
  SMEARGATE_ENABLED=1 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp007_bigramhash_clean "$ROOT/phase1/exp007_bigramhash_clean/train.py" \
  BIGRAM_HASH_SIZE=2048 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

run_one exp008_late_qat_clean "$ROOT/phase1/exp008_late_qat_clean/train.py" \
  LATE_QAT_ENABLED=1 LATE_QAT_BITS=6 LATE_QAT_FRAC=0.04 MAX_WALLCLOCK_SECONDS="$COMPARE_SECONDS"

echo ""
echo "================================================================"
echo "[phase1_clean_batch] complete $(date -Iseconds)"
echo "================================================================"
