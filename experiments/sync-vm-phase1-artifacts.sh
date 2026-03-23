#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT="$SCRIPT_DIR"
PHASE1_ROOT="$ROOT/phase1"
REMOTE="mi300x"

mkdir -p "$PHASE1_ROOT"

EXPERIMENTS=(
  exp001_11L_3xMLP
  exp001_11L_3xMLP_clean
  exp002_xsa4
  exp002_xsa4_clean
  exp003_ema
  exp003_ema_clean
  exp004_partial_rope
  exp004_partial_rope_clean
  exp005_ln_scale
  exp005_ln_scale_clean
  exp006_smeargate
  exp006_smeargate_clean
  exp007_bigramhash
  exp007_bigramhash_clean
  exp008_late_qat
  exp008_late_qat_clean
)

for exp in "${EXPERIMENTS[@]}"; do
  mkdir -p "$PHASE1_ROOT/$exp"
  rsync -av --prune-empty-dirs \
    --include='train.py' \
    --include='config.json' \
    --include='env_overrides.txt' \
    --include='result.json' \
    --include='full_log.txt' \
    --include='log.txt' \
    --include='status.txt' \
    --include='logs/***' \
    --exclude='*' \
    "$REMOTE:~/experiments/phase1/$exp/" "$PHASE1_ROOT/$exp/" 2>/dev/null || true
done

rsync -av "$REMOTE:~/experiments/phase1_exclusive_"*.log "$ROOT/" 2>/dev/null || true

echo "Synced Phase 1 artifacts into $PHASE1_ROOT"
