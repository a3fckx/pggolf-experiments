#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-mi300x}
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
VAULT_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd)
LOCAL_MANIFEST="$VAULT_ROOT/experiments/phase1_clean_remaining_manifest.tsv"
LOCAL_RUNNER="$VAULT_ROOT/experiments/vm_run_manifest.sh"
REMOTE_EXP_ROOT="~/experiments"
REMOTE_MANIFEST="$REMOTE_EXP_ROOT/phase1_clean_remaining_manifest.tsv"
REMOTE_RUNNER="$REMOTE_EXP_ROOT/vm_run_manifest.sh"
QUEUE_TS=$(date +%Y%m%dT%H%M%S)
WAIT_ON="pgolf_phase1_exp001_11L_3xMLP_clean"
REMOTE_LOG="$REMOTE_EXP_ROOT/phase1_clean_remaining_$QUEUE_TS.log"
REMOTE_PID="$REMOTE_EXP_ROOT/phase1_clean_remaining_$QUEUE_TS.pid"

scp "$LOCAL_MANIFEST" "$REMOTE:$REMOTE_MANIFEST"
scp "$LOCAL_RUNNER" "$REMOTE:$REMOTE_RUNNER"

ssh "$REMOTE" "chmod +x $REMOTE_RUNNER && nohup bash -lc 'while docker ps --format \"{{.Names}}\" | grep -q \"^$WAIT_ON\$\"; do sleep 30; done; bash $REMOTE_RUNNER $REMOTE_MANIFEST > $REMOTE_LOG 2>&1' >/dev/null 2>&1 & echo \$! > $REMOTE_PID"

echo "Queued clean Phase 1 continuation on $REMOTE"
echo "Waiting on: $WAIT_ON"
echo "Manifest: $REMOTE_MANIFEST"
echo "PID file: $REMOTE_PID"
echo "Log: $REMOTE_LOG"
