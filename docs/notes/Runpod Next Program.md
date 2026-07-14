---
tags:
  - experiment-log
  - wip
date: 2026-03-22
---

# Runpod Next Program

This is the short planning note for the remaining A40 program after the current flag-only lane.

## Current Lane

- `exp018_ntk_sliding_eval_gqa` already finished badly at `2.01194449` int8+zlib BPB, so NTK is not a keeper from this A40 sliding-eval run.
- `exp017_partial_rope_ortho` is the last cheap flag-only run still active.
- `exp017_partial_rope_swa` finished at `1.37406320`, which was close but still behind plain `Partial RoPE`.
- `batch786`, `LN Scale`, `KV8`, and the A40 NTK sliding-eval run are all treated as negative signals on this pod.

## What To Run Next

1. Let `exp017_partial_rope_ortho` finish as the last cheap flag-only check.
2. Freeze the conventional A40 anchor around the strongest simple `Partial RoPE` stack.
3. Move directly into the longer-step research lane:
   - `exp020_span_jepa_meta_stack`
   - `exp021_attnres_meta_stack`
4. Shut the pod down automatically after both longer-step runs finish and logs are synced back.

## Decision Gates

- Keep `OrthoInit` only if it improves the same `Partial RoPE` base without hurting step time.
- `NTK-RoPE` failed this A40 sliding-eval check and is no longer in the active keep pile.
- If `OrthoInit` also fails to help, stop the flag-only lane entirely.

## Switch To Longer Runs

Move to longer-step `JEPA` and `AttnRes` experiments after:

- the best conventional stack is frozen
- the remaining flag-only tests are exhausted
- the pod has a clean `Partial RoPE` comparison anchor
- we explicitly accept that A40 is only a directional research platform, not parity with H100 public runs

The queued longer-step lane is:

1. a `JEPA` variant on the strongest conventional stack
2. an `AttnRes` variant on the same anchor
3. then automatic pod shutdown after logs are mirrored back

## Shutdown Point

Shut down the pod after:

- `exp017_partial_rope_ortho` finishes
- `exp020_span_jepa_meta_stack` finishes
- `exp021_attnres_meta_stack` finishes
- the logs and int8 artifacts are synced back into the vault

See also: [[Parameter Golf]], [[Parameter Golf Experiment Framework]], [[AGENT_COORDINATION]], [[task-board]]
