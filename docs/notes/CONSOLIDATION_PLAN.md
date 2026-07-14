# Experiment Documentation Consolidation Plan

Based on swarm agent analysis of vault patterns and 4 experiment documents totaling ~12,950 words.

---

## 1. Proposed New Atomic Notes

### From `insights.md` (285 lines) → 6 atomic notes + 1 log

#### Note 1: Partial RoPE in Parameter Golf
- **Source**: insights.md, lines 138-172
- **Type**: `full-note`
- **Description**: Comparative analysis of Partial RoPE (16/64 dims) vs full RoPE showing speed gains (~10ms/step faster) and improved BPB (1.371 vs 1.379). Includes step-by-step loss curves and validation checkpoints.
- **Key Wikilinks**: [[RoPE]], [[NTK-aware RoPE]], [[Parameter Golf Experiment Framework]], [[Parameter Golf Negative Results]], [[OpenAI Parameter Golf]]
- **Length**: Medium (60-80 lines)

#### Note 2: NTK-aware RoPE Implementation
- **Source**: insights.md, lines 256-272 + AGENT_COORDINATION.md, lines 192-275
- **Type**: `full-note`
- **Description**: Dynamic base frequency scaling for length extrapolation. Implementation details, test matrix (train=1024/eval=2048), and integration path into experiment stack.
- **Key Wikilinks**: [[RoPE]], [[Partial RoPE in Parameter Golf]], [[Parameter Golf Evaluation Tricks]], [[Parameter Golf Experiment Framework]]
- **Length**: Medium (70-90 lines)

#### Note 3: Quantization-Aware Training in Parameter Golf
- **Source**: insights.md, lines 60-64, 126-130
- **Type**: `concept-note`
- **Description**: Late QAT findings showing minimal quantization gap (0.24%) and insufficient QAT steps on A40 (43 vs 400+ needed on H100). Decision to defer optimization.
- **Key Wikilinks**: [[Parameter Golf Compression Techniques]], [[Parameter Golf Evaluation Tricks]], [[OpenAI Parameter Golf]]
- **Length**: Short (40-55 lines)

#### Note 4: GPU Compute Contention Effects
- **Source**: insights.md, lines 70-75, 97-101, 213-229
- **Type**: `full-note`
- **Description**: Analysis of parallel experiment slowdown (736ms/step → 1.39-1.74s/step), batch scaling trade-offs (524K vs 786K tokens), and the decision to favor step count over batch size on A40.
- **Key Wikilinks**: [[Parameter Golf Experiment Framework]], [[Parameter Golf Architecture Lab Experiments]], [[Capacity, Computation, and Representation in Parameter Golf]]
- **Length**: Medium (65-85 lines)

#### Note 5: SmearGate Causality Bug
- **Source**: insights.md, lines 102-106
- **Type**: `full-note`
- **Description**: Investigation of impossibly low BPB (0.0022) caused by non-causal right-neighbor mixing. Root cause analysis and fix (left-only context).
- **Key Wikilinks**: [[Parameter Golf Architecture Diagram]], [[Parameter Golf Negative Results]], [[Parameter Golf Fundamentals]]
- **Length**: Medium (55-70 lines)

#### Note 6: Layer Normalization Scaling Effects
- **Source**: insights.md, lines 174-178
- **Type**: `concept-note`
- **Description**: LN Scale as regularizer that hurts underfitting models at short step counts. Per-layer scaling (1/sqrt(layer_idx+1)) analysis.
- **Key Wikilinks**: [[Parameter Golf Architecture Diagram]], [[Parameter Golf Negative Results]], [[Parameter Golf Fundamentals]]
- **Length**: Short (35-50 lines)

#### Log: Parameter Golf Experiment Log
- **Source**: insights.md, lines 11-131 (all findings)
- **Type**: `experiment-log` (ephemeral, stays in experiments/)
- **Description**: Chronological log of all experiment findings with raw observations, hypotheses, and actions. Maintains temporal context.
- **Links to**: All 6 atomic notes above via [[Note Title]] references
- **Length**: 285 lines (preserved)

---

### From `Feature Stack Guide.md` (203 lines) → 3 atomic notes + 1 status

#### Note 7: Parameter Golf Feature Stack
- **Source**: Feature Stack Guide.md, lines 11-97
- **Type**: `full-note`
- **Description**: Layer-by-layer architecture breakdown showing where each feature acts (Initialization → Input → Attention → Residual → Training → Export → Eval). Mental model diagram.
- **Key Wikilinks**: [[Parameter Golf Architecture Diagram]], [[Partial RoPE in Parameter Golf]], [[NTK-aware RoPE]], [[SmearGate Causality Bug]], [[Quantization-Aware Training in Parameter Golf]]
- **Length**: Medium (80-100 lines)

#### Note 8: Experiment Implementation Status
- **Source**: Feature Stack Guide.md, lines 118-139
- **Type**: `concept-note`
- **Description**: What's implemented vs planned. Runnable features (XSA, EMA, Partial RoPE, SmearGate, etc.) vs doc-only (AttnRes, TTT, JEPA-lite).
- **Key Wikilinks**: [[Parameter Golf Experiment Framework]], [[Parameter Golf Architecture Diagram]], [[Attention Residuals]], [[JEPA Joint Embedding Predictive Architecture]]
- **Length**: Short (45-60 lines)

#### Note 9: Parameter Golf Experiment Policy
- **Source**: Feature Stack Guide.md, lines 141-160
- **Type**: `full-note`
- **Description**: Clean run order (10 steps from control through OrthoInit to JEPA). Rationale for ordering: architecture first, then export tricks, then research bets.
- **Key Wikilinks**: [[Parameter Golf Goal Definition]], [[Parameter Golf Experiment Framework]], [[Parameter Golf JEPA Architecture Approach]]
- **Length**: Medium (50-70 lines)

#### Status: Current Parameter Golf Runs
- **Source**: Feature Stack Guide.md, lines 162-197
- **Type**: `experiment-status` (ephemeral, stays in experiments/)
- **Description**: Live snapshot of finished controls, follow-ups, current live lane, and interrupted branches. Updates frequently.
- **Links to**: All feature notes and experiment log
- **Length**: 35 lines (preserved)

---

### From `How We Conducted Parameter Golf Experiments.md` (54 lines) → 1 atomic note

#### Note 10: Parameter Golf Methodology
- **Source**: How We Conducted Parameter Golf Experiments.md, lines 1-54
- **Type**: `full-note`
- **Description**: Canonical split (code vs vault), 7-step experiment loop, infrastructure patterns (fast path over nice path), and evolution toward high-signal notes.
- **Key Wikilinks**: [[Parameter Golf Experiment Framework]], [[OpenAI Parameter Golf]], [[Parameter Golf Negative Results]], [[Parameter Golf Evaluation Tricks]]
- **Length**: Medium (50-65 lines)

---

### From `AGENT_COORDINATION.md` (588 lines) → 8 atomic notes + 3 ephemeral

#### Note 11: Agent Coordination Protocol
- **Source**: AGENT_COORDINATION.md, lines 1-36, 344-352
- **Type**: `full-note`
- **Description**: Collaboration loop (read → claim → execute → update → record), agent roster, and shared state rules. One-change-per-experiment principle.
- **Key Wikilinks**: [[Parameter Golf Experiment Framework]], [[Multi-Agent Systems]], [[Parameter Golf Methodology]]
- **Length**: Medium (70-90 lines)

#### Note 12: Parameter Golf Compute Resources
- **Source**: AGENT_COORDINATION.md, lines 37-70, 275-288
- **Type**: `full-note`
- **Description**: RunPod 8xA40 (primary) and MI300X (secondary) specs, SSH configs, performance characteristics (A40: ~560ms/step vs H100: ~58ms/step with FA3).
- **Key Wikilinks**: [[Parameter Golf Experiment Framework]], [[GPU Compute Contention Effects]], [[Parameter Golf Methodology]]
- **Length**: Medium (80-100 lines)

#### Note 13: Parameter Golf Experiment Queue
- **Source**: AGENT_COORDINATION.md, lines 78-131
- **Type**: `full-note`
- **Description**: 3-phase strategy (Phase 1: meta stack, Phase 2: untested techniques, Phase 3: JEPA research). Running now, promotion queue, Phase 2/3 queues.
- **Key Wikilinks**: [[Parameter Golf Goal Definition]], [[Parameter Golf Experiment Policy]], [[Parameter Golf JEPA Architecture Approach]]
- **Length**: Long (110-130 lines)

#### Note 14: Parallel Swarm Experimentation
- **Source**: AGENT_COORDINATION.md, lines 285-296
- **Type**: `full-note`
- **Description**: GPU contention policy, directional signal vs clean benchmark distinction, step time stretching under load, promotion defaults (1800s for compare, 3600s for finalists).
- **Key Wikilinks**: [[GPU Compute Contention Effects]], [[Parameter Golf Experiment Framework]], [[Agent Coordination Protocol]]
- **Length**: Medium (60-80 lines)

#### Note 15: Parameter Golf Code Reference
- **Source**: AGENT_COORDINATION.md, lines 368-568
- **Type**: `full-note`
- **Description**: Complete repo structure, model architecture classes, all environment variables (42+ vars), RunPod launch commands, 16MB budget math.
- **Key Wikilinks**: [[Parameter Golf Architecture Diagram]], [[Parameter Golf Feature Stack]], [[Muon]], [[Parameter Golf Compression Techniques]]
- **Length**: Long (120-150 lines)

#### Note 16: Memory Store vs Text Coordination
- **Source**: AGENT_COORDINATION.md, lines 86-89, 211-221
- **Type**: `concept-note`
- **Description**: When to use memory store (cross-session continuity) vs shared markdown files (real-time multi-agent coordination). Thread IDs and fallback strategy.
- **Key Wikilinks**: [[Agent Coordination Protocol]], [[Parameter Golf Methodology]]
- **Length**: Short (40-55 lines)

#### Note 17: External Intelligence Integration
- **Source**: AGENT_COORDINATION.md, lines 158-191
- **Type**: `full-note`
- **Description**: PR #369 findings (FlashAttention 3 + NTK-RoPE achieving 1.1328 BPB). FA3 H100-only benefits, NTK hardware-agnostic advantages.
- **Key Wikilinks**: [[NTK-aware RoPE]], [[Parameter Golf Evaluation Tricks]], [[OpenAI Parameter Golf]]
- **Length**: Medium (65-85 lines)

#### Note 18: Artifact Synchronization Rules
- **Source**: AGENT_COORDINATION.md, lines 276-283
- **Type**: `concept-note`
- **Description**: VM as execution surface, vault as human-readable mirror, sync paths, and the contract between scratch directories and vault mirrors.
- **Key Wikilinks**: [[Parameter Golf Methodology]], [[Parameter Golf Experiment Framework]]
- **Length**: Short (35-50 lines)

#### Ephemeral 1: Agent Coordination Live Status
- **Source**: AGENT_COORDINATION.md, lines 579-588
- **Type**: `coordination-status` (ephemeral, stays in experiments/)
- **Description**: Current pod state, active runs, queue updates. Changes daily.
- **Length**: 10 lines (preserved)

#### Ephemeral 2: Memory Store Thread Registry
- **Source**: AGENT_COORDINATION.md, lines 29-36
- **Type**: `registry` (ephemeral, stays in experiments/)
- **Description**: Thread IDs for VM setup, research, and fallback. Reference for agents.
- **Length**: 8 lines (preserved)

#### Ephemeral 3: Key Reference Quick Links
- **Source**: AGENT_COORDINATION.md, lines 354-366
- **Type**: `reference-index` (ephemeral, stays in experiments/)
- **Description**: Quick links to all major vault notes for agents. Updates as notes change.
- **Length**: 13 lines (preserved)

---

## Summary: 18 New Atomic Notes + 5 Ephemeral Docs

| Source File | Lines | New Notes | Ephemeral |
|-------------|-------|-----------|-----------|
| insights.md | 285 | 6 | 1 (log) |
| Feature Stack Guide.md | 203 | 3 | 1 (status) |
| How We Conducted... | 54 | 1 | 0 |
| AGENT_COORDINATION.md | 588 | 8 | 3 |
| **TOTAL** | **1130** | **18** | **5** |

---

## 2. Concept Index Updates

### Existing Tags to Update

#### OpenAI Parameter Golf (3 - Tags/OpenAI Parameter Golf.md)
**New entries to add:**
```markdown
## Notes
- [[Partial RoPE in Parameter Golf]]
- [[NTK-aware RoPE Implementation]]
- [[Quantization-Aware Training in Parameter Golf]]
- [[GPU Compute Contention Effects]]
- [[SmearGate Causality Bug]]
- [[Layer Normalization Scaling Effects]]
- [[Parameter Golf Feature Stack]]
- [[Parameter Golf Experiment Policy]]
- [[Parameter Golf Methodology]]
- [[Agent Coordination Protocol]]
- [[Parameter Golf Compute Resources]]
- [[Parameter Golf Experiment Queue]]
- [[Parallel Swarm Experimentation]]
- [[Parameter Golf Code Reference]]
- [[Memory Store vs Text Coordination]]
- [[External Intelligence Integration]]
- [[Artifact Synchronization Rules]]
```

**New cross-references:**
```markdown
## Related Tags
- [[Experiment Methodology]]
- [[Multi-Agent Systems]]
- [[Distributed Training]]
- [[RoPE]]
- [[Quantization]]
```

#### Muon (3 - Tags/Muon.md)
**Add link:**
```markdown
## Used In
- [[Parameter Golf Code Reference]] — environment variables and optimizer configuration
```

#### Attention Residuals (3 - Tags/Attention Residuals.md)
**Add link:**
```markdown
## Implementation Status
- [[Experiment Implementation Status]] — planned but not yet runnable
```

#### JEPA Joint Embedding Predictive Architecture (3 - Tags/JEPA...md)
**Add links:**
```markdown
## Phase 3 Experiments
- [[Parameter Golf Experiment Queue]] — span-JEPA, JEPA-lite, cross-layer JEPA queue
- [[Parameter Golf JEPA Architecture Approach]] — (existing)

## Implementation
- [[Experiment Implementation Status]] — Span-JEPA and Cross-layer JEPA runnable
```

#### Semantic Tube Prediction (3 - Tags/Semantic Tube Prediction.md)
**Add link:**
```markdown
## Experiment Status
- [[Parameter Golf Experiment Queue]] — STP-lite lambda sweep planned
```

#### QK-Norm (3 - Tags/QK-Norm.md)
**Add link:**
```markdown
## Experiment Status
- [[Parameter Golf Experiment Queue]] — exp010 planned in Phase 2
```

### New Tags to Create

#### RoPE (3 - Tags/RoPE.md)
```markdown
---
tags:
  - concept-index
date: 2026-03-23
---

# RoPE (Rotary Position Embedding)

Rotary Position Embedding and its variants used in Parameter Golf experiments.

## Variants
- [[Partial RoPE in Parameter Golf]] — using partial dimensions (16/64)
- [[NTK-aware RoPE Implementation]] — dynamic base scaling for length extrapolation

## Used In
- [[Parameter Golf Architecture Diagram]]
- [[Parameter Golf Feature Stack]]
- [[SmearGate Causality Bug]] — interaction with position mixing

## Related
- [[OpenAI Parameter Golf]]
- [[Parameter Golf Fundamentals]]
```

#### Quantization (3 - Tags/Quantization.md)
```markdown
---
tags:
  - concept-index
date: 2026-03-23
---

# Quantization

Quantization techniques and findings from Parameter Golf experiments.

## Techniques
- [[Quantization-Aware Training in Parameter Golf]] — Late QAT findings
- [[Parameter Golf Compression Techniques]] — Int6, Int8, zstd compression

## Key Findings
- Minimal quant gap (0.24%) without QAT
- QAT needs 400+ steps to show effect
- Mixed int5/int6/int8 from PR #369

## Related
- [[OpenAI Parameter Golf]]
- [[Parameter Golf Evaluation Tricks]]
```

#### Multi-Agent Systems (3 - Tags/Multi-Agent Systems.md)
```markdown
---
tags:
  - concept-index
date: 2026-03-23
---

# Multi-Agent Systems

Agent coordination patterns from Parameter Golf swarm experimentation.

## Patterns
- [[Agent Coordination Protocol]] — collaboration loop and rules
- [[Memory Store vs Text Coordination]] — when to use each layer
- [[Parallel Swarm Experimentation]] — GPU contention management

## Infrastructure
- [[Parameter Golf Compute Resources]] — RunPod and MI300X setup
- [[Parameter Golf Experiment Queue]] — 3-phase experiment strategy

## Related
- [[Parameter Golf Methodology]]
- [[Parameter Golf Experiment Framework]]
```

#### Experiment Methodology (3 - Tags/Experiment Methodology.md)
```markdown
---
tags:
  - concept-index
date: 2026-03-23
---

# Experiment Methodology

Methodological patterns for ML experimentation.

## Parameter Golf Methods
- [[Parameter Golf Methodology]] — 7-step experiment loop
- [[Parameter Golf Experiment Policy]] — clean run ordering
- [[GPU Compute Contention Effects]] — parallel vs exclusive runs
- [[Artifact Synchronization Rules]] — VM/vault split

## General Patterns
- One-change-per-experiment principle
- Directional signal vs promotion distinction
- Fast path over theoretically nice path

## Related
- [[OpenAI Parameter Golf]]
- [[Multi-Agent Systems]]
```

#### Distributed Training (3 - Tags/Distributed Training.md)
```markdown
---
tags:
  - concept-index
date: 2026-03-23
---

# Distributed Training

Multi-GPU training patterns and findings.

## Parameter Golf Findings
- [[GPU Compute Contention Effects]] — single-GPU parallel slowdown
- [[Parameter Golf Compute Resources]] — 8xA40 vs 8xH100 vs MI300X
- [[SmearGate Causality Bug]] — discovered during 8-GPU DDP debugging

## Infrastructure
- NCCL configuration (IB_DISABLE, P2P_DISABLE)
- torchrun patterns
- Spot instance considerations

## Related
- [[OpenAI Parameter Golf]]
- [[Parameter Golf Experiment Framework]]
```

---

## 3. Link Graph

### New Notes → Existing Vault Notes

```
Partial RoPE in Parameter Golf
├── [[RoPE]] (new tag)
├── [[NTK-aware RoPE]]
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[Parameter Golf Architecture Diagram]] (exists)
└── [[Parameter Golf Negative Results]] (exists)

NTK-aware RoPE Implementation
├── [[RoPE]] (new tag)
├── [[Partial RoPE in Parameter Golf]]
├── [[Parameter Golf Evaluation Tricks]] (exists)
├── [[External Intelligence Integration]]
└── [[Parameter Golf Feature Stack]]

Quantization-Aware Training in Parameter Golf
├── [[Quantization]] (new tag)
├── [[Parameter Golf Compression Techniques]] (exists)
└── [[Parameter Golf Evaluation Tricks]] (exists)

GPU Compute Contention Effects
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[Parameter Golf Architecture Lab Experiments]] (exists)
├── [[Capacity, Computation, and Representation in Parameter Golf]] (exists)
├── [[Parallel Swarm Experimentation]]
└── [[Parameter Golf Compute Resources]]

SmearGate Causality Bug
├── [[Parameter Golf Architecture Diagram]] (exists)
├── [[Parameter Golf Negative Results]] (exists)
└── [[RoPE]] (new tag)

Layer Normalization Scaling Effects
├── [[Parameter Golf Architecture Diagram]] (exists)
└── [[Parameter Golf Negative Results]] (exists)

Parameter Golf Feature Stack
├── [[Parameter Golf Architecture Diagram]] (exists)
├── [[Partial RoPE in Parameter Golf]]
├── [[NTK-aware RoPE]]
├── [[SmearGate Causality Bug]]
├── [[Quantization-Aware Training in Parameter Golf]]
├── [[Experiment Implementation Status]]
└── [[Parameter Golf Experiment Policy]]

Experiment Implementation Status
├── [[Parameter Golf Architecture Diagram]] (exists)
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[Attention Residuals]] (exists)
└── [[JEPA Joint Embedding Predictive Architecture]] (exists)

Parameter Golf Experiment Policy
├── [[Parameter Golf Goal Definition]] (exists)
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[Parameter Golf JEPA Architecture Approach]] (exists)
└── [[Parameter Golf Experiment Queue]]

Parameter Golf Methodology
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[OpenAI Parameter Golf]] (exists)
├── [[Parameter Golf Negative Results]] (exists)
└── [[Agent Coordination Protocol]]

Agent Coordination Protocol
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[Multi-Agent Systems]] (new tag)
└── [[Parameter Golf Methodology]]

Parameter Golf Compute Resources
├── [[Parameter Golf Experiment Framework]] (exists)
├── [[GPU Compute Contention Effects]]
└── [[Parameter Golf Methodology]]

Parameter Golf Experiment Queue
├── [[Parameter Golf Goal Definition]] (exists)
├── [[Parameter Golf Experiment Policy]]
├── [[Parameter Golf JEPA Architecture Approach]] (exists)
├── [[Semantic Tube Prediction]] (exists)
└── [[QK-Norm]] (exists)

Parallel Swarm Experimentation
├── [[GPU Compute Contention Effects]]
├── [[Parameter Golf Experiment Framework]] (exists)
└── [[Agent Coordination Protocol]]

Parameter Golf Code Reference
├── [[Parameter Golf Architecture Diagram]] (exists)
├── [[Parameter Golf Feature Stack]]
├── [[Muon]] (exists)
└── [[Parameter Golf Compression Techniques]] (exists)

Memory Store vs Text Coordination
├── [[Agent Coordination Protocol]]
└── [[Parameter Golf Methodology]]

External Intelligence Integration
├── [[NTK-aware RoPE]]
├── [[Parameter Golf Evaluation Tricks]] (exists)
└── [[OpenAI Parameter Golf]] (exists)

Artifact Synchronization Rules
├── [[Parameter Golf Methodology]]
└── [[Parameter Golf Experiment Framework]] (exists)
```

### Hub Notes (High Connectivity)

**Tier 1 Hubs** (connect 8+ new notes):
1. **Parameter Golf Experiment Framework** (exists) — connects 10 new notes
2. **OpenAI Parameter Golf** (exists, tag) — connects 14 new notes

**Tier 2 Hubs** (connect 4-7 new notes):
1. **Parameter Golf Architecture Diagram** (exists) — connects 6 new notes
2. **Agent Coordination Protocol** — connects 5 new notes
3. **Parameter Golf Methodology** — connects 5 new notes

**New Hubs**:
1. **Parameter Golf Feature Stack** — connects 7 other new notes
2. **GPU Compute Contention Effects** — connects 4 other new notes

### Tag Connections

```
OpenAI Parameter Golf (central tag)
├── [[RoPE]] (new)
├── [[Quantization]] (new)
├── [[Multi-Agent Systems]] (new)
├── [[Experiment Methodology]] (new)
├── [[Distributed Training]] (new)
├── [[Muon]] (exists)
├── [[Attention Residuals]] (exists)
├── [[JEPA Joint Embedding Predictive Architecture]] (exists)
├── [[Semantic Tube Prediction]] (exists)
└── [[QK-Norm]] (exists)
```

---

## 4. Migration Priority Order

### Phase 1: Quick Wins (1-2 hours)
**Criteria**: Single-source, low dependency, high reuse value

1. **Parameter Golf Methodology** (Note 10)
   - Single source file, clean extraction
   - Links to existing framework note
   - Foundational for understanding experiment approach

2. **SmearGate Causality Bug** (Note 5)
   - Self-contained finding
   - High pedagogical value (debugging story)
   - Links naturally to architecture diagram

3. **Quantization-Aware Training in Parameter Golf** (Note 3)
   - Clear decision documented (defer QAT)
   - Short note, easy to extract
   - Connects to existing compression note

### Phase 2: High Value (2-4 hours)
**Criteria**: Multiple dependencies, high connectivity, reusable patterns

4. **Partial RoPE in Parameter Golf** (Note 1)
   - Rich data (tables, curves)
   - Connects to NTK note and RoPE tag
   - Key architectural finding

5. **Parameter Golf Feature Stack** (Note 7)
   - Central hub note
   - Links many other notes together
   - Essential reference for experiment design

6. **Agent Coordination Protocol** (Note 11)
   - Critical for multi-agent work
   - Links to methodology and framework
   - Enables future swarm experiments

7. **Parameter Golf Compute Resources** (Note 12)
   - Practical reference
   - Connects contention findings
   - Needed for experiment planning

### Phase 3: Deep Cuts (4-6 hours)
**Criteria**: Long notes, complex cross-references, synthesis required

8. **NTK-aware RoPE Implementation** (Note 2)
   - Merges content from insights.md and AGENT_COORDINATION.md
   - Complex integration with PR #369 findings
   - Links to external intelligence note

9. **Parameter Golf Experiment Queue** (Note 13)
   - Long note (110-130 lines expected)
   - Complex table formatting
   - Links to many existing Phase 2/3 concepts

10. **Parameter Golf Code Reference** (Note 15)
    - Very long note (120-150 lines expected)
    - 42+ environment variables
    - Critical reference but dense

11. **GPU Compute Contention Effects** (Note 4)
    - Synthesizes findings from multiple sources
    - Requires careful data table extraction
    - Key insight for experiment design

12. **Parallel Swarm Experimentation** (Note 14)
    - Policy-oriented synthesis
    - Links contention and coordination
    - Important for methodology

### Phase 4: Supporting Notes (2-3 hours)
**Criteria**: Shorter notes, fill in gaps

13. **Layer Normalization Scaling Effects** (Note 6)
    - Short concept note
    - Links to negative results

14. **Experiment Implementation Status** (Note 8)
    - Status tracking note
    - Links to JEPA and AttnRes tags

15. **Parameter Golf Experiment Policy** (Note 9)
    - Policy synthesis
    - Links queue and framework

16. **Memory Store vs Text Coordination** (Note 16)
    - Meta-observation about agent tools
    - Short but important distinction

17. **External Intelligence Integration** (Note 17)
    - PR #369 synthesis
    - Links to NTK and evaluation tricks

18. **Artifact Synchronization Rules** (Note 18)
    - Infrastructure note
    - Short, procedural

---

## 5. Implementation Notes

### Refactoring in Existing Notes

#### Parameter Golf Experiment Framework.md
- **Line 211-221**: Add link to new [[Memory Store vs Text Coordination]] note
- **Line 343-351**: Expand "See also" to include new notes:
  ```markdown
  - [[Parameter Golf Methodology]]
  - [[Agent Coordination Protocol]]
  - [[Parameter Golf Feature Stack]]
  ```

#### OpenAI Parameter Golf.md (tag)
- Add all 18 new notes to Notes section (as specified in Section 2)
- Add 5 new related tags

#### Parameter Golf Architecture Diagram.md
- Add links to new architecture-related notes:
  - [[Partial RoPE in Parameter Golf]]
  - [[SmearGate Causality Bug]]
  - [[Layer Normalization Scaling Effects]]
  - [[Parameter Golf Feature Stack]]

### Wikilink Conventions

**Use exact note titles in wikilinks:**
- `[[Partial RoPE in Parameter Golf]]` — not `[[partial rope]]` or `[[RoPE partial]]`
- `[[NTK-aware RoPE Implementation]]` — not `[[NTK RoPE]]`
- `[[GPU Compute Contention Effects]]` — not `[[GPU contention]]`

**For tags, use tag path:**
- `[[OpenAI Parameter Golf]]` — links to 3 - Tags/OpenAI Parameter Golf.md
- `[[RoPE]]` — will link to 3 - Tags/RoPE.md (new)

**Cross-link liberally:**
- Every note should have 5-15 wikilinks
- Link to both existing and new notes
- Link to relevant tags

### Frontmatter Templates

#### Full Note Template:
```yaml
---
tags:
  - full-note
date: 2026-03-23
---

# Note Title

## Overview
1-2 paragraph summary

## Key Content
Main body (55-130 lines total)

## Key Findings (optional)
- Bullet point discoveries

## Notes
Important caveats or context

## Related Concepts
- [[Link 1]]
- [[Link 2]]

## Key Papers (if applicable)
- Power et al. 2022 on grokking
- PR #369 competition submission

## Open Questions (optional)
- Future investigation directions
```

#### Concept Note Template:
```yaml
---
tags:
  - concept-note
date: 2026-03-23
---

# Concept Name

Brief definition (2-3 sentences).

## How It Works
Mechanism explanation.

## Key Properties
- Property 1
- Property 2

## Notes
Caveats, limitations, or special cases.

## Related Concepts
- [[Link 1]]
- [[Link 2]]
```

#### Tag Template (Concept Index):
```yaml
---
tags:
  - concept-index
date: 2026-03-23
---

# Tag Name

Brief description of concept domain.

## Sub-concepts / Variants
- [[Note 1]]
- [[Note 2]]

## Used In
- [[Note 3]]
- [[Note 4]]

## Related Tags
- [[Related Tag 1]]
- [[Related Tag 2]]
```

### File Locations

**New atomic notes:**
- Place all 18 notes in `a3fckx/4 - Full Notes/`
- Use Title Case for filenames: `Partial RoPE in Parameter Golf.md`

**New tags:**
- Place all 5 new tags in `a3fckx/3 - Tags/`
- Use concise names: `RoPE.md`, `Quantization.md`

**Ephemeral docs (stay in experiments/):**
- `insights.md` → keep as experiment log
- `Feature Stack Guide.md` → archive after notes extracted
- `AGENT_COORDINATION.md` → archive after notes extracted
- `How We Conducted...` → archive after note extracted

### Migration Checklist

**Before starting:**
- [ ] Backup experiments/ folder
- [ ] Verify all target existing notes are readable
- [ ] Create new tag files first (for wikilink validation)

**During migration:**
- [ ] Create notes in Phase order (1 → 2 → 3 → 4)
- [ ] Add wikilinks as you write (not after)
- [ ] Update tag files incrementally
- [ ] Test 3-5 random wikilinks in Obsidian after each note

**After migration:**
- [ ] Verify all 18 notes render correctly in Obsidian
- [ ] Check that 5 ephemeral docs still work in experiments/
- [ ] Update existing notes with new backlinks
- [ ] Archive or mark source files as "consolidated"
- [ ] Record completion to memory store

### Success Criteria

- All 18 atomic notes created with proper frontmatter
- All 5 new tags created and populated
- Average 8-12 wikilinks per new note
- All source files archived or marked consolidated
- No broken wikilinks in Obsidian graph view
- Ephemeral docs still functional for active coordination
