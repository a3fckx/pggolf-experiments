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

    ## Reading brief

    **Question.** Under a fixed wall-clock cap and one sealed metric — int8+zlib
    validation bits-per-byte, lower is better — how should we sequence experiments
    on a ~27M-parameter GPT so each run buys information, not noise?

    **Prior idea (experiment prioritization).** Training techniques differ in
    *signal timing*: how many steps before an effect separates from run-to-run
    variance. Competition ablations and the modded-nanogpt speedrun treat Muon,
    QK-norm, and init choices as *early* (visible within 100–500 steps); EMA and
    width changes as *medium* (~500–2,000 steps); depth recurrence, auxiliary
    representation losses, and late QAT as *late* (2,000+ steps or the final tail).
    Ranking a late-signal idea on a short probe therefore measures the window, not
    the technique — the same mistake as grading a regularizer while the model is
    still underfitting.

    **What this catalog decides.** It tags fourteen tracked techniques by minimum
    viable evaluation length and maps each band to a budget lane: cheap 600 s
    directional screens for early signal, 1,800 s exclusive promotion for medium
    signal, full-length slots for late signal. Expected effect size is secondary;
    *when* an idea can be graded drives the queue.

    **Concrete lesson.** LN Scale finished last on every short-run metric; the
    honest read was "wrong window," not "bad idea." SmearGate's suspiciously low
    loss at step 100 was a causal leak, not a breakthrough — suspiciously good
    early numbers are a bug signal first.

    Parameter Golf is our fixed-budget training game. The companion **Run
    Leaderboard** notebook ranks sealed `result.json` artifacts; this view ranks
    *ideas before we spend the next run*.
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
    ## Timing-band scorecard

    **{len(techniques)}** techniques in catalog ·
    **{signal_counts["early"]}** early ·
    **{signal_counts["medium"]}** medium ·
    **{signal_counts["late"]}** late

    | Band | Count | Min steps to rank | Budget lane | Representative techniques |
    |---|---:|---|---|---|
    | early | {signal_counts["early"]} | 1–500 | 600 s contended screen; several per day | Muon, SmearGate, BigramHash, XSA, QK-Norm + Z-loss, OrthoInit + LN Scale |
    | medium | {signal_counts["medium"]} | 500–2,000 | 1,800 s exclusive promotion after early screen | 3×MLP, EMA, AttnRes, Partial RoPE |
    | late | {signal_counts["late"]} | 2,000+ or final tail | full-length slot only; never short-probe graded | Depth recurrence, STP-lite, JEPA-lite, Late QAT |

    | Claim | Evidence basis | Sequencing rule |
    |---|---|---|
    | Early band is short-probe viable | Muon vs AdamW visible by ~100 steps; QK-norm prevents divergence from step 1 (competition ablations; Keller Jordan speedrun) | Rank several early ideas per 600 s window |
    | Medium band needs promotion length | EMA benefit needs ~1,000+ late snapshots; 3×MLP ranks reliably only after ~800–1,200 steps (Apple EMA scaling note; PG ablation table) | Exclusive 1,800 s rerun before trusting order |
    | Late band is window-sensitive | Depth recurrence, JEPA/STP aux losses, Late QAT tail need thousands of steps or the last ~4% of training | Queue only when a long slot exists |
    | Short loss ≠ negative verdict for late ideas | LN Scale regressed at ~1,070 steps on an underfit model | Retest at 5,000+ steps, not in the screen queue |

    Filter the table below by band to build a run queue for the window you actually have.
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
    ## Interpretation

    **Budget sequencing takeaway.** Signal timing is the primary sort key for the
    queue, not charisma or paper prestige. Burn cheap 600 s batches on early-band
    ideas where a few hundred steps already separate signal from noise; spend
    1,800 s exclusive runs only on medium-band survivors; hold late-band and
    regularizer-shaped ideas until step counts match their design (thousands of
    steps, or the final quantization tail). Promotion — re-running the current
    winner at 3× wallclock — is how the sealed leaderboard moved from ~1.40 to
    **1.2949** quantized val BPB; that hop is mostly more steps on the best
    variant, not a new architecture trick.

    **What this catalog is not.** It is not a controlled bake-off of all fourteen
    techniques at matched budgets. Many rows are still hypotheses queued by timing
    band; the narrative bullets above are selected run-record reads, not a complete
    factorial. Before any head-to-head claim, equalize steps and wallclock — the
    leaderboard lineage view exists for that honesty check.

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
