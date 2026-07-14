#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT="$SCRIPT_DIR/phase1"
REMOTE="hotaisle@23.183.40.75"

mkdir -p "$ROOT/exp001_11L_3xMLP" "$ROOT/exp003_ema" "$ROOT/exp004_partial_rope" "$ROOT/exp005_ln_scale"

scp "$REMOTE:~/experiments/exp001_11L_3xMLP/full_log.txt" "$ROOT/exp001_11L_3xMLP/log.txt"
scp "$REMOTE:~/experiments/exp003_ema/log.txt" "$ROOT/exp003_ema/log.txt"
scp "$REMOTE:~/experiments/exp004_partial_rope/log.txt" "$ROOT/exp004_partial_rope/log.txt"
scp "$REMOTE:~/experiments/exp005_ln_scale/log.txt" "$ROOT/exp005_ln_scale/log.txt"

echo "Synced Phase 1 logs into $ROOT"
