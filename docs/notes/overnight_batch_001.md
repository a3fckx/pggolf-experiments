---
tags:
  - experiment-log
date: 2026-03-21
---

# Overnight Batch 001 — Phase 1 Understanding + Phase 3 Novel Ideas

## Execution Plan

Sequential experiments on MI300X (1 at a time, exclusive GPU).
Using Docker `pgolf-ready:latest` or `rocm/pytorch:rocm7.2_ubuntu22.04_py3.11_pytorch_release_2.10.0`.
Each Phase 1 experiment: 600s wallclock (~13 min total with val).
Each Phase 3 experiment: 2400s wallclock (~45 min total with val — grokking risk).

## Phase 1: Understanding Experiments (600s each)

### Depth Sweep
| # | Name | Config | Budget | What We Learn |
|---|------|--------|--------|---------------|
| 1 | depth_9L_3x | NUM_LAYERS=9 MLP_MULT=3 | ~21M / ~9.2MB | Fewer layers, wide MLP |
| 2 | depth_11L_3x | NUM_LAYERS=11 MLP_MULT=3 | ~26.5M / ~11.6MB | Meta stack (reference) |
| 3 | depth_13L_3x | NUM_LAYERS=13 MLP_MULT=3 | ~32M / ~14MB | Deeper, near budget limit |

### Width Sweep
| # | Name | Config | Budget | What We Learn |
|---|------|--------|--------|---------------|
| 4 | width_11L_2x | NUM_LAYERS=11 MLP_MULT=2 | ~22M / ~9.6MB | Narrow MLP |
| 5 | width_11L_4x | NUM_LAYERS=11 MLP_MULT=4 | ~31M / ~13.5MB | Very wide MLP |

### Vocab Sweep
| # | Name | Config | Budget | What We Learn |
|---|------|--------|--------|---------------|
| 6 | vocab_2048 | VOCAB_SIZE=2048 | +0.3MB | Bigger vocabulary |
| 7 | vocab_4096 | VOCAB_SIZE=4096 | +0.9MB | Even bigger vocabulary |

Total Phase 1: 7 experiments x ~13 min = ~1.5 hours

## Phase 3: Novel Ideas (2400s each)

| # | Name | Config | What We Learn |
|---|------|--------|---------------|
| 8 | stp_lite_001 | STP_LAMBDA=0.01 MAX_WALLCLOCK_SECONDS=2400 | Does trajectory smoothness help BPB? |
| 9 | span_jepa_001 | JEPA_LAMBDA=0.01 MAX_WALLCLOCK_SECONDS=2400 | Does span embedding prediction help BPB? |
| 10 | cross_layer_jepa_001 | JEPA_LAMBDA=0.01 MAX_WALLCLOCK_SECONDS=2400 | Does depth prediction help BPB? |

Total Phase 3: 3 experiments x ~50 min = ~2.5 hours

## Total Overnight Time
~4 hours for all 10 experiments. Can start at midnight, results by 4am.

## Expected Outputs
Each experiment produces:
- `~/experiments/<phase>/<name>/full_log.txt` — complete training log
- `~/experiments/<phase>/<name>/result.json` — val_bpb, params, steps
- `~/experiments/<phase>/<name>/train.py` — exact code snapshot

## Success Criteria
- Phase 1: identify optimal depth, width, vocab for our budget
- Phase 3: at least ONE novel technique improves val_bpb over baseline
- If STP or JEPA helps: we have a differentiated submission nobody else has

## See also
- [[Parameter Golf Goal Definition]]
- [[Parameter Golf Budget Game]]
- [[Grokking and Parameter Golf]]
- [[Parameter Golf Experiment Framework]]
