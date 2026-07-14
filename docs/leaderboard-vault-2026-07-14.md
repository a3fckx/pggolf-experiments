---
tags:
  - experiment-log
date: 2026-03-21
---

# Parameter Golf Experiment Leaderboard

## Results

| Rank | Experiment | val_bpb | Quant_bpb | Steps | Machine | Change | Date |
|------|-----------|---------|-----------|-------|---------|--------|------|
| **1** | **baseline_8xA40** | **1.2709** | **1.2731** | **2940** | **8xA40 RunPod** | **Unmodified baseline, 8-GPU DDP, 204ms/step** | **2026-03-21** |
| 2 | baseline_compiled | 1.3971 | 1.4005 | 816 | 1xMI300X | Docker PyTorch 2.10+ROCm7.2, exclusive GPU, 736ms/step | 2026-03-21 |
| 2 | exp004_partial_rope_clean | 1.4000 | 1.4032 | 821 | baseline | Partial RoPE 16/64, exclusive GPU, 731.81ms/step | 2026-03-21 |
| 3 | exp001_11L_3xMLP_clean | 1.4247 | 1.4311 | 606 | baseline | 11L+3xMLP, exclusive GPU, 992.47ms/step | 2026-03-21 |
| 4 | exp003_ema_clean | 1.4870 | 1.4905 | 815 | baseline | EMA(0.997), exclusive GPU, 737.3ms/step | 2026-03-21 |
| 5 | exp002_xsa4 | 1.5011 | 1.5135 | 481 | baseline | XSA4 exclusive, but confounded by slow manual attention path | 2026-03-21 |
| - | exp001_11L_3xMLP | 1.5123 | - | 406 | baseline | 11L+3xMLP, 26.5M params, CONTENDED (3x GPU sharing) | 2026-03-21 |
| - | exp004_partial_rope | 1.5973 | 1.5973 | 417 | baseline | Partial RoPE 16/64, CONTENDED (2x GPU sharing) | 2026-03-21 |
| - | exp005_ln_scale | 1.6751 | 1.7163 | 414 | baseline | LN Scale, CONTENDED (2x GPU sharing) | 2026-03-21 |
| - | exp003_ema | 2.2755 | 2.2959 | 416 | baseline | EMA(0.997), CONTENDED (3x GPU sharing) | 2026-03-21 |
| - | baseline_eager | 1.9603 | 2.0668 | 251 | - | Host PyTorch 2.5, eager mode, 3393ms/step | 2026-03-21 |

**NOTE**: The strongest clean Phase 1 result so far is now `exp004_partial_rope_clean`, which nearly matches the baseline while preserving full step throughput. Contended runs are still useful directional signals, but they are best compared within the same concurrency bucket.

## Notes

- Lower val_bpb is better
- Current ranked runs use about `600s` of training time on `1x MI300X`, plus extra validation and serialization time at the end
- Competition target: <1.120 BPB on 8xH100 (10 min)
- MI300X results are directional, not final scores
- Local mirrored artifacts for the completed baseline live in `experiments/baseline/`

## See also

- [[Parameter Golf Experiment Framework]]
- [[Parameter Golf Goal Definition]]
