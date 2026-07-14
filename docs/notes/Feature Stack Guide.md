---
tags:
  - full-note
date: 2026-03-22
---

# Feature Stack Guide

This note explains the current Parameter Golf stack in plain English: what the base model is, where each feature acts, and which local experiment files actually implement each idea.

## Mental Model

Think of the stack in layers:

```text
tokens
  |
  v
[token embedding] + [optional BigramHash]
  |
  v
[RMSNorm]
  |
  v
[optional SmearGate]
  |
  v
[11-layer GPT stack]
    |- attention path
    |    |- RoPE / Partial RoPE / NTK-RoPE
    |    |- optional XSA in late layers
    |
    |- residual path
    |    |- optional LN Scale
    |    |- future AttnRes candidate
    |
    |- MLP path
  |
  v
[final norm + tied lm head]
  |
  v
next-token loss
  |
  +--> optional training tricks: OrthoInit, SWA, Late QAT
  +--> optional research losses: JEPA / STP-lite
  +--> optional eval-time adaptation: TTT
```

## What Each Feature Does

| Feature | What it changes | Which part it affects | Why try it |
| --- | --- | --- | --- |
| `11L + 3x MLP` | More layers and larger feed-forward blocks | Model capacity | Better small-model expressivity |
| `BigramHash` | Adds a hashed previous-token/current-token embedding | Input representation | Cheap local pattern knowledge |
| `SmearGate` | Mixes each token with immediate left context | Input / early context shaping | Cheap local smoothing before attention |
| `Partial RoPE` | Rotates only some head dimensions | Attention representation | Leaves more dimensions content-focused |
| `NTK-RoPE` | Scales RoPE base for longer contexts | Attention over long contexts | Better length extrapolation |
| `XSA` | Removes self-attention in selected late layers | Attention mask / inductive bias | Force context use over identity copying |
| `LN Scale` | Scales normalized activations by depth | Residual / stability | Gentler deeper-layer updates |
| `OrthoInit` | Orthogonal init for linear weights | Initialization | Better early signal propagation |
| `SWA` | Averages late checkpoints | Optimization / final weights | Flatter, often more robust minima |
| `Late QAT` | Fake-quantizes linear weights near the end | Training-to-export bridge | Reduce float-to-quantized drop |
| `JEPA` | Adds hidden-state prediction loss | Training objective | Learn richer latent structure |
| `AttnRes` | Changes attention/residual interaction | Core architecture | Better residual routing |
| `TTT` | Adapts weights during evaluation | Eval-time procedure | Squeeze more performance at test time |

## Where Features Sit

```text
Initialization
  - OrthoInit

Input stack
  - BigramHash
  - SmearGate

Attention stack
  - Partial RoPE
  - NTK-RoPE
  - XSA

Residual / stability
  - LN Scale
  - AttnRes

Training / optimization
  - SWA
  - JEPA
  - STP-lite

Export / compression
  - Late QAT

Evaluation only
  - TTT
```

## Which Local Model Uses What

| Experiment | Uses |
| --- | --- |
| `baseline/train_gpt_snapshot.py` | Baseline `9L / 512d / 2x MLP`, full RoPE, no stack extras |
| `phase1/exp001_11L_3xMLP_clean` | `11L + 3x MLP` |
| `phase1/exp002_xsa4_clean` | `XSA4` |
| `phase1/exp003_ema_clean` | `EMA` training-time averaging, not a core architecture change |
| `phase1/exp004_partial_rope_clean` | `Partial RoPE` |
| `phase1/exp005_ln_scale_clean` | `LN Scale` |
| `phase1/exp006_smeargate_clean` | `SmearGate` |
| `phase1/exp007_bigramhash_clean` | `BigramHash` |
| `phase1/exp008_late_qat_clean` | `Late QAT` |
| `phase2/exp009_ntk_rope` | `NTK-RoPE` prototype |
| `phase2/exp017_meta_stack_core` | Default: `11L + 3x MLP + BigramHash + SmearGate`; optional flags for `XSA`, `Partial RoPE`, `LN Scale`, `NTK-RoPE`, `OrthoInit`, `SWA`, `Late QAT` |
| `phase3/span_jepa` | `Span-JEPA` auxiliary loss |
| `phase3/cross_layer_jepa` | `Cross-layer JEPA` auxiliary loss |
| `phase3/stp_lite` | `STP-lite` |

## What Is Implemented Vs Planned

Implemented locally as runnable code:
- `11L + 3x MLP`
- `XSA`
- `EMA`
- `Partial RoPE`
- `LN Scale`
- `SmearGate`
- `BigramHash`
- `Late QAT`
- `NTK-RoPE`
- `OrthoInit` in `exp017`
- `SWA` in `exp017`
- `Span-JEPA`
- `Cross-layer JEPA`
- `STP-lite`

Planned or doc-only right now:
- `AttnRes`
- `TTT`
- `JEPA-lite`

## Current Experiment Policy

We are intentionally not stacking everything at once.

The clean run order is:
1. Honest control on `exp017`
2. `+ Partial RoPE`
3. `+ LN Scale`
4. `+ XSA4`
5. `+ NTK-RoPE`
6. `+ SWA`
7. `+ OrthoInit`
8. `+ Late QAT`
9. Combine winners
10. Then test `AttnRes` and `JEPA`

Why this order:
- architecture changes should be measured on a clean common base
- export tricks should be tested when we already know the base is strong
- research bets like `JEPA` and `AttnRes` are easiest to judge after we reproduce the conventional stack

## Current Live Runs

```text
finished control:
  exp017_meta_stack_core
  causal SmearGate fix
  final_int8_zlib_roundtrip_exact val_bpb: 1.37856702

finished follow-ups:
  exp017_late_qat_only
  same exp017 base
  final_int8_zlib_roundtrip_exact val_bpb: 1.37113245

  exp017_partial_rope_only
  same exp017 base + ROPE_DIM=16
  final_int8_zlib_roundtrip_exact val_bpb: 1.37108571

current live lane:
  exp017_partial_rope_swa
  same exp017 base + ROPE_DIM=16 + SWA_ENABLED=1
  active on train_next_feature_hooks.py, latest flushed checkpoint: step 700 train_loss 2.4014 with step 400 val_bpb 1.4985 at ~548-558ms/step

latest completed follow-ups:
  exp017_partial_rope_kv8
  same exp017 base + ROPE_DIM=16 + NUM_KV_HEADS=8
  final_int8_zlib_roundtrip_exact val_bpb: 1.37748001

  exp017_partial_rope_ntk_gqa
  same exp017 base + ROPE_DIM=16 + NTK_ROPE_ENABLED=1 + NTK_SCALE_EXPONENT=0.0625
  final_int8_zlib_roundtrip_exact val_bpb: 1.37173728

interrupted branch:
  exp017_partial_rope_kv8_ntk
  same as kv8 + NTK_ROPE_ENABLED=1
  stopped by SIGTERM at step 300, so do not rank it against the finished runs
```

## Connections

- [[Parameter Golf Experiments]]
- [[Experiment Entry Points]]
- [[AGENT_COORDINATION]]
