---
tags:
  - experiment-log
date: 2026-03-21
---

# Baseline Mirror

This folder is the local vault mirror of the first successful MI300X baseline run.

## Files

- `log.txt` is the completed baseline log captured from the live `~/parameter-golf` run on the VM.
- `current_log_snapshot.txt` is the synchronized `~/experiments/baseline/current_log_snapshot.txt` helper copy from the VM.
- `train_gpt_snapshot.py` is the baseline training script snapshot used for the run.
- `result.json` is the normalized local summary for agents and humans.

## Baseline Result

- Float `val_bpb`: `1.9603`
- Quantized roundtrip `val_bpb`: `2.06682711`
- Steps reached before wallclock cap: `251`
- Average step time: `2397.06 ms`
- Validation tokens scanned: `62,021,632`

## Notes

- The training loop stopped at the built-in `600s` wallclock cap.
- The full process kept running after that because validation and final int8+zlib roundtrip evaluation still execute after training stops.
- The plot mirror for this run lives at `../plots-vm/training_curves.png`.

## See also

- [[leaderboard]]
- [[insights]]
- [[program|program.md]]
