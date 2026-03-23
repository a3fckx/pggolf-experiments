#!/usr/bin/env bash
set -euo pipefail

ROOT="${PGOLF_EXPERIMENTS_DIR:-$HOME/experiments}"
RUNNER="${PGOLF_RUNNER:-$ROOT/run_snapshot_experiment.sh}"
PHASE="phase1"
BATCH_NAME="${BATCH_NAME:-phase1_exclusive_$(date +%Y%m%dT%H%M%S)}"
BATCH_LOG="$ROOT/${BATCH_NAME}.log"

PHASE1_MAX_WALLCLOCK_SECONDS="${PHASE1_MAX_WALLCLOCK_SECONDS:-600}"
PHASE1_TRAIN_LOG_EVERY="${PHASE1_TRAIN_LOG_EVERY:-100}"
PHASE1_VAL_LOSS_EVERY="${PHASE1_VAL_LOSS_EVERY:-400}"

exec > >(tee -a "$BATCH_LOG") 2>&1

run_one() {
    local exp_name=$1
    local train_src=$2
    shift 2
    echo ""
    echo ">>> $(date -Iseconds) :: starting $exp_name"
    bash "$RUNNER" "$PHASE" "$exp_name" "$train_src" "$@"
    echo ">>> $(date -Iseconds) :: finished $exp_name"
}

echo "[batch] Starting $BATCH_NAME at $(date -Iseconds)"
echo "[batch] Runner: $RUNNER"
echo "[batch] Default max wallclock seconds: $PHASE1_MAX_WALLCLOCK_SECONDS"
echo "[batch] Train log every: $PHASE1_TRAIN_LOG_EVERY"
echo "[batch] Val loss every: $PHASE1_VAL_LOSS_EVERY"

run_one exp001_11L_3xMLP_clean "$ROOT/phase1/exp001_11L_3xMLP/train.py" \
    NUM_LAYERS=11 \
    MLP_MULT=3 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp002_xsa4_clean "$ROOT/phase1/exp002_xsa4_clean/train.py" \
    XSA_LAYERS=4 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp003_ema_clean "$ROOT/phase1/exp003_ema/train.py" \
    EMA_DECAY=0.997 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp004_partial_rope_clean "$ROOT/phase1/exp004_partial_rope/train.py" \
    ROPE_DIM=16 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp005_ln_scale_clean "$ROOT/phase1/exp005_ln_scale/train.py" \
    LN_SCALE_ENABLED=1 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp006_smeargate "$ROOT/phase1/exp006_smeargate/train.py" \
    SMEAR_ENABLED=1 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp007_bigramhash "$ROOT/phase1/exp007_bigramhash/train.py" \
    BIGRAM_VOCAB_SIZE=2048 \
    BIGRAM_DIM=128 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

run_one exp008_late_qat "$ROOT/phase1/exp008_late_qat/train.py" \
    QAT_BITS=6 \
    QAT_START_FRAC=0.96 \
    MAX_WALLCLOCK_SECONDS="$PHASE1_MAX_WALLCLOCK_SECONDS" \
    TRAIN_LOG_EVERY="$PHASE1_TRAIN_LOG_EVERY" \
    VAL_LOSS_EVERY="$PHASE1_VAL_LOSS_EVERY"

echo ""
echo "[batch] Finished $BATCH_NAME at $(date -Iseconds)"
