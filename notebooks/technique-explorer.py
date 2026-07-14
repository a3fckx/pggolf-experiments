# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    techniques = [
        {
            "name": "SmearGate",
            "signal": "early",
            "cost": "dim params (~2KB)",
            "notes": "Per-dim sigmoid gate blending current token with previous token. Strong early signal.",
        },
        {
            "name": "BigramHash",
            "signal": "early",
            "cost": "2K-10K hash buckets",
            "notes": "Deterministic hash of token pairs added to embeddings. Zero-init, ramps by ~300 steps.",
        },
        {
            "name": "XSA (Exclusive Self-Attention)",
            "signal": "early",
            "cost": "small compute",
            "notes": "Subtract self-value projection from attention output. Apply to last 3-4 layers.",
        },
        {
            "name": "Muon optimizer",
            "signal": "early",
            "cost": "Newton-Schulz steps",
            "notes": "Orthogonalized momentum. ~2x token efficiency over AdamW, visible from step 1.",
        },
        {
            "name": "OrthoInit + LN Scale",
            "signal": "early",
            "cost": "none",
            "notes": "Enables stable deep (11L+) training from the start.",
        },
        {
            "name": "QK-Norm + Z-loss",
            "signal": "early",
            "cost": "none",
            "notes": "Stability techniques. Prevent divergence and entropy drift immediately.",
        },
        {
            "name": "3xMLP",
            "signal": "medium",
            "cost": "params",
            "notes": "Incremental capacity gain. Needs ~800-1200 steps to rank reliably.",
        },
        {
            "name": "EMA",
            "signal": "medium",
            "cost": "memory",
            "notes": "Weight averaging. Benefit visible after ~1000-1500 steps.",
        },
        {
            "name": "AttnRes / Block AttnRes",
            "signal": "medium",
            "cost": "small",
            "notes": "Depth-wise attention over residuals. Strong paper evidence, cheap to implement.",
        },
        {
            "name": "Partial RoPE",
            "signal": "medium",
            "cost": "memory/compute",
            "notes": "Apply RoPE to ~10% of dimensions. Needs ~500+ steps to distinguish from noise.",
        },
        {
            "name": "Depth recurrence",
            "signal": "late",
            "cost": "complexity",
            "notes": "Shared-weight loops. Requires 2000-3000+ steps. Best result ~1.1629 BPB.",
        },
        {
            "name": "STP-lite",
            "signal": "late",
            "cost": "aux loss",
            "notes": "Semantic Tube Prediction. Constrains hidden-state geometry. Risky at <100M params.",
        },
        {
            "name": "JEPA-lite",
            "signal": "late",
            "cost": "aux loss",
            "notes": "Hidden-state prediction auxiliary loss. Needs 3000-5000 steps; may not help at this scale.",
        },
        {
            "name": "Late QAT",
            "signal": "late",
            "cost": "quantization",
            "notes": "Fake quantization in last 4% of training. Possibly a no-op under torch.compile.",
        },
    ]
    return (techniques,)


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
def _(mo, signal_filter, techniques):
    filtered = techniques
    if signal_filter.value != "all":
        filtered = [t for t in techniques if t["signal"] == signal_filter.value]

    rows = []
    for _t in filtered:
        rows.append(
            f"| {_t['name']} | {_t['signal']} | {_t['cost']} | {_t['notes']} |"
        )

    mo.md(
        f"""
        ## Parameter Golf Technique Explorer

        Showing **{len(filtered)}** techniques.

        | Technique | Signal | Cost | Notes |
        |---|---|---|---|
        {chr(10).join(rows)}

        ### Signal timing legend

        - **early** = measurable within 200-500 steps
        - **medium** = 500-2000 steps
        - **late** = 2000+ steps or post-training

        See also: [[OpenAI Parameter Golf]], [[Inbox Research Digest — 2026-03 to 2026-06]]
        """
    )
    return


if __name__ == "__main__":
    app.run()
