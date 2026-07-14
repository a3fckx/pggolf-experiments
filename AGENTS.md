# pggolf-experiments

Canonical code for OpenAI Parameter Golf: training harnesses, phase snapshots,
launch/sync scripts, analysis notebooks, and imported run history.

## Layout

- `experiments/` — training harness and per-experiment snapshots (edit code here)
- `notebooks/` — marimo analysis notebooks (`leaderboard.py`, `technique-explorer.py`)
- `docs/` — results, insights, and narrative imported from the vault

## Rules

- Runs execute remotely (RunPod / MI300X); results sync back as `result.json`,
  logs, and plots.
- Durable findings are distilled into the vault (`a3fckx/5 - Projects/Parameter
  Golf.md` and full notes) with links back to exact paths here.
- The vault holds no code; this repo holds no living narrative that belongs in
  the vault.
