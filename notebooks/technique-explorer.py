# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "marimo",
#     "pandas",
# ]
# ///

import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium", app_title="Parameter Golf — Technique Explorer")


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell
def _(mo):
    mo.md(
        r"""
# Parameter Golf — Technique Explorer

Under a fixed compute and parameter budget, which training ideas are worth a short
directional check — and which ones need a full-length run before their effect is
distinguishable from noise?

This catalog ranks fourteen techniques by **signal timing**: how many steps you
typically need before a change can be ranked. Use it to sequence a Parameter Golf
budget: spend early steps on early-signal ideas, and reserve long runs for
late-signal techniques.
"""
    )
    return


@app.cell
def _():
    techniques = [
        {
            "name": "SmearGate",
            "signal": "early",
            "steps": "200–500",
            "cost": "dim params (~2KB)",
            "notes": "Per-dim sigmoid gate blending current token with previous token. Strong early signal.",
        },
        {
            "name": "BigramHash",
            "signal": "early",
            "steps": "200–500",
            "cost": "2K–10K hash buckets",
            "notes": "Deterministic hash of token pairs added to embeddings. Zero-init; ramps by ~300 steps.",
        },
        {
            "name": "XSA (Exclusive Self-Attention)",
            "signal": "early",
            "steps": "200–500",
            "cost": "small compute",
            "notes": "Subtract self-value projection from attention output. Apply to last 3–4 layers.",
        },
        {
            "name": "Muon optimizer",
            "signal": "early",
            "steps": "1–200",
            "cost": "Newton–Schulz steps",
            "notes": "Orthogonalized momentum. ~2× token efficiency over AdamW, visible from step 1.",
        },
        {
            "name": "OrthoInit + LN Scale",
            "signal": "early",
            "steps": "1–200",
            "cost": "none",
            "notes": "Enables stable deep (11L+) training from the start.",
        },
        {
            "name": "QK-Norm + Z-loss",
            "signal": "early",
            "steps": "1–200",
            "cost": "none",
            "notes": "Stability techniques. Prevent divergence and entropy drift immediately.",
        },
        {
            "name": "3×MLP",
            "signal": "medium",
            "steps": "800–1200",
            "cost": "params",
            "notes": "Incremental capacity gain. Needs ~800–1200 steps to rank reliably.",
        },
        {
            "name": "EMA",
            "signal": "medium",
            "steps": "1000–1500",
            "cost": "memory",
            "notes": "Weight averaging. Benefit visible after ~1000–1500 steps.",
        },
        {
            "name": "AttnRes / Block AttnRes",
            "signal": "medium",
            "steps": "500–2000",
            "cost": "small",
            "notes": "Depth-wise attention over residuals. Strong paper evidence, cheap to implement.",
        },
        {
            "name": "Partial RoPE",
            "signal": "medium",
            "steps": "500+",
            "cost": "memory/compute",
            "notes": "Apply RoPE to ~10% of dimensions. Needs ~500+ steps to distinguish from noise.",
        },
        {
            "name": "Depth recurrence",
            "signal": "late",
            "steps": "2000–3000+",
            "cost": "complexity",
            "notes": "Shared-weight loops. Requires 2000–3000+ steps. Best recorded result ~1.1629 BPB.",
        },
        {
            "name": "STP-lite",
            "signal": "late",
            "steps": "2000+",
            "cost": "aux loss",
            "notes": "Semantic Tube Prediction. Constrains hidden-state geometry. Risky at <100M params.",
        },
        {
            "name": "JEPA-lite",
            "signal": "late",
            "steps": "3000–5000",
            "cost": "aux loss",
            "notes": "Hidden-state prediction auxiliary loss. Needs 3000–5000 steps; may not help at this scale.",
        },
        {
            "name": "Late QAT",
            "signal": "late",
            "steps": "last ~4%",
            "cost": "quantization",
            "notes": "Fake quantization in last 4% of training. Possibly a no-op under torch.compile.",
        },
    ]
    return (techniques,)


@app.cell
def _(mo, techniques):
    signal_counts = {"early": 0, "medium": 0, "late": 0}
    for row in techniques:
        signal_counts[row["signal"]] += 1
    mo.md(
        f"""
## Catalog size

**{len(techniques)}** techniques ·
**{signal_counts["early"]}** early ·
**{signal_counts["medium"]}** medium ·
**{signal_counts["late"]}** late

| Signal | Typical steps before ranking is meaningful |
|---|---|
| early | measurable within ~200–500 steps (some from step 1) |
| medium | ~500–2000 steps |
| late | 2000+ steps or post-training |
"""
    )
    return


@app.cell
def _(mo):
    signal_filter = mo.ui.dropdown(
        options=["all", "early", "medium", "late"],
        value="all",
        label="Signal timing",
    )
    signal_filter
    return (signal_filter,)


@app.cell
def _(mo, pd, signal_filter, techniques):
    filtered = techniques
    if signal_filter.value != "all":
        filtered = [t for t in techniques if t["signal"] == signal_filter.value]

    table = pd.DataFrame(filtered)[["name", "signal", "steps", "cost", "notes"]]
    table = table.rename(
        columns={
            "name": "Technique",
            "signal": "Signal",
            "steps": "Steps to rank",
            "cost": "Cost",
            "notes": "Notes",
        }
    )
    mo.vstack(
        [
            mo.md(f"Showing **{len(filtered)}** technique(s)."),
            mo.ui.table(table, selection=None, page_size=20),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
## How to use this in an experiment budget

1. **Short directional checks (≤500 steps):** only early-signal techniques. Ranking a
   late-signal idea here mostly measures noise.
2. **Medium runs (500–2000 steps):** add capacity and averaging ideas (3×MLP, EMA,
   Partial RoPE, AttnRes).
3. **Full-length / promo runs:** reserve for late-signal techniques and for promoting
   a medium-signal winner (for example Partial RoPE promo).

Companion view: the public **Run Leaderboard** notebook ranks sealed `result.json`
artifacts by quantized validation BPB.
"""
    )
    return


if __name__ == "__main__":
    app.run()
