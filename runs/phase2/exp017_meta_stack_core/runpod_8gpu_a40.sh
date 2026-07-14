#!/bin/bash
set -euo pipefail

cd /workspace/fair_runs/exp017_meta_stack_core

export PYTHONUNBUFFERED=1
export NCCL_IB_DISABLE=1
export NCCL_P2P_DISABLE=1
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1
export TORCH_NCCL_BLOCKING_WAIT=0
export TORCH_NCCL_HEARTBEAT_TIMEOUT_SEC=3600
export NCCL_TIMEOUT=3600000

export DATA_PATH=/workspace/parameter-golf/data/datasets/fineweb10B_sp1024
export TOKENIZER_PATH=/workspace/parameter-golf/data/tokenizers/fineweb_1024_bpe.model
export MAX_WALLCLOCK_SECONDS=600
export TRAIN_LOG_EVERY=100
export VAL_LOSS_EVERY=400
export SEED=1337
export RUN_ID=exp017_meta_stack_core_8gpu

exec torchrun --standalone --master-port 29617 --nproc_per_node=8 train.py 2>&1 | tee full_log.txt
