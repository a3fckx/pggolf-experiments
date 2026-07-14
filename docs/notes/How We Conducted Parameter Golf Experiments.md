---
tags:
  - experiment-log
  - parameter-golf
  - methodology
date: 2026-03-23
---

# How We Conducted Parameter Golf Experiments

This note is the vault-side methodology summary for the Parameter Golf work.

## Canonical Split

- Code and runnable harnesses live in `pggolf-experiments/`.
- The vault keeps the summary layer:
  - what we ran
  - what we learned
  - what changed our beliefs
  - how the workflow evolved

## Experiment Loop

1. Start from the current best known harness.
2. Change one bounded thing at a time.
3. Run a directional check first.
4. Promote only the promising variants to longer reruns.
5. Record the result in `leaderboard.md`.
6. Record the learning in `insights.md`.
7. Promote stable conceptual learning into `4 - Full Notes/`.

## Working Infrastructure Pattern

- Use the fast, working runtime path rather than the theoretically nicest one.
- Keep the execution path separate from the note-taking path.
- Compare runs within similar conditions.
- Treat contended exploratory runs differently from clean benchmark runs.

## What This Folder Should Become

Over time, `experiments/` should contain fewer code mirrors and more high-signal notes:

- `leaderboard.md`
- `insights.md`
- methodology notes
- selected experiment summaries
- links into the deeper knowledge notes in the vault

## Related Notes

- [[OpenAI Parameter Golf]]
- [[Parameter Golf Experiment Framework]]
- [[Parameter Golf Evaluation Tricks]]
- [[Parameter Golf Negative Results]]
