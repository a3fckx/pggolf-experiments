# exp020_span_jepa_meta_stack

Longer-step research variant built from the `exp017` meta-stack base.

## What Changes

- Keeps the strong conventional stack:
  - `11L / 512d / 8H / 4KV`
  - `3x relu^2` MLP
  - `BigramHash`
  - causal `SmearGate`
  - Muon + `WEIGHT_DECAY=0.04`
- Adds a training-only `Span-JEPA` auxiliary loss.
- The JEPA predictor is intentionally excluded from the exported submission artifact.

## Why This Exists

Short A40 runs are good for architectural filtering, but latent-learning ideas are more likely to pay off with more steps. This experiment is the first honest longer-step check for whether representation prediction helps BPB without changing inference-time architecture.

## Key Knobs

- `JEPA_LAMBDA=0.01`
- `JEPA_SPAN_LEN=8`
- `ROPE_DIM=16`
- `NUM_KV_HEADS=4`
- `MAX_WALLCLOCK_SECONDS=1800`
- `VAL_LOSS_EVERY=1200`

## First Intended Run

```bash
ROPE_DIM=16 \
JEPA_LAMBDA=0.01 \
JEPA_SPAN_LEN=8 \
VAL_LOSS_EVERY=1200 \
MAX_WALLCLOCK_SECONDS=1800 \
torchrun --standalone --master-port 29628 --nproc_per_node=8 train.py
```

## Interpretation

- If this beats the best conventional `Partial RoPE` anchor after a longer run, JEPA becomes the primary research lane.
- If it is flat or worse, we treat JEPA as an interesting but unproven idea at this scale.

