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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parameter Golf — Run Leaderboard

    This board is the running score of our Parameter Golf experiments, and the loop
    behind every row is the same: we edit one thing in the training harness, launch
    it remotely (RunPod, a single MI300X) under a fixed wallclock cap, and the pod
    syncs a `result.json` back into the repository when the run ends. The notebook
    ranks those synced artifacts.

    We rank on **quantized validation bits-per-byte** (lower is better) because the
    quantized number is the one that survives deployment-style compression — a
    variant that looks good in float but degrades after quantization is not a win
    we get to keep. Float BPB, step count, step time, and parameter count ride
    along for context.

    One honest caveat before reading further: runs differ in step count and
    wallclock budget, so the board is a lineage view — each row is one bounded
    change on its parent — not one controlled bake-off. When we care about a
    head-to-head claim, we re-run at matched budgets.

    The published page renders the sealed `notebooks/public/results.json` snapshot;
    local checkouts without that snapshot scan `../runs/**/result.json` instead.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How the board moved

    The question behind the sequence was always the same: what single edit buys
    quantized BPB inside a fixed wallclock? Read bottom-up, the chart is the path
    from 2.067 to 1.295:

    - **`baseline` → 2.0668:** the eager-mode start — at ~2,397 ms/step the 600 s
      cap bought only 251 steps, so the wallclock went to overhead, not learning.
    - **Compiled container → ~1.40:** the ROCm 7.2 / PyTorch 2.10 container cut
      steps to ~735 ms, roughly 3x the steps per cap (`docs/results.md` puts that
      baseline at 1.4005; the run is not in this sealed snapshot, but every
      Phase 1 row below inherits it).
    - **`exp002_xsa4` → 1.5135:** we tried exclusive self-attention (each token
      attends to every position but itself) on the last four layers, but a slow
      manual attention path confounded it (481 steps), so it never got a fair
      read.
    - **`exp003_ema_clean` → 1.4905:** EMA(0.997) weight averaging bought roughly
      nothing in this short-run regime.
    - **`exp001_11L_3xMLP_clean` → 1.4311:** deeper and wider (11 layers, 3x MLP,
      26.5M params) helped per step, but ~992 ms steps cost total steps.
    - **`exp004_partial_rope_clean` → 1.4032:** rotating only 16 of 64 head dims
      was the edit that cost nothing — the best of the Phase 1 ablations and
      slightly faster than its siblings (731.81 ms/step, 821 steps), landing
      within noise of the compiled baseline's 1.4005.
    - **`exp004_partial_rope_promo` → 1.2949:** the winner promoted to a 3x
      wallclock (1,800 s, 2,463 steps) — most of the drop is simply more steps on
      the strongest variant.

    What we took from it: the biggest hop was systems (eager → compiled), the best
    architecture edit was the cheapest one (partial RoPE), and promotion —
    spending real budget only on the current winner — is what moved the headline
    number.
    """)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What we'd try next

    The open questions in `docs/results.md` and `docs/insights.md` set the queue:

    - **Keep stacking on partial RoPE, one bounded change per run.** It is the
      carry-forward default, so every new feature gets tested against that base —
      when a run regresses, there is exactly one suspect.
    - **Give late QAT a longer tail.** It improved the quantized metric slightly,
      but the short window kept the effect size small and the confidence low;
      we would re-run it with a longer budget before promoting it.
    - **Revisit SWA on longer runs.** It beat the causal-fix baseline yet landed
      behind the partial-RoPE family; the short regime may be underselling it.
    - **Re-run the contenders at matched budgets.** The board is lineage; before
      claiming a head-to-head winner we would equalize steps and wallclock.
    - **Treat evaluation policy as an experiment parameter.** Full validation
      scans and final quantized evals are expensive enough to slow iteration, so
      how often we evaluate is itself a knob worth tuning.

    Two things we would not re-try soon: LN Scale (it behaves like a regularizer,
    a poor fit while the model is this undertrained) and the larger 786,432-token
    batch (a systems loss on A40 — slower steps erased the theoretical benefit).
    """)
    return


if __name__ == "__main__":
    app.run()
