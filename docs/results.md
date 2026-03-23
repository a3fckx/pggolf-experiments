# Results

Public snapshot of the strongest results recorded so far across the current Parameter Golf experiment lanes.

## Leaderboard Snapshot

| Rank | Experiment | val_bpb | quant_bpb | Steps | Machine | Change | Date |
|------|------------|---------|-----------|-------|---------|--------|------|
| 1 | `baseline_8xA40` | 1.2709 | 1.2731 | 2940 | 8xA40 | Unmodified baseline, 8-GPU DDP, 204 ms/step | 2026-03-21 |
| 2 | `baseline_compiled` | 1.3971 | 1.4005 | 816 | 1xMI300X | ROCm 7.2 / PyTorch 2.10 container baseline | 2026-03-21 |
| 2 | `exp004_partial_rope_clean` | 1.4000 | 1.4032 | 821 | 1xMI300X | Partial RoPE 16/64, exclusive GPU | 2026-03-21 |
| 3 | `exp001_11L_3xMLP_clean` | 1.4247 | 1.4311 | 606 | 1xMI300X | 11L + 3xMLP, exclusive GPU | 2026-03-21 |
| 4 | `exp003_ema_clean` | 1.4870 | 1.4905 | 815 | 1xMI300X | EMA(0.997), exclusive GPU | 2026-03-21 |
| 5 | `exp002_xsa4` | 1.5011 | 1.5135 | 481 | 1xMI300X | XSA4, confounded by a slow manual attention path | 2026-03-21 |

## Notes

- Lower `val_bpb` is better.
- MI300X runs were mostly short directional checks and promotion passes.
- The cleanest serious baseline recorded here is the `8xA40` DDP run.
- The strongest clean MI300X variant so far is `exp004_partial_rope_clean`.

## Current Direction

- Carry `Partial RoPE` forward as the default architecture win.
- Treat larger `786432` token batch sizes as a systems dead end on A40.
- Keep stacking features one at a time on the strongest current harness.
