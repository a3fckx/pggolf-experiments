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

    ## Reading brief

    **Question.** After each bounded edit to the training harness, what single
    change buys the lowest **quantized** validation bits-per-byte inside a fixed
    wallclock cap?

    **Prior idea (early vs late signal).** Fixed-budget experiment design treats
    techniques by when their effect becomes measurable: optimizer and stability
    edits show signal within hundreds of steps; capacity and averaging edits need
    ~500–2,000; recurrence, auxiliary losses, and late quantization need
    thousands of steps or the training tail. A board row therefore encodes both
    *what we changed* and *how long we let it run* — unequal step counts are
    features of the lineage, not noise to ignore.

    **What this snapshot decides.** It ranks sealed `notebooks/public/results.json`
    artifacts on int8+zlib roundtrip val BPB (lower is better). Float BPB, step
    count, and step time ride along for context. Rows without a quantized metric
    stay out of the ranking as smoke or incomplete syncs.

    **Honest caveat.** Runs differ in step count and wallclock budget. Read the
    board as a **lineage view** — each row is one bounded change on its parent —
    not one controlled bake-off. Head-to-head claims require matched budgets.
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
    return (n_incomplete, n_ranked, ranked,)


@app.cell(hide_code=True)
def _(mo, n_incomplete, n_ranked, pd, ranked, source):
    if ranked.empty:
        scorecard = mo.md("_No ranked runs — scorecard empty._")
    else:
        ordered = ranked.sort_values("quant_val_bpb").reset_index(drop=True)
        leader_bpb = float(ordered.iloc[0]["quant_val_bpb"])
        rows = []
        for rank, (_, row) in enumerate(ordered.iterrows(), start=1):
            bpb = float(row["quant_val_bpb"])
            delta = bpb - leader_bpb
            _steps = row.get("steps")
            steps_text = (
                f"{int(_steps):,}" if _steps is not None and pd.notna(_steps) else "—"
            )
            change = row.get("change") or "—"
            rows.append(
                {
                    "rank": rank,
                    "experiment": row["experiment"],
                    "quant val BPB": f"{bpb:.4f}",
                    "Δ vs leader": f"+{delta:.4f}" if delta else "0.0000",
                    "steps": steps_text,
                    "lane": change,
                }
            )
        scorecard = mo.vstack(
            [
                mo.md(
                    f"""
    ## Claim scorecard (sealed snapshot)

    Numbers from {source} only — no live recompute. **{n_ranked}** ranked ·
    **{n_incomplete}** excluded (null quantized BPB).
    """
                ),
                mo.ui.table(pd.DataFrame(rows), selection=None, show_column_summaries=False),
                mo.md(
                    """
    | Claim | Sealed evidence | Caveat |
    |---|---|---|
    | Current leader | `exp004_partial_rope_promo` @ **1.2949** quant val BPB, 2,463 steps | 3× wallclock promotion of partial-RoPE winner — mostly more steps, not a new edit |
    | Best 600 s ablation | `exp004_partial_rope_clean` @ **1.4032**, 821 steps | Phase-1 screen; within noise of compiled ~1.40 baseline (baseline not in this snapshot) |
    | Systems floor | `baseline` @ **2.0668**, 251 steps (eager, ~2,397 ms/step) | Wallclock went to overhead, not learning |
    | Medium-signal miss | `exp003_ema_clean` @ **1.4905**, 815 steps | EMA needs late snapshots — short window, not a fair EMA verdict |
    | Early-signal confound | `exp002_xsa4` @ **1.5135**, 481 steps | Slow manual attention path; implementation drowned architecture signal |

    Δ vs leader is descriptive only. Unequal step counts mean this is **lineage
    ordering**, not a matched-budget A/B table.
    """
                ),
            ]
        )
    scorecard
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
    ## Interpretation

    **Budget sequencing takeaway.** The sealed path is systems first (eager baseline
    at **2.0668** → compiled ~1.40, inherited by Phase 1 rows), then cheap
    architecture screens at 600 s, then promotion of the current winner at 3×
    wallclock. The headline move to **1.2949** is `exp004_partial_rope_promo` at
    2,463 steps — mostly more training on the best partial-RoPE variant, not a
    new trick. That matches the experiment-prioritization rule: rank early edits
    in short probes, spend long budgets only on survivors.

    **Lineage, not controlled A/B.** Step counts span 251 to 2,463; wallclock caps
    differ. The table orders progress through bounded edits (`parent` + `change`),
    not a factorial at matched steps. `exp003_ema_clean` trailing at **1.4905** is
    consistent with medium-signal timing on a short window, not proof EMA fails.
    Before any head-to-head claim, re-run contenders at equal steps and wallclock.

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
