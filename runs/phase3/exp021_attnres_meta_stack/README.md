# exp021_attnres_meta_stack

Longer-step residual-routing experiment built from the `exp017` meta-stack base.

## What Changes

- Keeps the same strong conventional stack:
  - `11L / 512d / 8H / 4KV`
  - `3x relu^2` MLP
  - `BigramHash`
  - causal `SmearGate`
  - Muon + `WEIGHT_DECAY=0.04`
- Adds a lightweight `AttnRes` module:
  - low-dimensional residual-state attention
  - learned routing over prior layer outputs
  - zero-init residual scale so the run starts near the vanilla stack

## Why This Exists

AttnRes is one of our cheapest architecture bets. It aims to improve depth-wise information routing and gradient flow without a meaningful parameter-budget hit.

## Key Knobs

- `ATTNRES_ENABLED=1`
- `ATTNRES_DIM=8`
- `ROPE_DIM=16`
- `NUM_KV_HEADS=4`
- `MAX_WALLCLOCK_SECONDS=1800`
- `VAL_LOSS_EVERY=1200`

## First Intended Run

```bash
ATTNRES_ENABLED=1 \
ATTNRES_DIM=8 \
ROPE_DIM=16 \
VAL_LOSS_EVERY=1200 \
MAX_WALLCLOCK_SECONDS=1800 \
torchrun --standalone --master-port 29629 --nproc_per_node=8 train.py
```

## Interpretation

- If this helps, AttnRes becomes the main architecture-differentiation lane after the conventional stack.
- If it does not, we can likely stop spending time on residual-routing tricks on A40.

