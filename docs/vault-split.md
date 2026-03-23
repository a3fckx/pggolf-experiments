# Vault Split

This documents the new split between the experiment code repo and the Obsidian vault.

## Repo Canonical

These should be edited in `pggolf-experiments/` going forward:

- `train.py` snapshots
- `train_gpt.py`
- launch and sync shell scripts
- `config.json`
- `env_overrides.txt`
- manifest files such as `*.tsv`
- run-specific `README.md` files that describe how a harness is supposed to be launched

## Vault Canonical

These should stay in `a3fckx/experiments/`:

- `leaderboard.md`
- `insights.md`
- `task-board.md`
- `AGENT_COORDINATION.md`
- `program.md`
- logs such as `full_log*.txt`
- outputs such as `result.json`
- checkpoints such as `final_model.pt` and `final_model.int8.ptz`
- synced plots and screenshots
- historical run folders used for narrative or result tracking

## Migration Rule

For new work:

1. create or edit the experiment code in `pggolf-experiments/experiments/`
2. run the experiment from the remote execution environment
3. sync the resulting artifacts back into the vault
4. update vault notes with findings

## Current State

This migration copied the reproducible code surface into `pggolf-experiments/experiments/` and intentionally left the vault untouched.

That means some code still exists in both places right now. Until we do a second cleanup pass, treat the repo as the place to make new code changes and the vault as the place to read results.
