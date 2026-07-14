#!/usr/bin/env python3
"""
Experiment: exp009_ntk_rope
NTK-aware RoPE (Neural Tangent Kernel-aware Rotary Positional Embedding)

Purpose: Enable length extrapolation by dynamically scaling RoPE base frequency
when evaluation sequences are longer than training sequences.

Key Change: Modified Rotary class to apply NTK-aware base scaling.
When eval_seq_len > train_seq_len:
    base_scaled = base * (eval_seq_len / train_seq_len) ** (1 / dim)

Expected Impact: Better BPB on sliding window eval (stride=64) which uses
longer sequences (2048) than training (1024).

Reference: PR #369 (signalrush) - 1.1328 BPB with NTK-RoPE + FA3
"""

import os
import sys
import math
import time
import json
import struct
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.cpp_extension import load_inline

# -----------------------------------------------------------------------------
# NTK-aware RoPE Configuration

# Standard training sequence length (from baseline)
TRAIN_SEQ_LEN = int(os.environ.get("TRAIN_SEQ_LEN", "1024"))

# Enable NTK-aware scaling
NTK_ROPE_ENABLED = int(os.environ.get("NTK_ROPE_ENABLED", "1"))

# Scaling factor exponent (1/dim as per PR #369)
NTK_SCALE_EXPONENT = float(os.environ.get("NTK_SCALE_EXPONENT", "0.0"))  # Auto: 1/dim

# -----------------------------------------------------------------------------
# Muon optimizer (unchanged from baseline)


class Muon(torch.optim.Optimizer):
    """
    Muon optimizer - spectral norm optimizer using Newton-Schulz iteration
    From PR #369: momentum=0.99, 5 Newton-Schulz steps
    """

    def __init__(self, params, lr=0.02, momentum=0.99, nesterov=True, ns_steps=5):
        defaults = dict(lr=lr, momentum=momentum, nesterov=nesterov, ns_steps=ns_steps)
        super().__init__(params, defaults)

    def step(self):
        for group in self.param_groups:
            for p in group["params"]:
                if p.grad is None:
                    continue

                g = p.grad
                state = self.state[p]

                if "momentum_buffer" not in state:
                    state["momentum_buffer"] = torch.zeros_like(g)

                buf = state["momentum_buffer"]
                buf.mul_(group["momentum"]).add_(g)

                if group["nesterov"]:
                    g = g.add(buf, alpha=group["momentum"])
                else:
                    g = buf

                # Newton-Schulz iteration for orthogonalization
                if g.ndim == 2 and g.size(0) >= 64 and g.size(1) >= 64:
                    # Spectral normalization via Newton-Schulz
                    X = g
                    # Initialize with normalized matrix
                    a = X.norm(dim=0, keepdim=True).clamp_min(1e-8)
                    X = X / a

                    # Newton-Schulz iterations
                    for _ in range(group["ns_steps"]):
                        X = X @ (
                            1.5 * torch.eye(X.size(1), device=X.device) - 0.5 * X.T @ X
                        )

                    g = X * a

                p.data.add_(g, alpha=-group["lr"])


# -----------------------------------------------------------------------------
# NTK-aware RoPE Implementation


class Rotary(nn.Module):
    """
    Rotary Position Embedding (RoPE) with NTK-aware base scaling.

    Standard RoPE uses fixed base frequency. NTK-aware RoPE dynamically scales
    the base when evaluating on sequences longer than training sequences.

    From PR #369: base_scaled = base * (seq_len / train_seq_len) ** (1/dim)
    """

    def __init__(self, dim: int, base: float = 10000.0):
        super().__init__()
        self.dim = dim
        self.base = base
        self.train_seq_len = TRAIN_SEQ_LEN

    def forward(self, x: torch.Tensor, seq_len: Optional[int] = None) -> torch.Tensor:
        """
        Apply rotary embeddings to input x.

        Args:
            x: Input tensor [batch, num_heads, seq_len, head_dim]
            seq_len: Current sequence length (for NTK scaling)
        """
        batch, n_heads, seq, head_dim = x.shape
        assert head_dim == self.dim, f"Head dim {head_dim} != Rotary dim {self.dim}"

        if seq_len is None:
            seq_len = seq

        # NTK-aware base scaling
        if NTK_ROPE_ENABLED and seq_len > self.train_seq_len:
            # Calculate scaling exponent (1/dim by default)
            exponent = (
                NTK_SCALE_EXPONENT if NTK_SCALE_EXPONENT > 0 else (1.0 / self.dim)
            )
            # Scale base: base * (seq_len / train_seq_len) ^ (1/dim)
            scale_factor = (seq_len / self.train_seq_len) ** exponent
            base = self.base * scale_factor
        else:
            base = self.base

        # Compute rotary frequencies
        inv_freq = 1.0 / (
            base ** (torch.arange(0, self.dim, 2, device=x.device).float() / self.dim)
        )
        t = torch.arange(seq, device=x.device)
        freqs = torch.outer(t, inv_freq)  # [seq, dim/2]

        # Convert to complex rotation
        cos, sin = torch.cos(freqs), torch.sin(freqs)

        # Apply rotation
        x1, x2 = x[..., ::2], x[..., 1::2]  # Split into even/odd
        rotated = torch.stack([x1 * cos - x2 * sin, x1 * sin + x2 * cos], dim=-1)
        return rotated.flatten(-2)  # [batch, n_heads, seq, dim]


# -----------------------------------------------------------------------------
# Model Components (unchanged from baseline)


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


class CausalSelfAttention(nn.Module):
    """Multi-head causal self-attention with GQA and RoPE."""

    def __init__(
        self, dim: int, num_heads: int, num_kv_heads: int, max_seq_len: int = 2048
    ):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = dim // num_heads

        assert dim % num_heads == 0

        # Q, K, V projections
        self.q_proj = nn.Linear(dim, num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(dim, num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(dim, num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(num_heads * self.head_dim, dim, bias=False)

        # RoPE
        self.rotary = Rotary(self.head_dim)

        # Causal mask
        self.register_buffer(
            "mask", torch.triu(torch.ones(max_seq_len, max_seq_len), diagonal=1).bool()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, T, C = x.shape

        # Project
        q = self.q_proj(x).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, T, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, T, self.num_kv_heads, self.head_dim).transpose(1, 2)

        # Apply RoPE
        q = self.rotary(q, T)
        k = self.rotary(k, T)

        # GQA: repeat K/V heads
        if self.num_kv_heads < self.num_heads:
            k = k.repeat_interleave(self.num_heads // self.num_kv_heads, dim=1)
            v = v.repeat_interleave(self.num_heads // self.num_kv_heads, dim=1)

        # Scaled dot-product attention
        scale = 1.0 / math.sqrt(self.head_dim)
        attn = torch.matmul(q, k.transpose(-2, -1)) * scale
        attn = attn.masked_fill(self.mask[:T, :T], float("-inf"))
        attn = F.softmax(attn, dim=-1)

        out = torch.matmul(attn, v)
        out = out.transpose(1, 2).contiguous().view(B, T, C)

        return self.o_proj(out)


class MLP(nn.Module):
    def __init__(self, dim: int, mult: int = 4):
        super().__init__()
        hidden = int(dim * mult)
        self.up_proj = nn.Linear(dim, hidden, bias=False)
        self.down_proj = nn.Linear(hidden, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # ReLU squared
        x = self.up_proj(x)
        x = F.relu(x).pow(2)
        return self.down_proj(x)


class Block(nn.Module):
    def __init__(
        self, dim: int, num_heads: int, num_kv_heads: int, mlp_mult: float = 4.0
    ):
        super().__init__()
        self.attn_norm = RMSNorm(dim)
        self.attn = CausalSelfAttention(dim, num_heads, num_kv_heads)
        self.mlp_norm = RMSNorm(dim)
        self.mlp = MLP(dim, mlp_mult)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.attn_norm(x))
        x = x + self.mlp(self.mlp_norm(x))
        return x


class GPT(nn.Module):
    def __init__(
        self,
        vocab_size: int = 1024,
        num_layers: int = 9,
        dim: int = 512,
        num_heads: int = 8,
        num_kv_heads: int = 4,
        mlp_mult: float = 4.0,
        max_seq_len: int = 2048,
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.num_layers = num_layers
        self.dim = dim

        self.embed = nn.Embedding(vocab_size, dim)
        self.blocks = nn.ModuleList(
            [Block(dim, num_heads, num_kv_heads, mlp_mult) for _ in range(num_layers)]
        )
        self.norm = RMSNorm(dim)
        self.head = nn.Linear(dim, vocab_size, bias=False)

        # Tie embeddings
        self.head.weight = self.embed.weight

        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        x = self.embed(tokens)
        for block in self.blocks:
            x = block(x)
        x = self.norm(x)
        logits = self.head(x)
        return logits

    def count_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


# -----------------------------------------------------------------------------
# Training (unchanged from baseline)


def get_batch(data: np.ndarray, batch_size: int, seq_len: int, device: str = "cuda"):
    """Sample a batch from data."""
    ix = torch.randint(len(data) - seq_len, (batch_size,))
    x = torch.stack(
        [torch.from_numpy(data[i : i + seq_len].astype(np.int64)) for i in ix]
    )
    y = torch.stack(
        [torch.from_numpy(data[i + 1 : i + 1 + seq_len].astype(np.int64)) for i in ix]
    )
    return x.to(device), y.to(device)


def train():
    # Config
    vocab_size = int(os.environ.get("VOCAB_SIZE", "1024"))
    num_layers = int(os.environ.get("NUM_LAYERS", "11"))
    dim = int(os.environ.get("MODEL_DIM", "512"))
    num_heads = int(os.environ.get("NUM_HEADS", "8"))
    num_kv_heads = int(os.environ.get("NUM_KV_HEADS", "4"))
    mlp_mult = float(os.environ.get("MLP_MULT", "3.0"))

    train_seq_len = int(os.environ.get("TRAIN_SEQ_LEN", "1024"))
    batch_tokens = int(os.environ.get("TRAIN_BATCH_TOKENS", "524288"))
    batch_size = batch_tokens // train_seq_len

    max_steps = int(os.environ.get("ITERATIONS", "20000"))
    max_time = int(os.environ.get("MAX_WALLCLOCK_SECONDS", "600"))

    lr = float(os.environ.get("MATRIX_LR", "0.025"))
    wd = float(os.environ.get("MUON_WEIGHT_DECAY", "0.04"))
    warmup = int(os.environ.get("WARMUP_STEPS", "20"))

    seed = int(os.environ.get("SEED", "1337"))
    run_id = os.environ.get(
        "RUN_ID", f"exp009_ntk_rope_{time.strftime('%Y%m%d_%H%M%S')}"
    )

    # Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[exp009_ntk_rope] Using device: {device}")
    print(f"[exp009_ntk_rope] NTK-RoPE enabled: {NTK_ROPE_ENABLED}")
    print(f"[exp009_ntk_rope] Train seq len: {train_seq_len}")

    # Seed
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Load data
    data_path = os.environ.get("DATA_PATH", "./data/datasets/fineweb10B_sp1024/")
    val_path = Path(data_path) / "val.bin"
    train_path = Path(data_path) / "train_0.bin"

    print(f"[exp009_ntk_rope] Loading data from {data_path}")

    # Simple binary loader
    def load_bin(path):
        with open(path, "rb") as f:
            header = f.read(256 * 4)  # Skip header
            data = np.frombuffer(f.read(), dtype=np.uint16)
        return data

    train_data = load_bin(train_path)
    val_data = load_bin(val_path)

    print(f"[exp009_ntk_rope] Train tokens: {len(train_data):,}")
    print(f"[exp009_ntk_rope] Val tokens: {len(val_data):,}")

    # Model
    model = GPT(
        vocab_size=vocab_size,
        num_layers=num_layers,
        dim=dim,
        num_heads=num_heads,
        num_kv_heads=num_kv_heads,
        mlp_mult=mlp_mult,
    ).to(device)

    print(f"[exp009_ntk_rope] Model params: {model.count_params():,}")

    # Optimizer
    muon_params = []
    adam_params = []

    for name, p in model.named_parameters():
        if p.ndim >= 2 and p.size(0) >= 64 and p.size(1) >= 64:
            muon_params.append(p)
        else:
            adam_params.append(p)

    optimizer = Muon(muon_params, lr=lr, momentum=0.99, ns_steps=5)
    adam = torch.optim.AdamW(adam_params, lr=0.05, weight_decay=wd)

    print(f"[exp009_ntk_rope] Muon params: {sum(p.numel() for p in muon_params):,}")
    print(f"[exp009_ntk_rope] Adam params: {sum(p.numel() for p in adam_params):,}")

    # Training loop
    start_time = time.time()
    step = 0

    print(f"\n[exp009_ntk_rope] Starting training...")
    print(f"[exp009_ntk_rope] Max time: {max_time}s | Max steps: {max_steps}")

    model.train()

    while time.time() - start_time < max_time and step < max_steps:
        # Get batch
        x, y = get_batch(train_data, batch_size, train_seq_len, device)

        # Forward
        logits = model(x)
        loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))

        # Backward
        optimizer.zero_grad()
        adam.zero_grad()
        loss.backward()

        # Clip grads
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        # Step
        optimizer.step()
        adam.step()

        step += 1

        if step % 100 == 0:
            elapsed = time.time() - start_time
            print(f"step:{step} loss:{loss.item():.4f} time:{elapsed:.1f}s")

    # Validation
    print(f"\n[exp009_ntk_rope] Running validation...")
    model.eval()

    val_loss = 0.0
    val_steps = 20
    with torch.no_grad():
        for _ in range(val_steps):
            x, y = get_batch(val_data, batch_size, train_seq_len, device)
            logits = model(x)
            loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
            val_loss += loss.item()

    val_loss /= val_steps
    val_bpb = val_loss / math.log(2)

    print(f"\n{'=' * 60}")
    print(f"EXPERIMENT COMPLETE: exp009_ntk_rope")
    print(f"Steps: {step}")
    print(f"Val loss: {val_loss:.4f}")
    print(f"Val BPB: {val_bpb:.4f}")
    print(f"{'=' * 60}")

    # Save result
    result = {
        "experiment": "exp009_ntk_rope",
        "ntk_rope_enabled": NTK_ROPE_ENABLED,
        "train_seq_len": train_seq_len,
        "steps": step,
        "val_loss": val_loss,
        "val_bpb": val_bpb,
        "model_params": model.count_params(),
    }

    result_path = Path("result.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[exp009_ntk_rope] Result saved to {result_path}")

    return val_bpb


if __name__ == "__main__":
    train()
