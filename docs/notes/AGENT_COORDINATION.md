# Agent Coordination — Parameter Golf Experiments

**This file is the shared state for all agents working on Parameter Golf.**
Any agent (Claude Code, Codex, OpenCode, etc.) should read this before starting work and update it after completing work.

## Agent Roster

| Agent Name | Role | Notes |
|---|---|---|
| Claude Code | orchestrator / VM runner | currently driving baseline bring-up and ROCm patches |
| Codex Relay | coordination / integration | keeps vault state, shared task board, and handoffs aligned; currently normalizing the RunPod A40 state |

## Collaboration Loop

All agents should operate in visible short loops:

1. Read this file and `experiments/task-board.md`
2. Check `Running Now` and claimed work
3. Claim one bounded task
4. Execute
5. Update shared files with a one-line result or blocker
6. Record to memory store when possible
7. Repeat

If memory store thread `T-F9ZTX1` is unavailable from a given session, agents should continue using the shared text files as the authoritative fallback layer.

---

## Memory Store Thread
- **Thread ID**: `T-F9ZTX1` (VM setup + experiments)
- **Research thread**: `T-GAW51Y` (architecture + strategy)
- **Active accessible fallback**: `T-QC6YRP`
- All agents SHOULD try `memory_store_recall` with thread `T-F9ZTX1` before starting experiment work
- If `T-F9ZTX1` is unavailable, continue with `T-QC6YRP` plus these shared markdown files
- All agents SHOULD call `memory_store_record` after significant findings

## Compute Resources

### RunPod 8x A40 (PRIMARY — serious experiments)
```
SSH: ssh runpod
Alt: ssh runpod-proxy
Current pod: `pgolf-8xA40` (`ukp4lcxzv2ukc3`)
NOTE: SPOT INSTANCE — IP/port may change if preempted. Check `~/.ssh/config` for the latest live endpoint.
Key: ~/.ssh/id_ed25519 (passphrase: a3fckx)
GPU: 8x NVIDIA A40 (48GB each, 384GB total)
Template image: `runpod/parameter-golf:latest`
Stack: Native CUDA, PyTorch `2.9.1+cu128`, `torchrun --standalone --nproc_per_node=8`
Current paths: `/workspace/parameter-golf`, `/workspace/experiments`, `/workspace/fair_runs`
Current launch caveat: healthy 8-GPU DDP on this pod requires `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1`
Current observed speed on `exp017_meta_stack_core`: ~`560ms/step`
Compute equivalent: substantially slower than 8xH100; use A40 runs for clean reproduction and stack ablations, not direct H100 throughput expectations
```

### MI300X VM (SECONDARY — code testing, Codex background)
```
SSH: ssh mi300x  (hotaisle@23.183.40.75)
Key: ~/.ssh/id_ed25519 (passphrase: a3fckx)
GPU: 1x AMD MI300X (205.8 GB VRAM)
Stack: Docker rocm/pytorch:rocm7.2 (torch.compile works)
Status: background code-testing box; treat older MI300X runs as historical unless explicitly re-checked
Speed reference: 736ms/step → 816 steps in 600s
```

### Common
```
Data: ~/parameter-golf/data/datasets/fineweb10B_sp1024 (16GB)
Phase 3 code: ~/experiments/phase3/{stp_lite,span_jepa,cross_layer_jepa}/train.py
Results: ~/experiments/ on VM, experiments/ in vault
```

## Current Strategy (3 Phases)
See [[Parameter Golf Goal Definition]] for full details.
- **Phase 1**: Reproduce proven meta stack → ~1.125 BPB baseline
- **Phase 2**: High-value untested techniques (QK-Norm, STP-lite, Backout, AttnRes, Adaptive Quant)
- **Phase 3**: LLM-JEPA adaptation (span-JEPA, JEPA-lite, cross-layer JEPA) — our research differentiator

## Experiment Queue

### Running Now
| Experiment | Agent | Started | Status |
|-----------|-------|---------|--------|
| exp018_ntk_sliding_eval_gqa | Codex Relay | 2026-03-22 | active on RunPod at `/workspace/fair_runs/exp018_ntk_sliding_eval_gqa/full_log_exp018_ntk_sliding_eval_gqa.txt`; launched from `train.py` with `ROPE_DIM=16`, `NUM_KV_HEADS=4`, `NTK_ROPE_ENABLED=1`, `EVAL_SEQ_LEN=2048`, `EVAL_STRIDE=64`, `EVAL_MAX_WINDOWS=2048`; healthy 8-GPU launch uses `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1`; this is the first fair NTK sliding-eval test on the 4-KV base |

Recent finished A40 follow-ups:
- `exp017_partial_rope_swa` finished cleanly at `final_int8_zlib_roundtrip_exact val_bpb 1.37406320`
- `exp017_partial_rope_kv8` finished cleanly at `final_int8_zlib_roundtrip_exact val_bpb 1.37748001`
- `exp017_partial_rope_ntk_gqa` finished cleanly at `final_int8_zlib_roundtrip_exact val_bpb 1.37173728`
- `exp017_partial_rope_kv8_ntk` was interrupted by `SIGTERM` at `step 300`, so it is not rankable yet

### Phase 1 Exclusive Batch
| Order | Experiment | Change from baseline | Duration | Status |
|----------|-----------|---------------------|----------|----------|
| 1 | exp001_11L_3xMLP_clean | 11 layers, 3x MLP | 600s | complete |
| 2 | exp002_xsa4 | Add XSA on last 4 layers | 600s | complete, but used a slow manual-mask attention path and needs replacement |
| 3 | exp003_ema_clean | Add EMA (decay=0.997) | 600s | complete, not promising enough to promote first |
| 4 | exp004_partial_rope_clean | Partial RoPE (16/64 dims) | 600s | complete, highly promising |
| 5 | exp005_ln_scale_clean | LN Scale (1/sqrt(layer+1)) | 600s | paused behind promotion shift |
| 6 | exp006_smeargate_clean | Add SmearGate | 600s | paused behind promotion shift |
| 7 | exp007_bigramhash_clean | Add BigramHash (2048) | 600s | paused behind promotion shift |
| 8 | exp008_late_qat_clean | Late QAT (6-bit, last 4% of run) | 900s | paused behind promotion shift |
| 9 | exp002_xsa4_clean | XSA rerun with shifted-SDPA fast path | 600s | still needed, but treat as a promotion candidate rather than just another short probe |

### Phase 1 Promotion Queue
| Priority | Experiment | Why promote | Duration | Status |
|----------|-----------|-------------|----------|--------|
| 1 | baseline_rocm72_container_long | Control run for longer-horizon comparison | 1800s | pending |
| 2 | exp001_11L_3xMLP_promo | Best exclusive Phase 1 variant so far (`1.4247`) | 1800s | pending |
| 3 | exp004_partial_rope_promo | Promoted: clean rerun landed `1.4000 / 1.4032` at full baseline-class throughput | 1800s | historical MI300X promotion note; not current live work |
| 4 | exp002_xsa4_clean | Patched shifted-SDPA rerun to get an unconflated XSA read | 1800s | pending after current run |

### Phase 2 Queue (after Phase 1 baseline established)
| Priority | Experiment | Change | Assigned |
|----------|-----------|--------|----------|
| 1 | exp009_ntk_rope | NTK-aware RoPE (dynamic base scaling for length extrapolation) | unassigned |
| 1a | exp009_ntk_rope_ablation | NTK-RoPE ablation: train=1024/eval=1024 vs train=1024/eval=2048 | unassigned |
| 2 | exp010_qknorm | QK-Norm + Z-loss | unassigned |
| 3 | exp011_stp_005 | STP-lite lambda=0.005 | unassigned |
| 4 | exp012_stp_01 | STP-lite lambda=0.01 | unassigned |
| 5 | exp013_stp_02 | STP-lite lambda=0.02 | unassigned |
| 6 | exp014_backout | Backout (learned residual subtraction) | unassigned |
| 7 | exp015_attnres | Attention Residuals | unassigned |
| 8 | exp016_adaptive_quant | Gradient-Guided Adaptive Quant | unassigned |

### Phase 3 Queue (JEPA research bet)
| Priority | Experiment | Change | Assigned |
|----------|-----------|--------|----------|
| 1 | exp020_span_jepa | Span-JEPA (predict masked span embedding) | unassigned |
| 2 | exp021_jepa_lite | JEPA-lite (predict future hidden state) | unassigned |
| 3 | exp022_cross_layer_jepa | Cross-layer JEPA (shallow predicts deep) | unassigned |
| 4 | exp023_best_jepa_combo | Best JEPA + best Phase 2 config | unassigned |

## Completed Experiments
| Experiment | val_bpb | Change | Date | Key Finding |
|-----------|---------|--------|------|-------------|
| baseline_eager | 1.9603 | Initial (eager, no compile) | 2026-03-21 | 251 steps/600s at 3.4s/step — too slow |
| baseline_rocm72_container | 1.3971 | Official ROCm 7.2 / PyTorch 2.10 container | 2026-03-21 | 816 steps/600s at 736.73ms/step; quantized `val_bpb=1.4005`; this is the new reference baseline |
| exp001_11L_3xMLP | 1.5123 | 11 layers, 3x MLP, exploratory swarm run | 2026-03-21 | 26.5M params; reached step 406/20000 under shared GPU load and logged float `val_bpb=1.5123` |
| exp001_11L_3xMLP_clean | 1.4247 | 11 layers, 3x MLP, exclusive rerun | 2026-03-21 | 26.5M params; 606 steps/600s at 992.47ms/step; much stronger than the contended swarm reading |
| exp002_xsa4 | 1.5011 | XSA on last 4 layers, exclusive run | 2026-03-21 | 17.1M params; 481 steps/600s at 1252.01ms/step; used manual `matmul + mask + softmax`, so this result is confounded by a slower attention implementation rather than XSA alone |
| exp003_ema | 2.2755 | EMA(0.997), exploratory swarm run | 2026-03-21 | reached step 416/20000 under shared GPU load; quantized `val_bpb=2.2959`; result is strongly confounded by parallel contention |
| exp003_ema_clean | 1.4870 | EMA(0.997), exclusive rerun | 2026-03-21 | 815 steps/600s at 737.3ms/step; cleaner than the swarm read, but still behind baseline and `11L_3xMLP_clean` |
| exp004_partial_rope | 1.5973 | Partial RoPE (16/64 dims), exploratory swarm run | 2026-03-21 | reached step 417/20000 under 2-way shared GPU load; final captured int8 roundtrip `val_bpb=1.5973` looks promising for a follow-up rerun |
| exp004_partial_rope_clean | 1.4000 | Partial RoPE (16/64 dims), exclusive rerun | 2026-03-21 | 821 steps/600s at 731.81ms/step; nearly baseline-level quality and throughput, so this is now the top Phase 1 promotion candidate |
| exp005_ln_scale | 1.6751 | LN Scale (1/sqrt(layer+1)), exploratory swarm run | 2026-03-21 | reached step 414/20000 under 2-way shared GPU load; final captured int8 roundtrip `val_bpb=1.7163` |

## Live Run Snapshot (2026-03-22)

- Stable mirrored path: `/workspace/fair_runs/exp017_meta_stack_core/train.py`
- Active pod path: `/workspace/fair_runs/exp017_meta_stack_core/train_next_feature_hooks.py`
- Active log: `/workspace/fair_runs/exp017_meta_stack_core/full_log_partial_rope_swa.txt`
- Active launch recipe: `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1 torchrun --standalone --nproc_per_node=8 train_next_feature_hooks.py`
- Reason for flags: on this A40 pod, a tiny 8-GPU DDP smoke test reached `init_process_group()` but hung on the first `all_reduce()` until both flags were set
- Status at save time: `exp018_ntk_sliding_eval_gqa` is the active run; `exp017_partial_rope_swa` finished at `1.37406320`; queued follow-up is `exp017_partial_rope_ortho`
- GPU state at save time: all 8 GPUs at `100%`, ~`22.9 GiB` used each
- Earlier queue note is now stale: `exp017_partial_rope_kv8` and `exp017_partial_rope_ntk_gqa` already completed, while `exp017_partial_rope_kv8_ntk` was interrupted before a clean comparison point

## External Intelligence — PR #369 (2026-03-22)

**Source**: [openai/parameter-golf#369](https://github.com/openai/parameter-golf/pull/369) — signalrush  
**Score**: 1.1328 BPB (3-seed mean) | 15.87 MB | 10,300+ steps on 8xH100 SXM

### Key Finding: FlashAttention 3 + NTK-aware RoPE

**FlashAttention 3**: Hopper-specific (H100 only), achieves **58ms/step** vs 99ms/step standard SDPA  
→ **71% more training steps** in same 600s budget (10,300 vs 6,000 steps)

**NTK-aware RoPE**: Dynamic base frequency scaling for length extrapolation  
- Scales RoPE base when `seq_len > train_seq_len`  
- Formula: `base = base * (seq_len / train_seq_len)^(1/dim)`  
- At train=1024, eval=2048: ~4x base scaling  
- **Zero extra parameters** — pure algorithmic improvement  
- Works on ANY hardware (A40, H100, MI300X)  
- Critical for sliding window eval (stride=64) which uses longer sequences

### PR #369 Architecture Stack
- 11L, 512d, 8H/4KV, MLP 3x
- SmearGate + BigramHash(4096) + OrthoInit + muP  
- NTK-aware RoPE + logit softcap=30  
- Muon (lr=0.025) + AdamW  
- WD=0.04, warmdown=3000  
- Int5 MLP / Int6 attn / Int8 embed + zstd-22  
- XSA on last 4 layers  
- EMA (decay=0.997)

### Implications for Our Experiments
1. **Test NTK-aware RoPE immediately on A40s** — hardware-agnostic, high upside  
2. **FA3 is H100-only** — defer to final submission hardware  
3. **Mixed int5/int6/int8 quantization** — more granular than our current uniform int6  
4. **Step time matters**: 58ms vs 99ms is massive — any A40 technique must be throughput-neutral or positive

## NTK-RoPE Experiment Plan

### Why Test This First
NTK-aware RoPE is the **highest-value, lowest-risk** technique from PR #369:
- Zero parameter cost (pure algorithmic change)
- Works on A40 (no H100 required)
- Enables proper sliding window evaluation
- Used by #1 competitive submission

### Proposed Test Matrix

| Experiment | Config | Train Seq | Eval Seq | Expected BPB | Purpose |
|------------|--------|-----------|----------|--------------|---------|
| exp009_ntk_rope_baseline | Standard RoPE | 1024 | 1024 | ~1.40 | Control (our current best) |
| exp009_ntk_rope_long | NTK-RoPE | 1024 | **2048** | ~1.38-1.39 | Test length extrapolation |
| exp009_ntk_rope_ablation | NTK-RoPE | 1024 | 1024 | ~1.40 | Verify no regression at train length |

**Key Question**: Does NTK-RoPE improve BPB when eval uses longer sequences (sliding window stride=64)?

### Integration with Existing Stack
Once validated, NTK-RoPE should be **added to ALL subsequent experiments**:
- Phase 2 queue (QK-Norm, Backout, AttnRes)
- Phase 3 JEPA experiments (evaluates at longer sequences)
- Final H100 submission (enables proper sliding window)

### Implementation Notes
- Modify `Rotary` class in `train_gpt.py`
- Dynamic base calculation: `base * (seq_len / train_seq_len) ** (1/dim)`
- Apply only during eval when `seq_len > train_seq_len`
- Zero training overhead (same speed as standard RoPE)

### Experiment Files Created
```
experiments/phase2/exp009_ntk_rope/
├── train.py          # Full model with NTK-RoPE implementation
├── config.json       # Experiment configuration
└── README.md         # Documentation and usage guide
```

### How to Run

**On RunPod 8x A40:**
```bash
cd /workspace/parameter-golf

# Option 1: Copy and run directly
cp ~/vault/experiments/phase2/exp009_ntk_rope/train.py ./exp009_train.py
NTK_ROPE_ENABLED=1 TRAIN_SEQ_LEN=1024 torchrun --standalone --nproc_per_node=8 exp009_train.py

# Option 2: Use baseline with NTK env vars
NTK_ROPE_ENABLED=1 \
TRAIN_SEQ_LEN=1024 \
NUM_LAYERS=11 \
MLP_MULT=3 \
torchrun --standalone --nproc_per_node=8 train_gpt.py
```

**Environment Variables:**
- `NTK_ROPE_ENABLED=1` - Enable NTK scaling
- `TRAIN_SEQ_LEN=1024` - Training sequence length
- `NTK_SCALE_EXPONENT=0.0` - Auto (1/dim) or manual override

### Success Criteria
- **Target**: Match or beat `exp004_partial_rope_clean` (1.4000 BPB)
- **Validation**: Test with sliding window eval (stride=64, seq_len=2048)
- **Next Step**: If successful, integrate into ALL subsequent experiments

### Which Experiments Should Use NTK-RoPE

**Immediately test on:**
1. ✅ **exp009_ntk_rope** (this experiment) - validate the technique
2. ✅ **exp010_qknorm** - NTK-RoPE + QK-Norm
3. ✅ **exp014_backout** - NTK-RoPE + Backout
4. ✅ **exp015_attnres** - NTK-RoPE + Attention Residuals

**All Phase 3 experiments:**
- ✅ exp020_span_jepa - JEPA benefits from longer context
- ✅ exp021_jepa_lite - Hidden state prediction at multiple scales
- ✅ exp022_cross_layer_jepa - Cross-layer with extrapolated positions

**Final submission stack:**
- ✅ Must include NTK-RoPE for proper sliding window evaluation
- ✅ Enables 2048-token eval on 1024-trained model

## Artifact Sync Rule

- The VM is the live execution surface: `~/parameter-golf/`, `~/experiments/`, and active Docker containers
- RunPod currently uses `/workspace/parameter-golf` and `/workspace/experiments`, not the older `~/experiments` layout
- The local vault `experiments/` folder is the human-readable mirror and promotion layer
- If `phase1/`, `phase2/`, or `phase3/` looks empty locally, that means no run has been synced there yet, not that no experiment work exists
- After a completed run, sync the exact training snapshot, `log.txt`, and `result.json` into the appropriate local phase folder
- Preferred sync path for the new exclusive batch is [sync-vm-phase1-artifacts.sh](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/sync-vm-phase1-artifacts.sh)

## Parallel Swarm Policy

- Parallel exploratory runs on the single MI300X are intentional during the swarm phase
- GPU contention is acceptable when the goal is directional learning signal and high experiment throughput
- Compare experiments within the same concurrency bucket when possible, rather than against exclusive-run wallclock numbers
- Reserve exclusive single-run comparisons for promotion or final confirmation only
- Do not let sequential-runner suggestions override direct user intent for swarm experimentation
- Expect step time to stretch under swarm load because compute is shared: the clean container baseline averaged about `736ms/step`, while the contended Phase 1 runs landed closer to `1.39-1.74s/step`
- XSA currently needs special care: the first exclusive `exp002_xsa4` run fell off the fast ROCm attention path because it materialized the full score matrix for the exclude-self mask; use the shifted-SDPA rerun (`exp002_xsa4_clean`) as the fair follow-up
- New default: once a variant looks promising, promote it to a longer run before burning more GPU time on weak 600s probes
- Promotion defaults: `1800s` for stronger compare runs, `3600s` only for finalists we think could beat the board-facing baseline

## How To Run An Experiment

Immediate note: until further notice, use the live ROCm path in [[program|program.md]]. The current authoritative harness is patched `~/parameter-golf/train_gpt.py` inside the official ROCm container, not `uv run` inside `~/autoresearch`.

### For Any Agent
Preferred execution is the containerized pattern in [[program|program.md]]. The host `python3` example below is a fallback path, not the default.

```bash
# 1. SSH into VM
ssh mi300x

# 2. Create experiment directory
mkdir -p ~/experiments/exp001_muon
cp ~/parameter-golf/train_gpt.py ~/experiments/exp001_muon/train.py

# 3. Modify train.py with your specific change
# (make ONE change at a time)

# 4. Run training from the repo root so data paths resolve correctly
cd ~/parameter-golf
timeout 360 python3 ~/experiments/exp001_muon/train.py 2>&1 | tee ~/experiments/exp001_muon/log.txt

# 5. Extract val_bpb from log
grep "val_bpb" ~/experiments/exp001_muon/log.txt | tail -1

# 6. Save config
echo '{"experiment": "exp001_muon", "change": "Added Muon optimizer", "val_bpb": <score>}' > ~/experiments/exp001_muon/result.json
```

### For Parallel Runs (4-8 at once)
```bash
# Each uses ~3GB of 192GB VRAM. Run from the repo root and write into separate experiment folders:
cd ~/parameter-golf
timeout 360 python3 ~/experiments/exp011_stp_005/train.py 2>&1 | tee ~/experiments/exp011_stp_005/log.txt &
timeout 360 python3 ~/experiments/exp012_stp_01/train.py 2>&1 | tee ~/experiments/exp012_stp_01/log.txt &
timeout 360 python3 ~/experiments/exp013_stp_02/train.py 2>&1 | tee ~/experiments/exp013_stp_02/log.txt &
timeout 360 python3 ~/experiments/exp014_backout/train.py 2>&1 | tee ~/experiments/exp014_backout/log.txt &
wait  # all 4 finish in ~8 min
```

### After Each Experiment
1. Update this file: move experiment from "Running" to "Completed"
2. Update `experiments/leaderboard.md` in vault
3. Record finding to memory store: `memory_store_record(content="...", thread_id="T-F9ZTX1")`
4. If val_bpb improved: note what worked and why in `experiments/insights.md`
5. Sync the promoted run artifacts back into the local vault phase folder

## Agent Rules
1. **ONE change per experiment** — never stack multiple untested changes
2. **Always read this file first** — check what's running, what's done, what's next
3. **Claim before running** — update "Assigned" column before starting
4. **Report after finishing** — update Completed table, leaderboard, memory store
5. **Don't duplicate work** — if another agent claimed it, pick the next one
6. **Use the mode-appropriate `val_bpb`** — tiny-slice for dev-fast, medium-slice for compare, full quantized val for promotion/final
7. **Save the train.py snapshot** — exact code that ran, not just the diff
8. **ROCm compatibility** — replace any nvidia-smi with rocm-smi, test CUDA kernels work on ROCm

## Key Reference Notes
- [[program|program.md]] — live execution contract for agents
- [[Parameter Golf Goal Definition]] — full strategy, 3-phase plan, risk assessment
- [[Parameter Golf Experiment Framework]] — infrastructure design, parallel execution
- [[Parameter Golf Architecture Diagram]] — what each component does
- [[Parameter Golf JEPA Architecture Approach]] — JEPA/STP theory
- [[Parameter Golf Fundamentals]] — what parameters are, budget math
- [[JEPA-lite]] — JEPA-lite architecture and loss function
- [[Semantic Tube Prediction]] — STP-lite loss function
- [[Muon]] — optimizer details
- [[Attention Residuals]] — AttnRes architecture
- [[Multi-Token Prediction]] — MTP design
- [[QK-Norm and Z-Loss]] — training stability

## Repository & Code Reference

### Repo Structure (RunPod: /workspace/parameter-golf)
```
parameter-golf/
├── train_gpt.py              ← THE file. ~1100 lines. Model + optimizer + training loop
├── train_gpt_mlx.py          ← Apple Silicon version (not used)
├── requirements.txt           ← sentencepiece, tiktoken, datasets, etc.
├── data/
│   ├── cached_challenge_fineweb.py   ← download script
│   ├── datasets/fineweb10B_sp1024/   ← 81 shards (80 train + 1 val), 16GB total
│   └── tokenizers/fineweb_1024_bpe.model
├── records/                   ← other people's submissions
│   ├── track_10min_16mb/
│   └── track_non_record_16mb/
└── logs/                      ← internal logs (one per run, named by UUID)
```

### RunPod Template Quick Start
The new RunPod template already includes Python and dependencies:

```bash
cd /workspace
git clone https://github.com/openai/parameter-golf.git
cd parameter-golf

# full validation + 80 train shards by default
python3 data/cached_challenge_fineweb.py --variant sp1024

# smaller iteration subset if needed
python3 data/cached_challenge_fineweb.py --variant sp1024 --train-shards 1
```

Single-GPU example from the template:

```bash
RUN_ID=baseline_sp1024 \
DATA_PATH=./data/datasets/fineweb10B_sp1024/ \
TOKENIZER_PATH=./data/tokenizers/fineweb_1024_bpe.model \
VOCAB_SIZE=1024 \
torchrun --standalone --nproc_per_node=1 train_gpt.py
```

Notes:

- `train_gpt.py` keeps its ~10 minute wallclock cap by default
- use `MAX_WALLCLOCK_SECONDS=0` for no cap, or a larger value like `1800` for promotion runs
- use `VAL_LOSS_EVERY=200` if you want periodic validation during training
- the template target is roughly `~1.2` final `val_bpb` with a compressed artifact under `16MB`

### Model Architecture (in train_gpt.py)
```
Classes:
  GPT              — full model: embeddings → blocks → head
  Block             — one transformer layer: attn_norm → attn → MLP
  CausalSelfAttention — Q/K/V projections, RoPE, SDPA, output proj
  MLP               — CastedLinear up → ReLU² → CastedLinear down
  RMSNorm           — root mean square normalization
  CastedLinear      — Linear that casts to bfloat16 in forward
  Rotary            — RoPE position encoding
  Muon              — spectral-norm optimizer (Newton-Schulz)

Forward pass:
  tokens → embed → [Block × num_layers] → final_norm → lm_head → logits
  Each Block: x = x + attn(norm(x)) → x = x + mlp(norm(x))
```

### All Environment Variables (configure without editing code)
```
# MODEL SHAPE
NUM_LAYERS=9          # transformer depth (try: 9, 11, 13)
MODEL_DIM=512         # hidden dimension
NUM_HEADS=8           # attention heads
NUM_KV_HEADS=4        # KV heads for GQA (4 = 2:1 GQA)
MLP_MULT=2            # MLP expansion ratio (try: 2, 3, 4)
VOCAB_SIZE=1024       # vocabulary size (try: 1024, 2048, 4096)
TIE_EMBEDDINGS=1      # share input/output embeddings
ROPE_BASE=10000.0     # RoPE base frequency
LOGIT_SOFTCAP=30.0    # logit capping
QK_GAIN_INIT=1.5      # QK attention gain initialization

# TRAINING
MAX_WALLCLOCK_SECONDS=600   # training time limit
TRAIN_BATCH_TOKENS=524288   # tokens per step (all GPUs combined)
TRAIN_SEQ_LEN=1024          # sequence length
ITERATIONS=20000            # max steps (wallclock usually stops first)
WARMUP_STEPS=20             # LR warmup steps
WARMDOWN_ITERS=1200         # LR cooldown steps

# OPTIMIZER (Muon + AdamW)
MATRIX_LR=0.04              # Muon LR for weight matrices
SCALAR_LR=0.04              # AdamW LR for biases/norms
EMBED_LR=0.6                # AdamW LR for embeddings
HEAD_LR=0.008               # LR for LM head (if untied)
TIED_EMBED_LR=0.05          # LR for tied embed/head
MUON_MOMENTUM=0.95          # Muon momentum
MUON_BACKEND_STEPS=5        # Newton-Schulz iterations
GRAD_CLIP_NORM=0.0          # gradient clipping (0=disabled)

# VALIDATION
VAL_LOSS_EVERY=1000         # validate every N steps
VAL_BATCH_SIZE=524288       # validation batch size
TRAIN_LOG_EVERY=200         # log train loss every N steps

# RUNTIME
SEED=1337                   # random seed
RUN_ID=<uuid>               # log file name
DATA_PATH=./data/datasets/fineweb10B_sp1024
TOKENIZER_PATH=./data/tokenizers/fineweb_1024_bpe.model
```

### How To Run Experiments On RunPod

```bash
# BASELINE (9L, 2x MLP):
cd /workspace/parameter-golf
torchrun --standalone --nproc_per_node=8 train_gpt.py

# PHASE 1 — change architecture via env vars:
NUM_LAYERS=11 MLP_MULT=3 \
torchrun --standalone --nproc_per_node=8 train_gpt.py

# PHASE 1 — change vocab:
VOCAB_SIZE=2048 \
torchrun --standalone --nproc_per_node=8 train_gpt.py

# PHASE 1 — wider model:
MODEL_DIM=576 \
torchrun --standalone --nproc_per_node=8 train_gpt.py

# PHASE 3 — novel losses (use modified train.py):
STP_LAMBDA=0.01 \
torchrun --standalone --nproc_per_node=8 \
  /workspace/experiments/phase3/stp_lite/train.py

JEPA_LAMBDA=0.01 \
torchrun --standalone --nproc_per_node=8 \
  /workspace/experiments/phase3/span_jepa/train.py

JEPA_LAMBDA=0.01 JEPA_SOURCE_LAYER=4 \
torchrun --standalone --nproc_per_node=8 \
  /workspace/experiments/phase3/cross_layer_jepa/train.py

# LONGER RUNS (for grokking / convergence testing):
MAX_WALLCLOCK_SECONDS=1800 \
torchrun --standalone --nproc_per_node=8 train_gpt.py

# SAVE FULL LOG:
RUN_ID=exp_name VAL_LOSS_EVERY=200 \
torchrun --standalone --nproc_per_node=8 train_gpt.py \
2>&1 | tee /workspace/experiments/phase1/exp_name/full_log.txt
```

### RunPod Utilities
Useful built-ins from the template:

```bash
# send a file from the pod
runpodctl send model_checkpoint.pt

# receive locally
runpodctl receive <code>
```

Ports exposed by the template:

- `22/tcp` SSH
- `8888/http` Jupyter Lab
- `3000/http` free for dashboards or ad hoc services

RunPod agent skill reference:

```bash
npx skills add https://github.com/runpod/skills --skill runpodctl
```

This is optional, but useful if we want agent-driven pod lifecycle management instead of treating SSH config as the only control path.

### Phase 3 Modified train.py Files (on RunPod)
```
/workspace/experiments/phase3/stp_lite/train.py
  Added: stp_loss() function, STP_LAMBDA env var
  Zero extra parameters. Regularizes hidden trajectory smoothness.

/workspace/experiments/phase3/span_jepa/train.py
  Added: JEPAPredictor class, span_jepa_loss(), JEPA_LAMBDA & JEPA_SPAN_LEN env vars
  ~262K predictor params (DISCARDED at inference, not in 16MB artifact)

/workspace/experiments/phase3/cross_layer_jepa/train.py
  Added: JEPAPredictor class, cross_layer_jepa_loss(), JEPA_LAMBDA & JEPA_SOURCE_LAYER env vars
  Captures hidden states at source layer and final layer.
  ~262K predictor params (DISCARDED at inference)
```

### 16MB Budget Quick Reference
```
Baseline (9L, 2x):  17.1M params → ~7.5 MB INT6+zstd  (8.5 MB headroom)
Meta (11L, 3x):     26.5M params → ~11.6 MB            (4.4 MB headroom)
12L + adaptive:     ~29M params  → ~15.8 MB             (0.2 MB headroom)
Budget limit:                      16.0 MB
```

### Performance Reference
```
8x A40 (RunPod):     180-200 ms/step → ~3,000 steps in 600s
1x MI300X (Docker):  736 ms/step     → ~816 steps in 600s
8x H100 (competition): ~150 ms/step  → ~4,000 steps in 600s

Competition-equivalent on A40: set MAX_WALLCLOCK_SECONDS=1800 (~30 min)
```

## 2026-03-22 Coordination Snapshot

- Repo-native RunPod launch wrappers confirmed: `/workspace/parameter-golf/experiments/run_all.sh`, `/workspace/parameter-golf/experiments/exp0*/run.sh`, `/workspace/parameter-golf/run_fastest_path.sh`
- Important repo caveat: `exp03`, `exp04`, and `exp05` still document that XSA, Partial RoPE/LN Scale, and true gradient-guided quant are not yet implemented in `train_gpt_sota.py`
- Current A40 pod failure mode reproduced with a tiny 8-GPU DDP smoke test: `init_process_group()` works, first collective hangs unless `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1`
- Current live run: `/workspace/fair_runs/exp018_ntk_sliding_eval_gqa/full_log_exp018_ntk_sliding_eval_gqa.txt`
- Current live status at save time: NTK sliding-eval run is active with `ROPE_DIM=16`, `NUM_KV_HEADS=4`, `EVAL_SEQ_LEN=2048`, and `EVAL_STRIDE=64`; `exp017_partial_rope_swa` already finished at `1.37406320`

## Last Updated
2026-03-22 05:40 IST by Codex Relay — refreshed the A40 queue to `exp018_ntk_sliding_eval_gqa`, recorded `exp017_partial_rope_swa` as finished, and cleaned up the stale KV8/SWA queue notes
