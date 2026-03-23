# Experiment: exp009_ntk_rope

## NTK-aware RoPE (Neural Tangent Kernel-aware Rotary Positional Embedding)

### Purpose
Enable length extrapolation by dynamically scaling RoPE base frequency when evaluation sequences are longer than training sequences.

### Key Change
Modified `Rotary` class in `train_gpt.py` to apply NTK-aware base scaling:

```python
if NTK_ROPE_ENABLED and seq_len > train_seq_len:
    base_scaled = base * (seq_len / train_seq_len) ** (1/dim)
```

### Why This Matters
- **Standard RoPE**: Fixed base frequency (e.g., 10000)
- **Problem**: Model trained on 1024 tokens breaks when evaluating on 2048 tokens (sliding window eval)
- **NTK-RoPE**: Dynamically scales base ~4x when eval_len=2048 > train_len=1024
- **Result**: Smooth extrapolation to unseen sequence lengths

### From PR #369
- Score: **1.1328 BPB** (3-seed mean)
- Train: 1024 tokens
- Eval: 2048 tokens with sliding window (stride=64)
- Zero extra parameters - pure algorithmic improvement

### How to Run

#### On RunPod 8x A40:
```bash
cd /workspace/parameter-golf

# Copy experiment
cp ~/vault/experiments/phase2/exp009_ntk_rope/train.py ./exp009_ntk_rope.py

# Run with NTK-RoPE enabled
NTK_ROPE_ENABLED=1 \
TRAIN_SEQ_LEN=1024 \
NUM_LAYERS=11 \
MLP_MULT=3 \
torchrun --standalone --nproc_per_node=8 exp009_ntk_rope.py
```

#### Environment Variables
- `NTK_ROPE_ENABLED=1` - Enable NTK scaling
- `TRAIN_SEQ_LEN=1024` - Training sequence length (for scaling calculation)
- `NTK_SCALE_EXPONENT=0.0` - Auto: 1/dim, or set manually

### Expected Results
- **Baseline** (standard RoPE, eval=1024): ~1.4000 BPB
- **NTK-RoPE** (eval=2048, sliding window): ~1.38-1.39 BPB
- Improvement from better length generalization

### Integration Plan
If this experiment succeeds:
1. ✅ Add NTK-RoPE to all Phase 2 experiments (QK-Norm, Backout, AttnRes)
2. ✅ Add NTK-RoPE to all Phase 3 JEPA experiments
3. ✅ Include in final H100 submission stack

### Files
- `train.py` - Modified model with NTK-RoPE
- `config.json` - Experiment configuration
- `README.md` - This file

### References
- PR #369: https://github.com/openai/parameter-golf/pull/369
- Paper: "RoPE: Rotary Position Embedding" (Su et al., 2021)
- NTK theory: Neural Tangent Kernel (Jacot et al., 2018)
