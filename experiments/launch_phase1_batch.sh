#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-mi300x}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VAULT_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
LOCAL_PHASE1="$VAULT_ROOT/experiments/phase1"
LOCAL_MANIFEST="$VAULT_ROOT/experiments/phase1_manifest.tsv"
LOCAL_RUNNER="$VAULT_ROOT/experiments/vm_run_manifest.sh"
REMOTE_EXP_ROOT="~/experiments"
REMOTE_PHASE1="$REMOTE_EXP_ROOT/phase1"
BATCH_TS=$(date +%Y%m%dT%H%M%S)

ssh "$REMOTE" "mkdir -p $REMOTE_PHASE1"

while IFS= read -r train_py; do
  exp_name=$(basename "$(dirname "$train_py")")
  ssh "$REMOTE" "mkdir -p $REMOTE_PHASE1/$exp_name"
  scp "$train_py" "$REMOTE:$REMOTE_PHASE1/$exp_name/train.py"
done < <(find "$LOCAL_PHASE1" -mindepth 2 -maxdepth 2 -name train.py | sort)

scp "$LOCAL_MANIFEST" "$REMOTE:$REMOTE_EXP_ROOT/phase1_manifest.tsv"
scp "$LOCAL_RUNNER" "$REMOTE:$REMOTE_EXP_ROOT/vm_run_manifest.sh"

ssh "$REMOTE" "chmod +x $REMOTE_EXP_ROOT/vm_run_manifest.sh && nohup bash $REMOTE_EXP_ROOT/vm_run_manifest.sh $REMOTE_EXP_ROOT/phase1_manifest.tsv > $REMOTE_EXP_ROOT/phase1_batch_$BATCH_TS.log 2>&1 & echo \$! > $REMOTE_EXP_ROOT/phase1_batch_$BATCH_TS.pid"

echo "Launched phase1 batch on $REMOTE"
echo "Manifest: $REMOTE_EXP_ROOT/phase1_manifest.tsv"
echo "PID file: $REMOTE_EXP_ROOT/phase1_batch_$BATCH_TS.pid"
echo "Batch log: $REMOTE_EXP_ROOT/phase1_batch_$BATCH_TS.log"
