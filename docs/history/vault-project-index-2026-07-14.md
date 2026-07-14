---
tags:
  - experiment-log
  - project-space
status: active
repo: pggolf-experiments
date: 2026-07-14
---

# Parameter Golf Experiments

This folder is the local vault mirror for the experiment story. The live training work runs on RunPod; this folder keeps the human-readable map of what is active, what is implemented, and what is still planned.

Canonical experiment code lives in [pggolf-experiments](/Users/a3fckx/Desktop/Attri/pggolf-experiments). This vault folder should stay focused on human-readable summaries, coordination notes, and lightweight result artifacts only.

> **Vault boundary (2026-07-14):** `.pt`/`.ptz` model weights, `.venv/`, and `__pycache__/` have been removed from this folder. Binary artifacts and runnable code belong in sibling project repos under `Attri/`, not in the vault.

## Start Here

- Current live RunPod run: [exp017_meta_stack_core README](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/README.md)
- Stable control harness mirrored locally: [exp017_meta_stack_core/train.py](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/train.py)
- Live feature-hooks harness on the pod: `train_next_feature_hooks.py` (`NTK_ROPE_ENABLED`, `ORTHO_INIT_ENABLED`, `LATE_QAT_ENABLED`, `SWA_ENABLED`)
- Working launch recipe: [runpod_8gpu_a40.sh](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/runpod_8gpu_a40.sh)
- Live log snapshot: [full_log_runpod_live_20260322.txt](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/phase2/exp017_meta_stack_core/full_log_runpod_live_20260322.txt)
- Run-entry map: [[Experiment Entry Points]]
- Feature explainer: [[Feature Stack Guide]]
- Method summary: [[How We Conducted Parameter Golf Experiments]]
- Active A40 live run: `exp018_ntk_sliding_eval_gqa` on `Partial RoPE` (`ROPE_DIM=16`) with `NTK_ROPE_ENABLED=1`, `EVAL_SEQ_LEN=2048`, and `EVAL_STRIDE=64`
- Queued A40 follow-up: `exp017_partial_rope_ortho` on the same `Partial RoPE` base with `ORTHO_INIT_ENABLED=1`
- Most recent completed A40 follow-ups: `exp017_partial_rope_swa` finished at `1.37406320` int8+zlib, `exp017_partial_rope_kv8` finished at `1.37748001` int8+zlib, `exp017_partial_rope_ntk_gqa` finished at `1.37173728`, and `exp017_partial_rope_kv8_ntk` was interrupted by `SIGTERM` at `step 300`
- Current systems finding: `TRAIN_BATCH_TOKENS=786432` was worse than `524288` on A40 and is now deprioritized

## What Lives Here

This is a project space (see `experiments/AGENTS.md` for the contract):

- `README.md` (this note) plus `leaderboard.md`, `insights.md`, `task-board.md`, and `program.md` are the living coordination layer.
- `notebooks/` holds literate marimo notebooks — start with `notebooks/leaderboard.py`, which scans `runs/**/result.json` and renders the leaderboard.
- `runs/` holds synced result artifacts: `baseline/`, `exp001`–`exp008`, `phase1/`–`phase3/`, `batch-logs/`, and `parameter-golf-logs/`.
- `artifacts/` holds curated exports (e.g. `plots-vm/`) for embedding in notes.
- `notes/` holds stable narrative docs: [[Experiment Entry Points]], [[Feature Stack Guide]], [[How We Conducted Parameter Golf Experiments]], [[Iteration Budget]], [[Runpod Next Program]], [[Archive Plan]], and the consolidation history.
- `ops/` holds operational state and `legacy-scripts/` (vault copies that drifted from the repo before dedup).
- Experiment code is canonical in [pggolf-experiments/experiments](/Users/a3fckx/Desktop/Attri/pggolf-experiments/experiments) — never edit training code here.

## How To Read It

- If a folder contains a synced run, that run already happened and the vault has a local artifact.
- If a note says `planned`, it is a label or idea, not necessarily a merged harness.
- If a note says `working`, it is the current executable path we should trust first.
- The A40 lane has moved beyond the earlier `KV8 -> KV8+NTK` note. The pod already finished `KV8`, lost a clean `KV8+NTK` ranking to an interrupted run, finished a strong `Partial RoPE + NTK` run on the 4-KV base, finished `Partial RoPE + SWA` at `1.37406320`, and is now actively testing real sliding-eval NTK in `exp018_ntk_sliding_eval_gqa`.

## See Also

- [[Parameter Golf Experiment Framework]]
- [[program|program.md]]
- [[AGENT_COORDINATION|AGENT_COORDINATION.md]]
