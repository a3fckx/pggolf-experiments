# pggolf-experiments

Canonical project for Parameter Golf experiment code, notebooks, execution history, and artifacts.

## Layout

- `experiments/` — editable harnesses, snapshots, configs, and launch scripts
- `notebooks/` — Marimo leaderboard and technique explorer
- `runs/` — imported and future execution records
- `artifacts/` — plots and other generated outputs
- `ops/` — operational state and legacy helper scripts
- `docs/` — program, task history, results, insights, and methodology

## Workflow

1. Edit the experiment in `experiments/`.
2. Run it locally or on the selected remote runner.
3. Sync the result into `runs/` and generated output into `artifacts/`.
4. Inspect results through `notebooks/leaderboard.py`.
5. Update the project docs and promote only durable conclusions into the Obsidian vault.

The vault project page is `/Users/a3fckx/Desktop/Attri/a3fckx/5 - Projects/Parameter Golf.md`. It stores context and decisions, not runtime material.

## Marimo

```sh
uv run marimo edit --sandbox notebooks/leaderboard.py
uv run marimo edit --sandbox notebooks/technique-explorer.py
```

## Docs

- [Results](docs/results.md)
- [Insights](docs/insights.md)
- [Program](docs/program.md)
- [Task history](docs/task-board.md)
- [Vault boundary](docs/vault-split.md)
- [Imported vault insights](docs/insights-vault-2026-07-14.md)
- [Imported vault leaderboard](docs/leaderboard-vault-2026-07-14.md)
