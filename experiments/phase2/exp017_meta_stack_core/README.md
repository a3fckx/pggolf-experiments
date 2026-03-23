# exp017_meta_stack_core

Canonical reproduction-oriented harness for the current Parameter Golf meta stack.

## Defaults

- `11` layers
- `512` model dim
- `8` heads / `4` KV heads
- `3x` `relu^2` MLP
- `SmearGate` enabled
- `BigramHash(4096, 128)` enabled
- Muon defaults shifted toward the stronger public stack:
  - `MATRIX_LR=0.02`
  - `SCALAR_LR=0.02`
  - `MUON_MOMENTUM=0.99`
  - `MUON_MOMENTUM_WARMUP_START=0.92`
  - `MUON_MOMENTUM_WARMUP_STEPS=1500`
  - `WEIGHT_DECAY=0.04`

## Optional Feature Flags

- `XSA_LAYERS=4` enables XSA on the last 4 layers
- `ROPE_DIM=16` enables Partial RoPE with 16 rotated dims
- `LN_SCALE_ENABLED=1` enables depth-scaled normalized inputs
- `NTK_ROPE_ENABLED=1` enables NTK-aware RoPE base scaling for longer-than-train contexts
- `ORTHO_INIT_ENABLED=1` enables orthogonal init for non-zero-init linear weights
- `SWA_ENABLED=1` enables late stochastic weight averaging
- `LATE_QAT_ENABLED=1` enables end-of-run fake quantization-aware training
- `BIGRAM_VOCAB_SIZE=0` disables BigramHash
- `SMEARGATE_ENABLED=0` disables SmearGate

## Still Separate Experiments

- TTT
- JEPA / AttnRes

## One-by-One Run Order

This is the original exp017 ablation order, kept here as harness history. The current live A40 queue moved on to `exp018_ntk_sliding_eval_gqa` and `exp017_partial_rope_ortho`.

1. Core stack only
2. `+ Late QAT`
3. `+ Partial RoPE`
4. `+ LN Scale`
5. `+ Partial RoPE + KV8`
6. `+ Partial RoPE + KV8 + NTK-RoPE`
7. Re-stack `Late QAT` on the best architecture winner
8. Then return to `XSA4`, `SWA`, and `OrthoInit`

Current live interpretation: `SWA` already finished at `1.37406320`, `KV8` lost to the simpler Partial-RoPE family, the old fixed-length NTK run was only a sanity check, and the real NTK test now lives in [exp018_ntk_sliding_eval_gqa](../exp018_ntk_sliding_eval_gqa/README.md).

Use the same hardware, seed, wallclock, and launch shape for every run.

## Live Run Snapshot

- Date: `2026-03-22`
- Hardware: `RunPod 8xA40`
- Stable mirrored harness: [train.py](train.py)
- Active pod runner: `train_next_feature_hooks.py`
- Active log path: `/workspace/fair_runs/exp018_ntk_sliding_eval_gqa/full_log_exp018_ntk_sliding_eval_gqa.txt`
- Selected live snapshots are tracked outside this repo in the results layer.
- Working launch recipe: [runpod_8gpu_a40.sh](runpod_8gpu_a40.sh)
- Important A40 caveat: 8-GPU DDP on the current pod hung on the first collective until `NCCL_IB_DISABLE=1` and `NCCL_P2P_DISABLE=1` were both set
- Status at save time: `exp018_ntk_sliding_eval_gqa` is the active run; `exp017_partial_rope_swa` finished at `1.37406320`; `exp017_partial_rope_ortho` is queued next
- Most recent completed A40 follow-ups: `exp017_partial_rope_swa` finished at `1.37406320` int8+zlib, `exp017_partial_rope_kv8` finished at `1.37748001`, `exp017_partial_rope_ntk_gqa` finished at `1.37173728`, and `exp017_partial_rope_kv8_ntk` was interrupted by `SIGTERM` at `step 300`
