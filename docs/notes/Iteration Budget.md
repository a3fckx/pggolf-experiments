---
tags:
  - full-note
date: 2026-03-22
---

# Iteration Budget

Short A40 runs are useful, but only for a limited class of questions.

## What A40 600s Runs Tell Us

- They are good for directionality: does a change improve early loss, stabilize training, or obviously break the harness?
- They are good for cheap ablations on the same harness, seed, and launch shape.
- They are good for ranking ideas that mainly differ in optimization behavior or runtime cost.

## What They Do Not Tell Us

- They do not reliably predict final leaderboard rank against stronger H100-style runs.
- They do not fully capture late-training effects like grokking, delayed regularization wins, or long-horizon eval gains.
- They do not settle whether a trick is “real” if it only helps after many more steps.

## Throughput Reality

- A 600s run on our current A40 pod is around `1072` steps at about `560 ms/step`.
- Stronger public H100 runs are in a very different throughput class, so they simply see more optimization in the same wallclock.
- That means a small early gain on A40 can still lose to a slower-starting idea that needs more steps to show its value.

## Comparability Limits

- Compare A40 600s runs to each other only when the launch shape and harness are the same.
- Do not directly compare a short A40 directional run to a long H100 public result as if they were the same budget.
- Use H100 results as an external target for where the stack should end up, not as a like-for-like scorecard for short local ablations.

## What We Can Conclude

- `exp017_meta_stack_core` showed the stacked A40 harness is healthy and can produce real signal under the 600s cap.
- Early improvement on the stacked base is meaningful, especially for deciding what deserves a longer promotion run.
- `Partial RoPE`, `XSA`, `LN Scale`, and `NTK-RoPE` should be judged first by whether they help on the same local stack.

## What We Cannot Conclude Yet

- Whether `JEPA` or `AttnRes` is truly competitive from a single 600s pass.
- Whether a regularization-heavy idea will win only after many more steps.
- Whether a small A40 win survives into the stronger public H100 regime without a longer promotion run.

## Credible Long Runs For Novel Ideas

- `JEPA` and `AttnRes` need longer promotion-style runs, not just a single short probe.
- A credible test should keep the same stack, then extend wallclock and step count enough to observe late effects.
- For these ideas, the run needs to be long enough that plateau-then-improve behavior would actually have time to appear.

## See also

- [[Parameter Golf Experiments]]
- [[Experiment Entry Points]]
- [[AGENT_COORDINATION]]
- [[insights]]
