# Architecture Manual: Apex Rig (`apex-rig`)

---

## 1. System Design Principles

Apex Rig implements the sovereign architecture for high-concurrency autonomous agent swarms:

1. **Zero External Dependencies**: Implemented entirely with Python 3.9+ standard library (`dataclasses`, `heapq`, `collections`, `hashlib`, `math`, `subprocess`).
2. **Deterministic Sandboxing**: All agent harness file writes are staged through copy-on-write AST journals. Diffs are verified before committing.
3. **Decoupled Cognitive Arbitration**: The harness does not decide the model; the entropy router predicts the optimal model tier based on token information density.
4. **Hardware-Coupled Memory Protection**: KV-cache growth rate $\frac{dM}{dt}$ is actively monitored to prevent OOM panics before they happen.

---

## 2. Layered Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      APEX RIG ORCHESTRATOR                      │
├────────────────────────────────┬────────────────────────────────┤
│       HARNESS MESH             │       COGNITIVE ROUTER         │
│ • ClaudeCodeHarness            │ • EntropyRouter (Shannon H(X)) │
│ • AiderHarness                 │ • KeyPooler (Multi-Account)    │
│ • OpenHandsHarness             │ • LatencyArbiter (Outlier P95) │
│ • PrefixRadixTrie              │ • BedrockBridge / OpenRouter   │
├────────────────────────────────┼────────────────────────────────┤
│       SILICON FABRIC           │       ENTERPRISE ADAPTERS      │
│ • HardwareProber               │ • FirmwareAdapter (apex-fw)    │
│ • LLMFitEngine                 │ • ContextFabricAdapter (KV)    │
│ • VRAMProjector (dM/dt)        │ • SpecAgentAdapter (Rollback)  │
│ • LocalRunner (MPS/CPU)        │ • CapitalMatrixAdapter (FinOps)│
└────────────────────────────────┴────────────────────────────────┘
```

---

## 3. Algorithmic Complexity Guarantees

- **Prefix Lookup & Registration**: $\mathcal{O}(K)$ where $K$ is the segment count.
- **Entropy Classification & Routing**: $\mathcal{O}(N)$ where $N$ is token count; completes in $< 10\,\mu\text{s}$.
- **VRAM Horizon Derivative**: $\mathcal{O}(1)$ via circular ring buffer.
- **Speculative Rollback**: $\mathcal{O}(1)$ via pointer discard in `WorkspaceJournal`.
