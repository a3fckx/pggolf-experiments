---
tags:
  - full-note
date: 2026-03-22
---

# Experiment Entry Points

This note separates the harnesses we can actually run today from the labels that still describe planned or partially merged ideas.

## Working Harnesses

- `exp017_meta_stack_core` on RunPod is the current live 8-GPU harness.
- The stable control file mirrored locally is [train.py](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/train.py).
- The live feature-hooks runner on the pod is `train_next_feature_hooks.py`, which adds `NTK_ROPE_ENABLED`, `ORTHO_INIT_ENABLED`, `LATE_QAT_ENABLED`, and `SWA_ENABLED`.
- The working launch recipe is [runpod_8gpu_a40.sh](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/runpod_8gpu_a40.sh).
- The live log is [full_log_runpod_live_20260322.txt](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/full_log_runpod_live_20260322.txt).
- The repo-native orchestration layer is `run_all.sh`, the per-experiment `exp0*/run.sh` scripts, and `run_fastest_path.sh`.
- The plain-English architecture map is [[Feature Stack Guide]].
- The live A40 run on the pod is currently `exp018_ntk_sliding_eval_gqa`; the earlier `exp017_partial_rope_kv8 -> exp017_partial_rope_kv8_ntk` queue is now only historical context.
- The current high-confidence A40 default is `TRAIN_BATCH_TOKENS=524288`; the `786432` batch run was kept as a systems ablation and lost badly on quality.

## Planned Or Labels

- `exp03_11L_xsa4` is a label for XSA, but the repo script still says the feature is not implemented in `train_gpt_sota.py`.
- `exp04_11L_partial_rope_ln_scale` is a label for Partial RoPE plus LN Scale, but the repo script still marks both as not implemented in `train_gpt_sota.py`.
- `exp05_11L_grad_guided_quant` is a label for gradient-guided quantization, but the repo script still describes it as a proxy rather than the real adaptive method.
- `exp017_meta_stack_core` is the current clean harness for one-by-one ablations.
- The current A40 sequence already observed on the pod is `Partial RoPE -> KV8 -> interrupted KV8+NTK -> Partial RoPE + NTK (4KV) -> Partial RoPE + SWA -> NTK sliding eval`, with `exp017_partial_rope_ortho` queued next.

## Connections

- [[Parameter Golf Experiments]]
- [[Parameter Golf Experiment Framework]]
- [[Parameter Golf Goal Definition]]
