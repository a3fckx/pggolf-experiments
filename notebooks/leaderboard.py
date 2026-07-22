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
app = marimo.App(width="medium", app_title="Parameter Golf — Run Leaderboard")


@app.cell
def _(mo):
    mo.md(r"""
    # Parameter Golf — Run Leaderboard

    Every Parameter Golf experiment runs remotely (RunPod / MI300X) and syncs a
    `result.json` back into the repository. This notebook ranks those artifacts by
    **quantized validation bits-per-byte** (lower is better), with float BPB, step
    count, step time, and parameter count alongside.

    Runs differ in step count and wallclock budget — the board is a lineage view, not
    one controlled bake-off. Prefer the sealed `notebooks/public/results.json`
    snapshot for the published site; local checkouts can also scan `../runs/**/result.json`.
    """)
    return


@app.cell
def _():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    return Path, alt, json, mo, pd


@app.cell
def _(Path, json, mo, pd):
    def _load_frame():
        notebook_dir = Path(mo.notebook_dir())
        local_bundled = notebook_dir / "public" / "results.json"
        runs_dir = (notebook_dir / ".." / "runs").resolve()

        # Prefer the sealed public snapshot when present so exports match the
        # committed provenance artifact even if local run trees drift.
        if local_bundled.is_file():
            frame = pd.read_json(local_bundled)
            return frame, "sealed `notebooks/public/results.json`"

        if runs_dir.is_dir():
            results = [
                json.loads(path.read_text())
                for path in sorted(runs_dir.glob("**/result.json"))
            ]
            return pd.DataFrame(results), "local `runs/**/result.json`"

        # WASM / published site: pyodide patches HTTP so pandas can read the URL.
        remote_bundled = mo.notebook_location() / "public" / "results.json"
        frame = pd.read_json(str(remote_bundled))
        return frame, "bundled `public/results.json` (WASM)"

    df, source = _load_frame()
    return df, source


@app.cell
def _(df, mo, pd, source):
    ranked = (
        df[df["quant_val_bpb"].notna()]
        if "quant_val_bpb" in df.columns
        else df.iloc[0:0]
    )
    n_ranked = len(ranked)
    n_incomplete = len(df) - n_ranked
    if n_ranked:
        best = ranked.sort_values("quant_val_bpb").iloc[0]
        steps = best.get("steps")
        steps_bit = (
            f" over {int(steps):,} steps"
            if steps is not None and pd.notna(steps)
            else ""
        )
        best_line = (
            f"**Leader:** `{best['experiment']}` at "
            f"**{float(best['quant_val_bpb']):.4f}** quantized val BPB{steps_bit}."
        )
    else:
        best_line = "_No ranked runs with quantized val BPB in this snapshot._"

    mo.md(
        f"""
    ## Snapshot

    Found **{len(df)}** run record(s) from {source} · **{n_ranked}** ranked ·
    **{n_incomplete}** incomplete / smoke.

    {best_line}
    """
    )
    return


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
    present = [column for column in columns if column in df.columns]
    leaderboard = (
        df.loc[df["quant_val_bpb"].notna(), present]
        .sort_values("quant_val_bpb")
        .reset_index(drop=True)
    )
    leaderboard.insert(0, "rank", range(1, len(leaderboard) + 1))
    mo.vstack(
        [
            mo.md("### Ranked runs (quantized val BPB)"),
            mo.ui.table(leaderboard, selection=None, page_size=20),
        ]
    )
    return (leaderboard,)


@app.cell
def _(alt, leaderboard, mo):
    if leaderboard.empty:
        chart = mo.md("_Nothing to chart — no ranked runs._")
    else:
        plot_df = leaderboard.copy()
        plot_df["label"] = plot_df["experiment"]
        chart = mo.ui.altair_chart(
            alt.Chart(plot_df)
            .mark_bar()
            .encode(
                x=alt.X(
                    "quant_val_bpb:Q",
                    title="quantized val BPB (lower = better)",
                ),
                y=alt.Y("label:N", sort="x", title=None),
                tooltip=[
                    "rank",
                    "experiment",
                    "change",
                    "quant_val_bpb",
                    "float_val_bpb",
                    "steps",
                    "model_params",
                ],
            )
            .properties(height=max(180, 28 * len(plot_df)))
        )
    chart
    return


@app.cell
def _(df, mo):
    incomplete = df.loc[df["quant_val_bpb"].isna()].copy()
    if incomplete.empty:
        view = mo.md("")
    else:
        cols = [
            column
            for column in (
                "experiment",
                "steps",
                "status_code",
                "exit_status",
                "run_id",
            )
            if column in incomplete.columns
        ]
        view = mo.vstack(
            [
                mo.md(
                    """
    ### Incomplete / smoke runs

    These records synced without a quantized val BPB (wallclock smoke or failed
    validation). They stay out of the ranking.
    """
                ),
                mo.ui.table(incomplete[cols], selection=None),
            ]
        )
    view
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reading the board

    - **Rank metric:** quantized validation BPB — the number that survives
      deployment-style quantization. Float BPB is shown for reference.
    - **Lineage:** when present, `parent` + `change` record the single edit relative
      to the previous run.
    - **Unequal budgets:** step counts and wallclock caps differ across rows; use the
      board to track progress, not to claim a head-to-head winner without matched
      budgets.

    ## Extending

    - New runs appear in local scans once their `result.json` lands under `runs/`.
    - Refresh the sealed public snapshot by regenerating `notebooks/public/results.json`
      from the run tree, then re-pin publication hashes.
    """)
    return


if __name__ == "__main__":
    app.run()
