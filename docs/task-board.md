---
tags:
  - experiment-log
date: 2026-03-21
---

# Parameter Golf Shared Task Board

Single shared coordination file for all coding agents working on the [[Parameter Golf Experiment Framework]].

## Purpose

Use this file as the visible source of truth for:

- who is working on what
- what is blocked
- what has already been set up
- what needs to be handed off to the next agent

Memory store is still useful, but this file is the human-readable coordination layer that every agent can inspect and update directly.

## Coordination Rules

1. Claim one concrete task at a time.
2. Update the status before and after doing work.
3. If you change the VM or experiment harness, add one line to the activity log.
4. If you finish an experiment, also update [leaderboard.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/leaderboard.md).
5. If you discover a pattern or failure mode, also update [insights.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/insights.md).
6. Record important milestones to memory store when possible, but do not rely on memory store alone for coordination.

## Active Context

- Primary live memory thread from this session: `T-QC6YRP`
- Framework-referenced VM setup thread: `T-F9ZTX1`
- Current issue: `T-F9ZTX1` was referenced in the framework note but was not accessible from this session, so textual coordination in this file is currently the safer shared layer

## Agent Roster

| Agent Name | Tooling | Role | Coordination Style |
|---|---|---|---|
| Claude Code | external coding agent | primary VM runner and experiment executor | updates shared files + memory store |
| Codex Relay | Codex | cross-agent coordinator, integration reviewer, vault synchronizer | reads shared files each loop, claims tasks, writes handoffs |

## Loop Protocol

Every active agent should work in short loops:

1. Read [AGENT_COORDINATION.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/AGENT_COORDINATION.md), this task board, [leaderboard.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/leaderboard.md), and [insights.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/insights.md).
2. Claim exactly one task or subtask.
3. Do one bounded unit of work.
4. Write a short handoff note into the activity log.
5. Record major findings to memory store if available.
6. Repeat.

This keeps collaboration visible even when agents cannot directly message each other.

## Current Compute State

- Primary serious runner: `RunPod 8x A40`
- RunPod SSH: `ssh runpod` or `ssh runpod-proxy`
- RunPod live paths: `/workspace/parameter-golf`, `/workspace/experiments`, `/workspace/fair_runs`
- Current healthy 8-GPU A40 launch requires: `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1`
- Secondary background runner: `enc1-gpuvm010`
- MI300X SSH: `ssh hotaisle@23.183.40.75`
- Host OS: Ubuntu 22.04.5
- GPU visibility on host: working
- Host PyTorch: `2.5.1+rocm6.2`
- GPU seen by host PyTorch: `AMD Instinct MI300X VF`
- Docker: installed
- ROCm PyTorch image pulled: `rocm/pytorch:rocm7.2_ubuntu22.04_py3.11_pytorch_release_2.10.0`
- Preferred runtime now: official ROCm container on PyTorch `2.10.0+rocm7.2.0`
- Active container observed: historical MI300X promotion note; current live RunPod work is `exp017_meta_stack_core`
- Remote folders present: `~/autoresearch`, `~/parameter-golf`, `~/experiments`
- Important caveat: upstream `~/autoresearch` is still CUDA-oriented and its `.venv` currently sees `torch 2.9.1+cu128` with no GPU

## Shared Tasks

| ID | Status | Owner | Task | Notes |
|---|---|---|---|---|
| PG-001 | completed | Claude Code | Establish reproducible ROCm experiment runtime | Host PyTorch 2.5.1+rocm6.2 works, GPU verified, deps installed |
| PG-002 | completed | Claude Code | Decide whether to use upstream `autoresearch` with patches or switch to AMD fork | Using upstream with patches — simpler |
| PG-003 | completed | Claude Code | Add ROCm-safe attention/kernel fallback for `parameter-golf/train_gpt.py` | Patched: GQA via repeat_interleave, nvidia-smi→rocm-smi, torch.compile disabled |
| PG-004 | completed | Claude Code | Run first baseline smoke test and capture `val_bpb` logging path | DONE: val_bpb=1.9603 (float), 2.0668 (quant), 251 steps/600s, log `~/parameter-golf/logs/81ec99c4*.txt` |
| PG-005 | completed | Codex Relay | Create/align `program.md` with Phase 1 experiment ladder | Shared runbook added at `experiments/program.md` |
| PG-006 | pending | unclaimed | Define parallel experiment process limits on MI300X VF | Framework estimates 4-8; needs empirical validation |
| PG-007 | completed | Codex | Mirror local experiment phase folders in vault | `experiments/baseline`, `phase1`, `phase2`, `phase3` created |
| PG-008 | completed | Codex | Create shared multi-agent coordination file | This file |
| PG-009 | in_progress | Codex Relay | Maintain cross-agent synchronization loop | Read Claude updates, reconcile shared files, keep handoffs clean |
| PG-010 | pending | unclaimed | Reconcile framework docs with live harness reality | `autoresearch` is planned, but baseline is running in `parameter-golf` |
| PG-011 | in_progress | Codex Relay | Investigate Option C speed fixes with Claude | Focus: faster iterations via ROCm kernel/runtime improvements and promotion-run strategy |
| PG-012 | in_progress | Codex Relay | Normalize local artifact sync and phase-folder visibility | Populate vault mirrors so experiment state is visible without SSH |
| PG-013 | in_progress | Codex Relay | Run the A40 architecture loop and keep notes synchronized | Control, Late QAT, Partial RoPE, LN Scale, batch786, `KV8`, and `NTK on 4KV` are now recorded; the live pod has moved to `exp018_ntk_sliding_eval_gqa` as the first fair NTK test, with `exp017_partial_rope_ortho` queued behind it |
| PG-014 | completed | Codex Relay | Save the live RunPod meta-stack run into vault state | Working 8-GPU launch recipe, current log path, and live status for `exp017_meta_stack_core` are now recorded; stale "current" labels retired |
| PG-015 | in_progress | Codex Relay | Record A40 findings in memory store and vault docs | Batch786 is a systems dead end on A40; `KV8` finished weaker than the best Partial-RoPE family, `SWA` finished at `1.37406320`, and the fixed-length NTK read is not final until `exp018_ntk_sliding_eval_gqa` completes |

## Hand-Off Notes

- If you take `PG-001`, prefer a path that works both interactively and in unattended overnight runs.
- If you take `PG-002`, compare the AMD fork against upstream before making broad code edits.
- If you take `PG-003`, start by removing the assumption that only NVIDIA FlashAttention is available.
- If you take `PG-004`, save exact command, runtime, and log location here after the first successful run.

## Activity Log

### 2026-03-22

- Codex Relay: recorded `exp017_partial_rope_swa` as finished at `final_int8_zlib_roundtrip_exact val_bpb 1.37406320`
- Codex Relay: launched `exp018_ntk_sliding_eval_gqa` as the active NTK fairness run with sliding eval and queued `exp017_partial_rope_ortho` behind it

### 2026-03-21

- Codex: connected to `enc1-gpuvm010`, confirmed MI300X VF visibility with `amd-smi` and host PyTorch
- Codex: confirmed Docker is installed and pulled the official ROCm PyTorch image
- Codex: verified remote repo layout exists at `~/autoresearch`, `~/parameter-golf`, and `~/experiments`
- Codex: found that upstream `~/autoresearch/.venv` is CUDA-pinned and not usable for ROCm as-is
- Codex: created local vault phase folders and this shared task board for agent coordination
- Claude Code: installed PyTorch 2.5.1+rocm6.2 on host (no Docker needed), verified GPU compute
- Claude Code: installed parameter-golf requirements, downloaded FineWeb data (16GB, 81 shards)
- Claude Code: patched train_gpt.py for ROCm — GQA via repeat_interleave, nvidia-smi→rocm-smi, torch.compile disabled
- Claude Code: baseline training running (PG-004), awaiting first val_bpb
- Claude Code: created AGENT_COORDINATION.md with full experiment queue and parallel run instructions
- Claude Code: added SSH config (`ssh mi300x`) with key setup instructions
- Codex Relay: adopted stable agent identity for collaboration and added roster + loop protocol to the shared task board
- Codex Relay: subagent sweep confirmed baseline is live in `~/parameter-golf`, not `~/autoresearch`; claimed PG-005 and wrote a shared `experiments/program.md` execution contract
- Codex Relay: monitored Claude's live baseline run; latest log `/home/hotaisle/parameter-golf/logs/81ec99c4-6915-47dd-8bef-40f90d3f45b7.txt` shows `model_params:17059912`, GPU at 100%, and training progressing through step 10
- Codex Relay: prepared remote `~/experiments/{baseline,phase1,phase2,phase3}` folders, copied a baseline train snapshot, and confirmed the current run is still compute-active (`python3 train_gpt.py`, ~121% CPU, GPU 100%, VRAM ~47 GB) even though the visible log has not advanced past step 10 yet
- Codex Relay: set up direct observability paths for the user — local Docker context `mi300x-vm`, remote tmux monitor session `pg-monitor`, helper scripts in `experiments/`, and local plot sync to `experiments/plots-vm/training_curves.png`
- Codex Relay: claimed PG-011 to collaborate with Claude on speed fixes; next pass is focused on Option C runtime improvement and faster experiment modes
- Codex Relay: synced baseline artifacts into the local vault mirror, added `experiments/README.md`, wrote `experiments/baseline/result.json`, and added phase-folder readmes so empty local folders are now explicit status rather than silence
- Ohm: speed review found that runtime docs disagree on `120s` vs `360s/420s/600s`, `run_fast.sh` is not snapshot-isolated, and fast runs still pay full validation plus final quantization tax
- Sartre: measured the main dev-time sinks as repeated full validation over `62,021,632` tokens plus mandatory post-training roundtrip eval; current wrappers can make a nominal 2-minute run much longer in real wallclock
- James: verified the official ROCm 7.2 / PyTorch 2.10 container is the practical speed fix; live `pgolf_baseline` logs show about `735 ms/step` by step 200, which is much faster than the older host eager path
- Codex Relay: checked the finished `pgolf_baseline` container result and mirrored it locally; final container baseline is `816` steps in `601.168s`, float `val_bpb=1.3971`, quantized `val_bpb=1.4005`
- Codex Relay: claimed `exp001_muon` as the first Phase 1 run and started reading the live optimizer path in `~/parameter-golf/train_gpt.py` before patching the ROCm-container experiment copy
- Codex Relay: found that Muon is already part of the live baseline optimizer split, so `exp001_muon` would be a no-op; switched the first real Phase 1 run to `exp003_ema`
- Codex Relay: pushed the EMA experiment snapshot to `~/experiments/exp003_ema/train.py` and confirmed the live `pgolf_exp003_ema` container is using it; current log includes `ema_decay:0.997000`
- Codex Relay: discovered a fairness blocker after launch: untracked container `pgolf_exp001` is also active on the same single GPU, so `exp003_ema` cannot be trusted as a clean comparison unless one run is stopped and retried alone
- Codex Relay: identified the untracked container as `exp001_11L_3xMLP` with `26,501,720` params and step-200 progress in `~/experiments/exp001_11L_3xMLP/full_log.txt`
- User clarified that parallel swarm execution is the goal; contention on the single MI300X is acceptable for exploratory runs, so we should compare experiments within similar concurrency conditions instead of treating contention as a blocker
- Codex Relay: created `experiments/phase1/exp004_partial_rope/train.py`, patched Partial RoPE to rotate only `16/64` head dims, and verified the snapshot compiles locally before VM launch
- Codex Relay: synced the live VM logs back into local vault folders for `exp001_11L_3xMLP`, `exp003_ema`, `exp004_partial_rope`, and `exp005_ln_scale`; added `experiments/sync-vm-experiment-logs.sh` for repeat pulls
- Codex Relay: monitored the end of the first swarm batch; `exp004_partial_rope` finished at final int8 roundtrip `val_bpb=1.5973`, `exp005_ln_scale` finished at `val_bpb=1.6751` / quantized `1.7163`, and no experiment containers remained active afterward
- Codex Relay: updated the coordination docs to say explicitly that swarm slowdown on the MI300X is compute contention, not VRAM exhaustion, and that contended runs are directional signals best compared within the same concurrency bucket
- Codex Relay: created the missing Phase 1 experiment snapshots for `exp002_xsa4`, `exp006_smeargate`, `exp007_bigramhash`, and `exp008_late_qat`, plus a clean VM runner that writes `config.json`, `env_overrides.txt`, `full_log.txt`, `logs/`, and `result.json`
- Codex Relay: launched the new exclusive overnight Phase 1 batch through `~/experiments/run_phase1_batch.sh`; current remote batch log is `~/experiments/phase1_exclusive_20260321T162134.log` and the first active container is `pgolf_phase1_exp001_11L_3xMLP_clean`
- Codex Relay: reconciled the runner conflict on the VM, detected that the other clean batch script had failed after `exp001`, copied the missing `exp007_bigramhash_clean` patch into the active clean path, and queued `exp002` through `exp008` behind the current `exp001_11L_3xMLP_clean` container with `~/experiments/phase1_clean_remaining_manifest.tsv`
- Codex Relay: verified that `exp002_xsa4` was slowed by the manual exclude-self attention path, confirmed the local `exp002_xsa4_clean` snapshot already uses a shifted-SDPA fast path, and corrected the clean runner/manifest env var drift to `XSA_LAYERS=4` so the next XSA rerun will be fair
- Codex Relay: synced the new clean result files locally for `exp001_11L_3xMLP_clean`, `exp002_xsa4`, and `exp003_ema_clean`, then restarted Phase 1 manually on `exp004_partial_rope_clean` after the original clean batch stalled
- Codex Relay: updated the shared strategy to stop over-investing in weak 600s probes; after the current rerun, promising variants should be promoted to `1800s` runs before we keep expanding the short queue
- Codex Relay: `exp004_partial_rope_clean` finished very strong at `1.4000 / 1.4032` with `821` steps and baseline-class throughput, so the policy change is now live on the VM as `exp004_partial_rope_promo` (`1800s`, `TRAIN_LOG_EVERY=200`, `VAL_LOSS_EVERY=800`)
- Codex Relay: added the new RunPod access to the shared compute picture and aligned the docs so RunPod is the primary serious-experiment box while the MI300X stays the background ROCm box
- Codex Relay: logged into RunPod and confirmed it is already running a serious 8-GPU CUDA baseline at `/workspace/experiments/baseline_8gpu/full_log.txt`; current speed is about `202ms/step`, `step 1000 val_bpb=1.3823`, and the main gap is that RunPod artifacts are not yet normalized into the same `result.json` sync flow as MI300X

### 2026-03-22

- Codex Relay: reviewed the actual RunPod repo entrypoints (`run_all.sh`, `exp0*/run.sh`, `run_fastest_path.sh`) and confirmed they are the intended launch wrappers, but several experiment labels in `train_gpt_sota.py` are still placeholders rather than implemented features
- Codex Relay: reproduced the current A40 pod NCCL failure mode with a tiny 8-GPU DDP smoke test and found the reliable fix is `NCCL_IB_DISABLE=1 NCCL_P2P_DISABLE=1`
- Codex Relay: saved the working A40 launch recipe into `experiments/phase2/exp017_meta_stack_core/runpod_8gpu_a40.sh` and recorded the live run status in the vault while the pod training continued
- Codex Relay: normalized the shared docs so MI300X is clearly background-only, the A40 meta-stack run is the only live RunPod task, and stale "current" labels are retired
- Codex Relay: re-checked the live RunPod state and found the pod had advanced well past the saved `KV8` note; recorded finished `exp017_partial_rope_swa` (`1.37406320`), finished `exp017_partial_rope_kv8` (`1.37748001`), finished `exp017_partial_rope_ntk_gqa` (`1.37173728`), and marked `exp017_partial_rope_kv8_ntk` as interrupted by `SIGTERM` at `step 300`
- Codex Relay: launched `exp018_ntk_sliding_eval_gqa` as the first fair NTK sliding-eval test on the 4-KV base and queued `exp017_partial_rope_ortho` behind it

## See also

- [[Parameter Golf Experiment Framework]]
- [[Parameter Golf Goal Definition]]
- [leaderboard.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/leaderboard.md)
- [insights.md](/Users/a3fckx/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/a3fckx/experiments/insights.md)
