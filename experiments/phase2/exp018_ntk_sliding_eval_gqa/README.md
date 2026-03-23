# exp018_ntk_sliding_eval_gqa

Separate exp017-derived experiment for testing NTK-RoPE under longer-context sliding evaluation without touching the main harness.

## Purpose

NTK-RoPE only changes the rotary base when evaluation sequence length exceeds training sequence length. The standard exp017 validation path uses fixed `TRAIN_SEQ_LEN=1024` chunks, so it does not meaningfully exercise NTK behavior.

This copy adds:
- `EVAL_SEQ_LEN`
- `EVAL_STRIDE`
- `EVAL_MAX_WINDOWS`
- sliding-window validation that scores only newly exposed tokens per stride

Current status: this is the active A40 NTK fairness run. It follows `exp017_partial_rope_swa`, and `exp017_partial_rope_ortho` is queued behind it.

## Intended Run

- `ROPE_DIM=16`
- `NUM_KV_HEADS=4`
- `NTK_ROPE_ENABLED=1`
- `EVAL_SEQ_LEN=2048`
- `EVAL_STRIDE=64`
- `EVAL_MAX_WINDOWS` for directional A40 testing

## Notes

- This is a directional NTK test harness, not yet the canonical baseline harness.
- Full stride-64 sliding eval over the entire 62M-token validation split is too expensive on A40, so `EVAL_MAX_WINDOWS` exists to cap directional tests.
