---
tags:
  - experiment-log
date: 2026-03-21
---

# Experiment Insights

Patterns, learnings, and unexpected findings from Parameter Golf experiments.

## Findings

### Finding: Current RunPod A40 pod needs NCCL IB/P2P disables for healthy 8-GPU DDP
- **Experiment**: `exp017_meta_stack_core` bring-up on RunPod 8xA40
- **Observation**: a tiny 8-GPU DDP smoke test successfully reached `init_process_group()` on all ranks, but the first `all_reduce()` hung on the current pod. Setting `NCCL_IB_DISABLE=1` and `NCCL_P2P_DISABLE=1` made the same smoke test complete and unblocked the real 8-GPU training run.
- **Hypothesis**: the current pod advertises a transport/topology path that NCCL tries first, but that path is not healthy on this box. For this pod, forcing a simpler transport is more reliable than the default auto-detection.
- **Action**: launch current A40 8-GPU runs with `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1` and treat that as part of the active RunPod recipe until a later pod/image proves otherwise.

### Finding: Repo-native experiment scripts are useful launch wrappers, but several still point at unimplemented features
- **Experiment**: RunPod repo review
- **Observation**: `experiments/run_all.sh` and the per-experiment `exp0*/run.sh` files are the intended orchestration layer, but `exp03_11L_xsa4`, `exp04_11L_partial_rope_ln_scale`, and `exp05_11L_grad_guided_quant` explicitly say their headline features are not yet implemented inside `train_gpt_sota.py`.
- **Hypothesis**: the experiment queue was scaffolded faster than feature code was merged, so the repo can look more complete than the executable harness really is.
- **Action**: treat the repo scripts as the right launch pattern, but verify implementation in `train_gpt_sota.py` or the experiment snapshot before trusting a run label. Keep `exp017_meta_stack_core` as the working harness for one-by-one stack ablations.

### Finding: MI300X baseline throughput and BPB
- **Experiment**: baseline
- **Observation**: 251 steps in 600s (2.4s/step avg). val_bpb=1.9603 pre-quant, 2.0668 after int8+zlib. Peak VRAM 20.1 GiB of 192 GiB available. Train loss dropped 6.93→3.38 over 251 steps.
- **Hypothesis**: Single MI300X is ~10x slower per-step than 8xH100 cluster. BPB gap vs competition target (1.120) is mostly throughput-limited — same model with more steps/better optimizer should close significantly.
- **Action**: Phase 1 optimizations (Muon, XSA, EMA) should improve BPB substantially. VRAM headroom (20/192 GiB) means parallel experiments are safe, but development runs also need a cheaper eval policy.

### Finding: Fast runs are still paying full validation and quantization tax
- **Experiment**: baseline harness review
- **Observation**: `train_gpt.py` always scans the full `62,021,632`-token validation split and always performs the final int8+zlib roundtrip validation. The completed baseline spent `49,290 ms` on the final quantized eval alone, and the wrapper scripts can still trigger repeated full validations.
- **Hypothesis**: day-to-day iteration speed is being hurt more by evaluation policy than by raw training-step speed alone.
- **Action**: split runtime into `dev-fast`, `compare`, and `promotion/final` modes so only promotion runs pay the full validation and quantization cost.

### Finding: Empty local phase folders mostly reflected missing sync, not missing work
- **Experiment**: coordination layer
- **Observation**: live runs and helper scripts already existed on the VM, but the local vault phase folders had not yet been populated with promoted artifacts or status files.
- **Hypothesis**: the contract between VM scratch directories and local vault mirrors was implicit, so the local state looked emptier than the real experiment state.
- **Action**: maintain visible local mirrors with `README.md`, `result.json`, and synced logs so humans and agents can read the current state without SSH.

### Finding: ROCm 7.2 / PyTorch 2.10 container baseline is the first truly usable dev baseline
- **Experiment**: baseline_rocm72_container
- **Observation**: the containerized run reached `816` steps in `601.168s` with float `val_bpb=1.3971` and quantized `val_bpb=1.4005`, versus the older eager host baseline at `251` steps with quantized `val_bpb=2.0668`.
- **Hypothesis**: most of the improvement comes from the newer ROCm/PyTorch runtime and its faster SDPA kernel path, not from a model architecture change.
- **Action**: treat the containerized baseline as the new reference point for upcoming Phase 1 experiments and stop using the older eager host path for ranking experiments.

### Finding: Python output buffering breaks remote log monitoring
- **Experiment**: all baseline runs
- **Observation**: `nohup python3 > log.txt` produces empty/stale files. Internal `log0()` writes buffered by Linux. Logs appeared stuck at step 10 for minutes while GPU was at 100%.
- **Hypothesis**: Python file writes are OS-buffered. SSH pipe commands (`| tail -50`) add another buffering layer.
- **Action**: Always use `PYTHONUNBUFFERED=1 python3 -u`. Check internal log at `~/parameter-golf/logs/<uuid>.txt`, not just redirected stdout.

### Finding: Competing GPU processes silently degrade — no crash, no error
- **Experiment**: baseline (accidentally ran 2 processes)
- **Observation**: Both ran at ~2x slower. Neither crashed. The only signal was step timing in logs (3.4s→6.8s).
- **Action**: When you want a clean baseline or promotion run, check for stale overlap first. During swarm mode, overlap is acceptable, but label the concurrency bucket clearly so the result is interpreted as a contended directional signal rather than an exclusive-run benchmark.

### Finding: Quantization overhead is tiny even without Late QAT
- **Experiment**: baseline_compiled
- **Observation**: Float val_bpb=1.3971, quantized=1.4005. Gap=0.0034 (0.24%).
- **Action**: Don't prioritize Late QAT in Phase 1. Architecture improvements (XSA, EMA) will give bigger gains.

### Finding: 9% VRAM usage confirms parallel experiments viable
- **Experiment**: baseline_compiled
- **Observation**: 18.5 GB used of 206 GB. 187 GB free.
- **Action**: Default to 4 parallel experiments per batch. Test 8 parallel to find compute contention sweet spot.

### Finding: Parallel slowdown is compute contention, not VRAM exhaustion
- **Experiment**: Phase 1 swarm runs on the single MI300X
- **Observation**: the clean ROCm 7.2 baseline averaged about `736 ms/step`, while contended runs landed closer to `1.39-1.74 s/step`. Even during the active `exp005_ln_scale` check, the GPU was pinned at `100%` with only `18.1/191.7 GB` VRAM in use.
- **Hypothesis**: the accelerator is compute-bound on attention and matmul work long before it is memory-bound, so parallel launches mostly divide throughput instead of filling unused VRAM.
- **Action**: keep swarm batches for directional signal, compare within similar concurrency buckets, and rerun only the most promising variants exclusively when we want promotion-quality numbers.

### Finding: Monitoring loops should match experiment lifecycle
- **Experiment**: baseline monitoring session
- **Observation**: 3 cron loops firing every 3/5/7 min = 8+ SSH checks when GPU was idle. Useful during training, pure noise otherwise.
- **Action**: Start monitors when experiments launch, kill when done. Never leave idle monitors running.

### Finding: Sub-agent swarm catches things orchestrator misses
- **Experiment**: full session coordination
- **Observation**: Ohm found `run_fast.sh` isn't snapshot-isolated. Sartre measured 62M validation overhead. Codex Relay independently identified Docker speed fix. None of these came from the main orchestrator.
- **Action**: Keep using the swarm. Different agents have different blind spots.

### Finding: Shared text files beat memory store for real-time multi-agent coordination
- **Experiment**: Claude Code + Codex Relay collaboration
- **Observation**: Codex Relay couldn't access memory store thread `T-F9ZTX1`, used their own `T-QC6YRP`. The markdown files (`task-board.md`, `AGENT_COORDINATION.md`) were the reliable shared layer.
- **Action**: Text files = durable coordination. Memory store = cross-session continuity. Don't rely on memory store for real-time state.

### Finding: Grokking risk — short runs may miss delayed learning effects
- **Experiment**: theoretical (informed by Phase 2/3 design)
- **Observation**: Grokking (Power et al. 2022) causes loss to plateau then suddenly drop after many steps. Our MI300X runs get ~800 steps; competition gets ~4000. Techniques that work via regularization (STP-lite, JEPA-lite, weight decay) may cause grokking at step 1500-3000 that we'd never see in 800-step runs.
- **Hypothesis**: Regularization-based techniques (STP, JEPA, depth recurrence) need more steps to manifest than architecture changes (XSA, layers, MLP expansion). Phase 1 techniques (architecture) show up fast. Phase 2/3 techniques (regularization) may grok late.
- **Action**: For Phase 2/3 experiments, use `MAX_WALLCLOCK_SECONDS=2400` (40 min, ~3200 steps) instead of default 600s. For Phase 1, 600s is fine — architecture changes help immediately. Monitor loss curves for plateau-then-drop patterns.

### Finding: Contended experiments are directional but not rankable against exclusive runs
- **Experiment**: exp001, exp003, exp004, exp005 (all GPU-contended)
- **Observation**: All got ~400-417 steps vs baseline's 816 exclusive. exp001_11L_3xMLP showed better per-step learning (loss 2.78 at step 200 vs baseline 2.82) but worse final val_bpb (1.5123 vs 1.3971) due to fewer total steps. Same pattern for all contended runs.
- **Action**: Compare contended runs ONLY against each other (same concurrency bucket). For promotion decisions, re-run exclusively. The contended runs told us: 11L+3xMLP learns faster per step, Partial RoPE and LN Scale are in the right ballpark, EMA result is unreliable (worst contention, 3x sharing).

### Finding: Non-causal SmearGate leaks future tokens, producing impossibly low BPB
- **Experiment**: `exp017_meta_stack_core` on RunPod 8xA40
- **Observation**: val_bpb=0.0022 and train_loss=0.004 by step 100 — orders of magnitude below the competition record of 1.1248. BPB formula and data were verified correct. A swarm investigation (Differ, BatchChecker, ArchInvestigator) traced the root cause to `SmearGate.forward()`: `right = F.pad(x[:, 1:], (0, 0, 0, 1))` copies position i+1's embedding into position i's local context. Since `input_ids[i+1] == target_ids[i]`, the model sees the answer it needs to predict. The sigmoid gate learns to extract this leaked info trivially.
- **Hypothesis**: SmearGate was ported from a bidirectional context (or designed without considering autoregressive causality). Averaging left+right neighbors is valid for masked language models but breaks next-token prediction. The known-good SOTA record script didn't include SmearGate at all; the bug was introduced when exp017 added it.
- **Action**: Fixed by making SmearGate causal-only (left neighbor only, no right). Re-run produced val_bpb=1.3786 (INT8+zlib) at 1,074 steps — realistic and still descending. Any future position-mixing module applied pre-attention MUST be verified causal. Treat "suspiciously good loss" as a bug signal, not a breakthrough.

### Finding: Partial RoPE and LN Scale ARE implemented despite experiment scripts claiming otherwise
- **Experiment**: exp017 script audit
- **Observation**: Experiment runner reports flagged Partial RoPE and LN Scale as "Not implemented, no env vars." This is wrong — `ROPE_DIM` (line 76) controls partial RoPE (set < head_dim to enable), and `LN_SCALE_ENABLED` (line 74) activates layer-depth scaling (`1/sqrt(layer_idx+1)`). Both are just disabled by default. NTK-RoPE is genuinely not implemented — the Rotary class uses a fixed `rope_base` with no dynamic scaling.
- **Hypothesis**: the experiment scaffolding was audited against `train_gpt_sota.py` which may have lacked these, but the exp017 snapshot (derived from a newer codebase) includes them.
- **Action**: update experiment runner metadata to reflect actual implementation status. Use `ROPE_DIM=32` and `LN_SCALE_ENABLED=1` in ablation runs. NTK-RoPE requires code changes to the Rotary class if we want to test it.

### Finding: 8xA40 gets ~1,074 steps in 600s wallclock — 10x fewer than 8xH100
- **Experiment**: exp017 causal fix run on RunPod 8xA40
- **Observation**: 559ms/step average, yielding 1,074 steps in 600s. The known-good record achieved 10,424 steps at 57.6ms/step on 8xH100. Final val_bpb=1.3548 (float) at step 1,074 vs 1.2092 at step 10,424 on H100 — the gap is mostly step count, not architecture quality.
- **Hypothesis**: A40 HBM bandwidth (768 GB/s) is 4.4x less than H100 (3,350 GB/s), and the attention/matmul throughput gap compounds to ~10x wall-clock difference per step. Loss curve was still descending at cutoff.
- **Action**: use A40 runs for directional signal and bug detection (this run successfully validated the SmearGate fix). For competitive BPB numbers, must run on H100. A40 results at 1,074 steps are roughly equivalent to H100 at step ~100.

### Finding: Only 49% VRAM utilized — massive headroom for bigger batch or model
- **Experiment**: exp017 runs on RunPod 8xA40
- **Observation**: Each GPU uses 22.6 GB of 46 GB (49%). Peak allocation from logs: 20.8 GB. Free: 23.4 GB per GPU × 8 = 183 GB wasted across the pod. The model (27.35M params) is tiny relative to the hardware.
- **Hypothesis**: The 8xA40 config was designed for H100s where the training loop is compute-bound, not memory-bound. The A40's smaller compute throughput means it can't saturate its own memory bandwidth. Larger batch or model would use the VRAM without proportionally slowing steps.
- **Action**: The raw VRAM headroom was real, but the follow-up runs showed it should not go to bigger batch on A40. Keep the fast 524K regime and use the headroom for cheap architectural ablations and fair longer-context tests instead of forcing full MHA.

### Finding: Late QAT effect is minimal at 1,074 steps — only 43 QAT steps
- **Experiment**: exp017 Late QAT (6-bit, 4% frac) vs causal-fix baseline
- **Observation**: Float BPB improved 1.3548 → 1.3480, INT8+zlib improved 1.3786 → 1.3711 (-0.008 BPB). Float→quant gap barely changed (0.0238 → 0.0231). Late QAT activated at step 1,031, ran only 43 steps.
- **Hypothesis**: 4% of 1,074 steps = 43 steps is insufficient for the model to adapt to quantization noise. On H100 with 10,000+ steps, 4% = 400+ QAT steps — should have a much larger effect on the quant gap.
- **Action**: Keep Late QAT enabled but don't evaluate its effectiveness on A40. The real test is H100. Consider increasing `late_qat_frac` to 0.08-0.10 for A40-only testing if we want to see the effect.

### Finding: SWA is a small real win, but not enough to beat the best Partial RoPE family
- **Experiment**: exp017 `Partial RoPE + SWA` on the A40 feature-hooks harness
- **Observation**: The run finished cleanly at `final_int8_zlib_roundtrip_exact val_bpb 1.37406320`. That is better than the causal-fix baseline (`1.37856702`) and better than LN Scale / batch786, but still slightly behind `Partial RoPE` alone (`1.37108571`) and the NTK-on-4KV family (`1.37173728`).
- **Hypothesis**: SWA is smoothing the late weights, but A40 only gives us a short late-training window, so the average has too few snapshots to beat the strongest architecture tweaks.
- **Action**: Keep SWA recorded as a real but modest improvement. It is worth carrying forward on stronger or longer-step runs, but it is not the current A40 winner.

### Finding: Partial RoPE (16/64) is a free win — faster, smoother, slightly better BPB
- **Experiment**: exp017 Partial RoPE (`ROPE_DIM=16`) vs full RoPE (`ROPE_DIM=64`), head-to-head on 8xA40
- **Observation**: Detailed step-by-step comparison:

**Speed**: 549 ms/step (partial) vs 559 ms/step (full) — 10ms faster, yields ~20 extra steps in 600s.

**Train loss curve** (side-by-side):

| Step | Partial RoPE | Full RoPE | Delta |
|------|-------------|-----------|-------|
| 1 | 6.932 | 6.932 | 0.000 |
| 10 | 5.771 | 5.771 | 0.000 |
| 100 | 3.396 | 3.367 | +0.029 (partial slightly behind) |
| 200 | 2.841 | 2.839 | +0.002 |
| 300 | 2.468 | 2.475 | -0.007 (partial catches up) |
| 400 | 2.324 | 2.331 | -0.007 |
| 500 | 2.456 | 2.465 | -0.009 |
| 600 | 2.505 | 2.515 | -0.010 |
| 700 | 2.402 | 2.411 | -0.009 |
| 800 | 2.252 | 2.257 | -0.005 |
| 900 | 2.299 | 2.303 | -0.004 |
| 1000 | 2.335 | 2.342 | -0.007 |

**Val BPB checkpoints**:

| Step | Partial RoPE | Full RoPE | Winner |
|------|-------------|-----------|--------|
| 0 | 4.105 | 4.105 | tie |
| 400 | 1.498 | 1.502 | Partial (-0.004) |
| 800 | 1.385 | 1.389 | Partial (-0.004) |

**Curve smoothness**: Both descend monotonically at val checkpoints. No instability. Train loss has mild shard-oscillation (step 500-600 bumps) which is normal. Both curves still descending at cutoff — learning is step-count-limited, not architecture-limited.

- **Hypothesis**: By encoding position in only 16 of 64 dims, the remaining 48 dims are free to learn purely semantic representations. This gives a slight edge that compounds over steps. The speed gain comes from less rotary computation per attention call. The advantage may grow with more steps on H100.
- **Action**: Partial RoPE is a confirmed free win. Include `ROPE_DIM=32` (or 16) in all future configs. Both curves still descending at cutoff confirms that maximizing per-step learning (bigger batch, full MHA) is the priority over feature toggles.

### Finding: LN Scale hurts at short step counts — it's a regularizer that penalizes underfitting
- **Experiment**: exp017 LN Scale (`LN_SCALE_ENABLED=1`) vs all other variants on 8xA40
- **Observation**: LN Scale finished last in every metric. val_bpb at step 400: 1.5151 (worst by 0.013+). Final INT8+zlib: 1.3916 (worst by 0.02). Also slower at 563 ms/step (vs 549-559 for others) and fewer total steps (1,066 vs 1,074-1,094). The `1/sqrt(layer_idx+1)` scaling dampens deeper layers: layer 10 only contributes 30% of its full strength. This stabilizes long training runs but starves the model when steps are scarce.
- **Hypothesis**: LN Scale is a regularizer. Regularizers prevent overfitting. But at 1,074 steps on 8B tokens, the model is heavily underfitting — it's seen <0.7% of the data. Regularizing an underfitting model makes it worse. LN Scale may help on H100 with 10,000+ steps where the model starts to overfit on repeated data, but on A40 it's actively harmful.
- **Action**: Do NOT include LN Scale in A40 configs. Revisit only on H100 runs with 5,000+ steps. This generalizes: any technique that acts as a regularizer (LN Scale, SWA, JEPA, dropout) should be tested on H100, not A40.

### Finding: Run comparison table (all exp017 variants, 8xA40, 600s wallclock)
- **Experiment**: all completed exp017 runs to date on A40 (same model family, same data, one dominant knob per run)
- **Observation**:

| Rank | Run | Key Change | Steps | ms/step | Float BPB | INT8+zlib BPB |
|------|-----|-----------|-------|---------|-----------|---------------|
| - | Buggy (non-causal SmearGate) | leaked future tokens | 1,072 | 560 | 0.0022 | 0.0022 |
| 1 | + Partial RoPE | `ROPE_DIM=16` | 1,094 | 549 | 1.3489 | **1.37108571** |
| 2 | + Late QAT | 6-bit QAT last 4% | 1,074 | 559 | 1.3480 | 1.37113245 |
| 3 | Causal fix (baseline) | SmearGate left-only | 1,074 | 559 | 1.3548 | 1.37856702 |
| 4 | + LN Scale | LN_SCALE_ENABLED=1 | 1,066 | 563 | 1.3675 | 1.3916 |
| 5 | + Batch 786K | `TRAIN_BATCH_TOKENS=786432` | 736 | 815 | 1.4149 | 1.48769516 |

Partial RoPE and Late QAT are effectively tied on A40 quant BPB, with Partial RoPE ahead by a hair and also the fastest run of the bunch. Batch scaling to `786432` tokens was the only severe regression outside the known SmearGate bug. SWA lands nearby but does not beat Partial RoPE.

**Val BPB at each checkpoint (all variants)**:

| Step | Partial RoPE | Late QAT | Causal Fix | LN Scale |
|------|-------------|----------|------------|----------|
| 0 | 4.105 | 4.105 | 4.105 | 4.105 |
| 400 | **1.498** | 1.494 | 1.502 | 1.515 |
| 800 | **1.385** | 1.381 | 1.389 | 1.400 |
| Final | 1.349 | **1.348** | 1.355 | 1.368 |

**Key takeaways**:
1. All non-buggy 524K-batch variants land in 1.34-1.39 float BPB and 1.37-1.39 quant BPB at ~1,070 steps
2. Partial RoPE and Late QAT are the only clear wins on A40 so far
3. LN Scale is the only clear loss (slower + worse at every checkpoint)
4. Bigger batch is a separate systems loss on A40, not a modeling win
5. The clean current A40 lane moved away from `KV8`; `exp018_ntk_sliding_eval_gqa` is the active NTK fairness test, and `exp017_partial_rope_ortho` is queued behind it

- **Action**: Keep `TRAIN_BATCH_TOKENS=524288` on A40. Treat `Partial RoPE` as the carry-forward default. The fair NTK test now requires sliding-window eval (`exp018_ntk_sliding_eval_gqa`), and the next low-cost follow-up is `OrthoInit` on the same base. Re-stack `Late QAT` later on the best architecture variant.

### Finding: Bigger batch (786K) loses badly on A40 — step count beats batch size
- **Experiment**: exp017 batch786 (`TRAIN_BATCH_TOKENS=786432`) vs baseline 524K, 8xA40
- **Observation**:

| Metric | 524K batch | 786K batch | Delta |
|--------|-----------|-----------|-------|
| Steps | 1,074 | 736 | -338 (31% fewer) |
| ms/step | 559 | 815 | +256 (46% slower) |
| Total tokens seen | 563M | 579M | +16M (+3% more) |
| VRAM/GPU | 22.7 GB | 33.6 GB | +10.9 GB |
| Float BPB (final) | 1.3548 | 1.4149 | +0.060 (worse) |
| INT8+zlib BPB | 1.3786 | 1.4877 | **+0.109 (much worse)** |

The 1.5x batch paid 46% more per step but only gained 3% more total tokens. The 31% fewer gradient updates devastated final BPB. At step 400, val_bpb was nearly identical (1.502 vs 1.502) — the batch saw 1.5x more tokens per step but the model didn't benefit because it was still in the high-learning-rate phase where more iterations matter more than gradient stability.

- **Hypothesis**: The model at ~1,074 steps is deeply underfitting (seen <0.7% of 8B tokens). In this regime, more gradient updates > stabler gradients. Bigger batch helps when you're near convergence and gradients are noisy — not when you're 10x away from convergence. On H100 with 10,000+ steps and approaching convergence, 786K batch (the SOTA config) likely does help. On A40 with 736 steps, it's pure waste.
- **Action**: **Keep 524K batch on A40.** Do NOT increase batch size. The VRAM headroom should go to full MHA (+0.8M params, negligible step time cost) not bigger batch. Reserve 786K batch for H100 runs where step count isn't the bottleneck. Updated `experiments/next-run-config.md`.

### Finding: Current A40 loop should stay architecture-first after batch786 failed
- **Experiment**: synthesis of all completed exp017 ablations plus current queued architecture tests
- **Observation**: The clean A40 plan is no longer "use more batch because VRAM is free." It is "keep the fast 524K regime, carry forward Partial RoPE, and test attention capacity plus length handling before recombining more tricks."

| Feature | Verdict | Why |
|---------|---------|-----|
| Causal SmearGate | **KEEP** | Prerequisite — fixes the leak, 0 cost |
| BigramHash | **KEEP** | Free local context, helps early steps |
| Partial RoPE (16/64) | **KEEP** | Best or tied-best quant BPB, fastest run |
| Late QAT (6-bit, 4%) | **KEEP LATER** | Small real quantization win, but architecture signal comes first |
| KV8 / full MHA | **SKIP FOR NOW** | Lost to simpler GQA-based variants on A40 |
| NTK-RoPE | **TEST WITH SLIDING EVAL** | Only meaningful when eval context exceeds train length |
| LN Scale | **SKIP** | Regularizer, hurts underfitting A40 runs |
| Bigger batch (786K) | **SKIP** | 46% slower steps, 31% fewer steps, worse BPB |
| SWA | **KEEP AS MODEST WIN** | Small real improvement, but not best-in-class on A40 |
| JEPA / AttnRes | **LATER** | Research lane after the conventional stack is cleaner |

- **Action**: the earlier `KV8 -> KV8+NTK` queue note is now historical only. `KV8` finished weaker than the best Partial-RoPE family, `KV8+NTK` was interrupted before a clean read, `Partial RoPE + NTK` on the 4-KV base was only a fair test once sliding eval existed, and the live branch is now `exp018_ntk_sliding_eval_gqa`.

### Finding: KV8 is slower and slightly worse than the simpler Partial-RoPE carry-forward on A40
- **Experiment**: `exp017_partial_rope_kv8`
- **Observation**: the 8xA40 run finished `1044` steps in `600.198s` at `574.90ms/step` with `final_int8_zlib_roundtrip_exact val_bpb 1.37748001`. That is slower and worse than the earlier `Partial RoPE` carry-forward (`1.37108571`) despite the extra KV capacity.
- **Hypothesis**: on the A40's 600-second underfit regime, the added attention cost from `NUM_KV_HEADS=8` hurts step count more than it helps representation quality.
- **Action**: do not treat `KV8` as the new default A40 lane. Keep it logged as a completed branch, but carry the faster 4-KV `Partial RoPE` family forward.

### Finding: NTK-aware RoPE on the 4-KV Partial-RoPE base is a near-tied A40 winner
- **Experiment**: `exp017_partial_rope_ntk_gqa`
- **Observation**: the run finished `1093` steps in `600.164s` at `549.10ms/step` with `step 400 val_bpb 1.4982`, `step 800 val_bpb 1.3855`, and `final_int8_zlib_roundtrip_exact val_bpb 1.37173728`. That is essentially tied with the best A40 numbers while preserving the faster 4-KV path.
- **Hypothesis**: NTK-aware rotary scaling gives a small quality gain without paying the heavier per-step tax that `KV8` incurred on A40.
- **Action**: treat `Partial RoPE + NTK` on the 4-KV base as the cleaner A40 carry-forward branch. Test late-stage hooks like `SWA`, `OrthoInit`, or `Late QAT` on top of this family before revisiting `KV8`.

### Finding: KV8 + NTK is unresolved because the run was interrupted
- **Experiment**: `exp017_partial_rope_kv8_ntk`
- **Observation**: the run only reached `step 300` before `torchrun` exited on `SIGTERM` at `23:19 UTC` on `2026-03-21`. It never produced a clean 600-second result or final validation metric.
- **Hypothesis**: the job was preempted, superseded, or manually terminated before it reached a comparable checkpoint, so the architecture itself is still unmeasured.
- **Action**: mark `KV8+NTK` as interrupted instead of queued/current in the vault. Only compare it after a clean rerun.

### Finding: NTK without sliding eval is not a fair verdict
- **Experiment**: `exp017_partial_rope_ntk_gqa` versus `exp018_ntk_sliding_eval_gqa`
- **Observation**: the fixed-length `exp017_partial_rope_ntk_gqa` run only validated on `TRAIN_SEQ_LEN=1024` windows, so it did not actually exercise NTK's longer-context behavior. The `exp018_ntk_sliding_eval_gqa` copy adds `EVAL_SEQ_LEN=2048` and `EVAL_STRIDE=64` so NTK is tested with longer context in the evaluation loop.
- **Hypothesis**: NTK only matters once the eval context exceeds the training context. Without sliding eval, it can look like a no-op even if the implementation is correct.
- **Action**: use `exp018_ntk_sliding_eval_gqa` as the real NTK verdict and stop treating the fixed-length `exp017_partial_rope_ntk_gqa` result as conclusive.

## Template

### Finding: [title]
- **Experiment**: expXXX
- **Observation**: what happened
- **Hypothesis**: why
- **Action**: what to try next

## See also

- [[Parameter Golf Experiment Framework]]
- [[leaderboard]]
