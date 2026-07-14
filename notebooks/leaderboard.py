# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pandas",
#     "altair",
#     "pyarrow",
# ]
# ///

import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md("""
    # Parameter Golf — Run Leaderboard

    Scans `../runs/**/result.json` (synced back from training VMs) and renders the leaderboard. Code lives in `pggolf-experiments/`; this notebook only reads local result artifacts.

    Run with `uv run marimo edit --sandbox notebooks/leaderboard.py`.
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    return alt, json, mo, pd


@app.cell
def _(json, mo, pd):
    runs_dir = (mo.notebook_dir() / ".." / "runs").resolve()
    results = [
        json.loads(p.read_text()) for p in sorted(runs_dir.glob("**/result.json"))
    ]
    df = pd.DataFrame(results)
    mo.md(f"Found **{len(df)}** runs under `{runs_dir}`.")
    return (df,)


@app.cell
def _(df, mo):
    columns = [
        "experiment",
        "parent",
        "change",
        "quant_val_bpb",
        "float_val_bpb",
        "steps",
        "step_avg_ms",
        "model_params",
        "date",
    ]
    leaderboard = (
        df[[c for c in columns if c in df.columns]]
        .sort_values("quant_val_bpb")
        .reset_index(drop=True)
    )
    mo.ui.table(leaderboard, selection=None)
    return (leaderboard,)


@app.cell
def _(alt, leaderboard, mo):
    chart = (
        alt.Chart(leaderboard)
        .mark_bar()
        .encode(
            x=alt.X("quant_val_bpb:Q", title="quantized val bpb (lower = better)"),
            y=alt.Y("experiment:N", sort="x"),
            tooltip=["experiment", "change", "quant_val_bpb", "float_val_bpb"],
        )
        .properties(height=220)
    )
    mo.ui.altair_chart(chart)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Extending

    - New runs appear automatically once their `result.json` lands in `runs/`.
    - Export a figure for the entry note with the chart's save menu into `../artifacts/`, then embed it in `../README.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
