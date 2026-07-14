---
tags:
  - experiment-log
date: 2026-03-21
---

# Parameter Golf Agent Program

This is the short execution contract for agents working on Parameter Golf right now.

## Immediate Truth

Use the live working path, not the idealized future path.

For now, the authoritative experiment path is:

- Primary serious runner: `RunPod 8x A40`
- RunPod SSH: `ssh runpod` or `ssh runpod-proxy`
- Current RunPod paths: `/workspace/parameter-golf`, `/workspace/experiments`, `/workspace/fair_runs`
- RunPod template image: `runpod/parameter-golf:latest`
- Current fair stacked harness: `/workspace/fair_runs/exp017_meta_stack_core/train.py`
- Current A40 launch requirement: `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1` for healthy 8-GPU DDP on the live pod
- Secondary background runner: `enc1-gpuvm010`
- MI300X SSH: `ssh mi300x` or `ssh hotaisle@23.183.40.75`
- Active repo: `~/parameter-golf`
- Active training entrypoint: `~/parameter-golf/train_gpt.py`
- Preferred runtime on MI300X: warmed Docker image `pgolf-ready:latest`
- Live single-run helper: `~/experiments/run_and_save.sh`
- Host Python on MI300X: `python3` with `torch 2.5.1+rocm6.2` for inspection and fallback only

Do not use `~/autoresearch/.venv` or host `python3` as the default training path right now.

Why:

- RunPod now gives us a true CUDA path for serious multi-GPU experiments without ROCm-specific friction
- the template already ships with Python 3.12, PyTorch 2.9.1 CUDA 12.8, and the required Python dependencies
- RunPod is already live with an 8-GPU baseline under `/workspace/experiments/baseline_8gpu`
- the fastest live path is the warmed ROCm 7.2 / PyTorch 2.10 image `pgolf-ready:latest`
- the current live RunPod work is `exp017_meta_stack_core`; MI300X promotion runs remain background/history unless explicitly re-checked
- `~/autoresearch` is still CUDA-pinned
- the current ROCm work is happening in `parameter-golf`, not `autoresearch`

## Before You Start

1. Read [AGENT_COORDINATION.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/AGENT_COORDINATION.md).
2. Read [task-board.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/task-board.md).
3. Check [leaderboard.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/leaderboard.md) and [insights.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/insights.md).
4. Claim one task before running anything.

## Current Roles

- `Claude Code`: VM runner and experiment executor
- `Codex Relay`: queue shaper, integration reviewer, shared-state synchronizer

## Baseline Status

Two baseline states matter right now:

- completed eager host baseline, mirrored locally
- active ROCm 7.2 / PyTorch 2.10 container baseline for the faster runtime path

Completed eager log path:

```text
/home/hotaisle/parameter-golf/logs/81ec99c4-6915-47dd-8bef-40f90d3f45b7.txt
```

Local mirror:

```text
experiments/baseline/
```

Historical MI300X batch log:

```text
/home/hotaisle/experiments/phase1_exclusive_20260321T162134.log
```

Most recent MI300X promotion run:

```text
/home/hotaisle/experiments/phase1/exp004_partial_rope_promo/
```

Last known RunPod run:

```text
/workspace/fair_runs/exp017_meta_stack_core/full_log.txt
```

Template bootstrap on a fresh pod:

```bash
cd /workspace
git clone https://github.com/openai/parameter-golf.git
cd parameter-golf
python3 data/cached_challenge_fineweb.py --variant sp1024
```

Repo-native launch wrappers that matter on RunPod:

```text
/workspace/parameter-golf/experiments/run_all.sh
/workspace/parameter-golf/experiments/exp0*/run.sh
/workspace/parameter-golf/run_fastest_path.sh
```

Important: those repo scripts are the intended launch shape, but some experiment labels still outpace implementation. `exp03`, `exp04`, and `exp05` in the repo currently document that XSA, Partial RoPE/LN Scale, and true gradient-guided quant are not fully merged into `train_gpt_sota.py` yet.

## How To Run A New Experiment

Use one bounded change per run. For promising variants, prefer a longer promotion rerun over adding more short weak probes.

```bash
ssh mi300x
mkdir -p ~/experiments/phase1/expXXX_name
cp ~/parameter-golf/train_gpt.py ~/experiments/phase1/expXXX_name/train.py

# make one specific change to train.py, then either:
# 1. point ~/experiments/run_and_save.sh at that snapshot for a clean single run
# 2. use 600s for quick directional checks
# 3. use 1800s for promotion runs once a variant looks real
```

After the run:

1. Extract the best or final `val_bpb`
2. Save a small `result.json`
3. Update [leaderboard.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/leaderboard.md)
4. Update [insights.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/insights.md) if there is a real finding
5. Add one line to [task-board.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/task-board.md)
6. Sync the promoted artifact set into the matching local vault phase folder

## Artifact Layout

Remote VM:

```text
~/experiments/
  baseline/
  phase1/
  phase2/
  phase3/
  phase1/
    expXXX_name/
      train.py
      full_log.txt
      result.json
      config.json
      env_overrides.txt
```

Local vault:

```text
experiments/
  README.md
  leaderboard.md
  insights.md
  task-board.md
  AGENT_COORDINATION.md
  program.md
  baseline/
  phase1/
  phase2/
  phase3/
```

Important: the local vault is a synchronized mirror for coordination and promoted artifacts. Live experiment scratch directories are still created and executed on the VM first. A local phase folder may be empty until a run is synced back.

## Current Priorities

1. Keep the current RunPod `exp017_meta_stack_core` harness as the authoritative live path
2. Treat the `524288` batch size as the A40 default; `786432` was tested and lost badly
3. Run the current architecture loop one-by-one on the same harness and launch shape: `Partial RoPE + KV8`, then `Partial RoPE + KV8 + NTK-RoPE`
4. Treat MI300X promotion notes as historical/background unless explicitly re-checked
5. Treat `autoresearch` ROCm porting as a later harness-improvement task
6. Keep syncing live RunPod artifacts and launch recipes back into the vault

## Promotion Rule

- Keep `600s` for first-pass directional checks
- Move promising variants to `1800s` quickly instead of spending most time on weak follow-ups
- Use `3600s` only for finalists or near-submission confidence checks

## Known ROCm Caveats

- `~/autoresearch` is pinned to CUDA wheels and is not the default path yet
- FlashAttention-style NVIDIA assumptions need fallbacks if `autoresearch` becomes active later
- `torch.compile` should be treated cautiously on ROCm bring-up

## Rule Of Thumb

Prefer the path that is running real experiments today over the path that is theoretically cleaner but not yet operational.
