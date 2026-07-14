---
tags:
  - experiment-log
date: 2026-03-22
---

# Archive Plan

This note records the non-destructive cleanup plan for the `experiments/` folder.

## Keep As First-Class

- `README.md`
- `Experiment Entry Points.md`
- `AGENT_COORDINATION.md`
- `task-board.md`
- `program.md`
- `insights.md`
- `baseline/`
- `phase2/exp017_meta_stack_core/`

## Historical Or Noisy

- Top-level scratch experiment folders like `exp001_11L_3xMLP/` through `exp008_late_qat/`
- `parameter-golf-logs/`
- `smoke_xsa4_runner/`
- `phase1_*.log`, `phase1_*.tsv`, `current_run.txt`, `alerts.txt`
- One-off helper scripts that are no longer the active launch path

## Why Not Move Yet

- Several notes still mention the older paths by name.
- The live RunPod run is still active, so the safest move is to keep the structure readable first and only physically relocate files after the references are updated.
- The new entry-point map already gives us the clean separation between working harnesses and planned labels.

## Next Safe Step

Create an `archive/` bucket for the noisy historical material and move only files that do not appear in any active note links. Leave the current RunPod harness and its log snapshot where they are.

## See also

- [[Parameter Golf Experiments]]
- [[Experiment Entry Points]]
- [[AGENT_COORDINATION]]
