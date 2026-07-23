# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.17.6"
app = marimo.App(
    width="medium",
    app_title="Parameter Golf — Technique Explorer",
)


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Parameter Golf — Technique Explorer

    Parameter Golf is our fixed-budget training game: a ~27M-parameter GPT, a fixed
    wall-clock window, and one sealed metric — validation bits-per-byte after an
    int8+zlib roundtrip, lower is better. The question we keep returning to is
    simple: **how far can fixed-budget small-model training be pushed, and in what
    order should the budget be spent?**

    Early on we ranked techniques by how promising they sounded. That failed in a
    specific way. Our 8xA40 pods give us roughly 1,070 steps in a 600-second
    window, while the reference H100 record took 10,000+ steps. A technique whose
    benefit only appears after a few thousand steps — a regularizer, a weight
    average, an auxiliary loss — cannot show its effect inside that window, so
    ranking a late-signal technique on a short run measures noise, not the
    technique. We learned this the concrete way: LN Scale finished last in every
    short-run metric, and the honest reading was "wrong window," not "bad idea."

    So this catalog organizes the fourteen techniques we track by **signal
    timing**: how many steps a change typically needs before its effect is
    distinguishable from run-to-run noise. Signal timing, not expected effect
    size, decides where a technique belongs in the budget.
    """)
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


@app.cell(hide_code=True)
def _(mo, techniques):
    signal_counts = {"early": 0, "medium": 0, "late": 0}
    for row in techniques:
        signal_counts[row["signal"]] += 1
    mo.md(
        f"""
    ## Reading the catalog

    **{len(techniques)}** techniques ·
    **{signal_counts["early"]}** early ·
    **{signal_counts["medium"]}** medium ·
    **{signal_counts["late"]}** late

    | Signal | Steps before ranking is meaningful | How we spend budget on it |
    |---|---|---|
    | early | ~200–500 steps (some from step 1) | cheap 600 s directional checks, several per day, contention tolerated |
    | medium | ~500–2000 steps | 1800 s exclusive promotion runs, only after a clean early screen |
    | late | 2000+ steps or post-training | full-length runs only; never graded from a short probe |

    The sequencing rule we actually follow: screen early-signal ideas in short
    contended batches, promote anything that survives to an exclusive 1800 s run,
    and reserve long exclusive runs for late-signal techniques and finalists. Two
    corollaries keep us honest. First, a short-run loss for a medium- or
    late-signal technique is not evidence against it — it is evidence we used the
    wrong window. Second, contended runs are only comparable to other runs in the
    same concurrency bucket; promotion decisions always get an exclusive rerun.
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


@app.cell(hide_code=True)
def _(mo, signal_filter, techniques):
    filtered = techniques
    if signal_filter.value != "all":
        filtered = [t for t in techniques if t["signal"] == signal_filter.value]

    rows = [
        f"| {t['name']} | {t['signal']} | {t['steps']} | {t['cost']} | {t['notes']} |"
        for t in filtered
    ]
    mo.md(
        f"""
    ## Techniques

    Showing **{len(filtered)}** technique(s). We use the filter above to build a
    run queue for a given window: *early* rows are safe to rank in a 600 s check,
    *medium* rows need an 1800 s exclusive run, and *late* rows are only worth
    queueing when a full-length slot is available.

    | Technique | Signal | Steps to rank | Cost | Notes |
    |---|---|---|---|---|
    {chr(10).join(rows)}
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What we actually tried

    Entries distilled from the run record. Unless noted, runs are 8xA40, 600 s
    wall-clock, ~1,070 steps; the sealed metric is int8+zlib roundtrip val_bpb.

    - **SmearGate — the bug that taught us the most.** We added a
      neighbor-blending gate and saw val_bpb 0.0022 by step 100, far below the
      1.1248 competition record. It was leaking the answer: the pad copied
      position i+1 into position i, and the next input token is the current
      target. Made causal-only, the rerun gave an honest 1.3786 at 1,074 steps.
      Suspiciously good loss is a bug signal, not a breakthrough.
    - **Partial RoPE — the free win we carry forward.** We rotated 16 of 64 head
      dims. The run was faster (549 vs 559 ms/step, ~20 extra steps in the
      window) and finished at 1.3711 quant BPB vs 1.3786 for the causal-fix
      baseline — best or tied-best of the family. It is now our default.
    - **LN Scale — a regularizer punished us for underfitting.** We enabled
      depth-scaled residuals and it finished last in every metric: 1.3916 quant
      BPB, slowest at 563 ms/step. At ~1,070 steps the model has seen under 0.7%
      of the data, and regularizing an underfitting model makes it worse. We
      would only retest it at 5,000+ steps.
    - **Bigger batch (786K tokens) — a systems loss, not a modeling result.** We
      raised batch 1.5× to use spare VRAM; steps got 46% slower, we got 31% fewer
      of them, and quant BPB fell to 1.4877 vs 1.3786. In this regime more
      gradient updates beat stabler gradients.
    - **EMA — the signal-timing table predicted this one.** Our clean exclusive
      MI300X check of EMA(0.997) finished at 1.4870 val_bpb over 815 steps vs
      1.3971 for the same-window baseline: behind, exactly what we expect when a
      weight average gets too few late snapshots. An earlier contended read was
      unusable (3× GPU sharing).
    - **XSA and Late QAT — reads we refuse to grade yet.** The XSA4 run (on
      1×MI300X) landed at 1.5011 val_bpb over only 481 steps, confounded by a
      slow manual attention path — implementation speed drowned the architecture
      signal. Late QAT's 4%
      tail was just 43 steps here and still moved quant BPB 1.3786 → 1.3711; real
      but tiny, and the fair test needs a 10,000-step run.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Where this goes next

    Honest next steps, taken from the open questions in our own run record:

    1. **Finish the fair NTK verdict.** Fixed-length eval never exercises longer
       context, so our earlier NTK run could look like a no-op even if the code is
       correct. The live test (`exp018_ntk_sliding_eval_gqa`) evaluates 2048-token
       windows with stride 64; that run, not the fixed-length one, decides NTK.
       The interrupted KV8+NTK branch (killed at step 300) also still owes us a
       clean rerun.
    2. **Give regularizer-shaped ideas a long-run lane.** LN Scale, SWA, EMA, and
       the JEPA/STP family all act like regularizers, and grokking-style effects
       can land at step 1,500–3,000 — outside our ~1,070-step A40 window. The plan
       is 2,400 s (~3,200-step) windows, or H100 runs with 5,000+ steps, before we
       pass judgment on any of them.
    3. **Re-stack the small wins on the best base.** SWA (1.3741) and Late QAT
       (1.3711) each beat the 1.3786 baseline on their own. The queued follow-up
       is OrthoInit on the Partial-RoPE base (`exp017_partial_rope_ortho`), then
       re-applying Late QAT — possibly with an 8–10% tail on A40 so the effect is
       measurable — once the architecture stack settles.

    Companion view: the public **Run Leaderboard** notebook ranks sealed
    `result.json` artifacts by quantized validation BPB.
    """)
    return


if __name__ == "__main__":
    app.run()
