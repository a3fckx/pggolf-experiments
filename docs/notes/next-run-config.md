---
tags:
  - experiment-config
  - wip
date: 2026-03-22
---

# Next Run Config: Research Lane After Ortho

Keep the A40 loop architecture-first. Batch stays at 524K because the 786K ablation lost badly. `exp018_ntk_sliding_eval_gqa` has now finished badly, `exp017_partial_rope_ortho` is the last active cheap flag run, and the pod is queued to move into longer-step `JEPA` and `AttnRes` experiments after that.

Update on `2026-03-22`: `exp017_partial_rope_kv8` finished at `1.37748001`, the first `exp017_partial_rope_kv8_ntk` attempt was interrupted at `step 300`, `exp017_partial_rope_ntk_gqa` finished at `1.37173728`, `exp017_partial_rope_swa` finished at `1.37406320`, and `exp018_ntk_sliding_eval_gqa` finished very badly at `2.01194449`.

## Rationale

After the completed A40 ablations, we know:
- Step count is king at ~1,074 steps (deeply underfitting regime)
- Bigger batch (786K) costs 46% more per step for only 3% more tokens — net loss
- Partial RoPE and Late QAT are the only clear wins on this harness
- LN Scale hurts (regularizer on underfitting model)
- KV8 lost to the simpler 4-KV Partial-RoPE family
- the A40 sliding-eval NTK experiment was a real fairness check, and it still lost badly
- JEPA / AttnRes deserve longer promotion-style runs more than more tiny flag ablations do

## Current Queue

| Run | Key settings | Why |
|-----|--------------|-----|
| `exp017_partial_rope_ortho` | `ROPE_DIM=16`, `ORTHO_INIT_ENABLED=1` | Last cheap initializer check on the strong Partial-RoPE stack |
| `exp020_span_jepa_meta_stack` | `ROPE_DIM=16`, `JEPA_LAMBDA=0.01`, `JEPA_SPAN_LEN=8`, `MAX_WALLCLOCK_SECONDS=1800` | First longer-step latent-learning check |
| `exp021_attnres_meta_stack` | `ROPE_DIM=16`, `ATTNRES_ENABLED=1`, `ATTNRES_DIM=8`, `MAX_WALLCLOCK_SECONDS=1800` | First longer-step residual-routing check |

## What We Expect

- `OrthoInit` is a hygiene check, not a likely leaderboard move.
- `Span-JEPA` and `AttnRes` are the real research bets and need more steps than the 600s flag lane.
- Both longer-step runs are intentionally based on the simple `Partial RoPE` stack, not on the losing `KV8` / `LN Scale` / `NTK` branches.

## Automated Flow

```bash
1. finish exp017_partial_rope_ortho
2. run exp020_span_jepa_meta_stack (1800s)
3. run exp021_attnres_meta_stack (1800s)
4. sync logs back locally
5. stop pod ukp4lcxzv2ukc3
```

## What To Watch

1. **Ortho result** — does it beat plain `Partial RoPE` at all?
2. **JEPA train_aux_loss** — does the auxiliary signal stay active without destabilizing CE?
3. **AttnRes step time** — does residual routing stay cheap enough on A40 to be worth it?
4. **Final int8+zlib BPB** — this still decides whether the research lane earned more time.

## Ablation Results That Informed This Config

| Feature | Steps | ms/step | INT8+zlib BPB | Verdict |
|---------|-------|---------|---------------|---------|
| Causal fix (baseline) | 1,074 | 559 | 1.3786 | KEEP (prerequisite) |
| + Late QAT | 1,074 | 559 | **1.3711** | modest real win |
| + Partial RoPE | 1,094 | 549 | **1.3711** | best simple architecture win |
| + SWA | 1,081 | 555 | 1.3741 | close but behind |
| + LN Scale | 1,066 | 563 | 1.3916 | bad |
| + Batch 786K | 736 | 815 | 1.4877 | bad |
| + KV8 | 1,044 | 575 | 1.3775 | bad |
| + NTK sliding eval | 800 train steps + final sliding eval | 550 | 2.0119 | bad on A40 |

## Later Stack (after this loop)

- If one research run is promising, do exactly one follow-up rerun before shutting down and regrouping

See also: [[Parameter Golf]], [[Parameter Golf Experiment Framework]]
