---
tags:
  - experiment-log
date: 2026-03-21
---

# Phase 1

This folder will hold synced artifacts for the first reproduction passes on the proven meta stack.

Current status: this folder tracks the early reproduction passes on the MI300X lane. Promoted artifacts can be pulled in with [sync-vm-phase1-artifacts.sh](../sync-vm-phase1-artifacts.sh) after runs finish.

Expected early experiments:

- `exp001_11L_3xMLP_clean`
- `exp002_xsa4_clean`
- `exp003_ema_clean`
- `exp004_partial_rope_clean`
- `exp005_ln_scale_clean`
- `exp006_smeargate_clean`
- `exp007_bigramhash_clean`
- `exp008_late_qat_clean`

Important note: `exp002_xsa4` is now a historical slow-path result. The clean rerun uses shifted SDPA for the exclude-self attention path so it stays on the ROCm fast path.

See the repo-level docs and the external coordination layer for the live queue.
