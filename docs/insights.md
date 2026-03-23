# Insights

Curated experiment learnings pulled into the public repo from the current working notes.

## Key Findings

### Partial RoPE is the strongest low-cost architecture win so far

- Rotating only `16/64` head dimensions improved quality slightly while also running a bit faster.
- The clean MI300X `exp004_partial_rope_clean` run nearly matched the best baseline throughput and outperformed the other Phase 1 ablations.
- This is the current carry-forward default.

### Bigger batch was a clear loss on A40

- Moving from `524288` to `786432` training tokens per step reduced total steps sharply and hurt final BPB.
- The loss was mostly systems-driven: slower steps wiped out any theoretical benefit from the larger batch.
- Current default is to stay at `524288` on the A40 lane.

### Late QAT looks real, but the short A40 window limits confidence

- Late QAT improved the quantized metric slightly relative to the causal-fix baseline.
- The effect size on A40 is small because the QAT tail only gets a short number of steps.
- It remains worth carrying forward, but not as the primary architecture bet.

### SWA is a modest improvement, not the current winner

- SWA beat the causal-fix baseline.
- It still landed a bit behind the best Partial RoPE family runs.
- It is worth revisiting on longer or stronger runs, not treating as the lead path today.

### LN Scale hurts in the short-run regime

- LN Scale was slower and worse at the checkpoints that mattered in the current A40 setup.
- The working interpretation is that it behaves like a regularizer, which is a poor fit when the model is still strongly undertrained.

### Runtime and evaluation policy matter as much as architecture

- The ROCm 7.2 / PyTorch 2.10 container baseline was a major systems improvement over the earlier eager host path.
- Full validation scans and final quantized evals are expensive enough to noticeably slow iteration.
- For day-to-day work, evaluation policy needs to be treated as a first-class experiment parameter.

### Current A40 pods need conservative NCCL settings

- The working 8-GPU DDP recipe required `NCCL_IB_DISABLE=1` and `NCCL_P2P_DISABLE=1`.
- Without those flags, the pod could hang at the first collective even after process-group setup succeeded.

## Working Rule Of Thumb

- Use one bounded change per run.
- Compare runs only within similar concurrency conditions.
- Promote promising variants quickly instead of over-spending on weak short probes.
