# pggolf-experiments

Code repo for experiment harnesses, snapshots, and runner scripts.

This repo is the code side of the split:

- code, configs, and launch helpers live here
- results, logs, checkpoints, plots, and coordination notes stay in the vault at `a3fckx/experiments/`

## Layout

- `experiments/train_gpt.py` is the base local harness mirror
- `experiments/phase1/`, `experiments/phase2/`, and `experiments/phase3/` contain experiment snapshots we may edit and launch
- `experiments/*.sh` contains the current helper scripts for launch, sync, and monitoring
- `docs/results.md` tracks the current public-facing leaderboard
- `docs/insights.md` captures the strongest experiment learnings so far

## Workflow

1. Edit experiment code here.
2. Sync or copy the chosen snapshot to the remote machine or runner.
3. Run the experiment remotely.
4. Save logs, metrics, `result.json`, checkpoints, and plots back into `a3fckx/experiments/`.
5. Update vault notes such as `leaderboard.md`, `insights.md`, and `task-board.md`.

## Current Migration State

This first cut is intentionally non-destructive. The vault still contains older code mirrors, but the new intended direction is:

- repo is canonical for experiment code
- vault is canonical for experiment results and narrative context

## Docs

- [Results](docs/results.md)
- [Insights](docs/insights.md)
- [Vault split](docs/vault-split.md)
