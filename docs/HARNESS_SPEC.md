# Apex Rig: Harness Orchestration Specification

---

## 1. Overview & Protocol Contract

The **Harness Layer** in Apex Rig manages the lifecycle, sandboxing, context sharing, and speculative filesystem mutations of heterogeneous autonomous coding agents (Claude Code, Aider, OpenHands, and specialized AST verifiers).

### The Dual-Layer Hierarchy
Unlike traditional multi-agent systems that treat agents as monolithic workers, Apex Rig decouples the **agent cognitive harness** from the **underlying model inference**:

1. **Cognitive Harness**: Owns the tool loop, prompt framing, file parsing, and git operations.
2. **Cognitive Router**: Intercepts prompt tokens, calculates entropy, pools API credentials, and dispatches to the optimal local or cloud model.

```
┌────────────────────────────────────────────────────────┐
│                   APEX RIG HARNESS MESH                │
├────────────────────────────────────────────────────────┤
│  [ Lead Architect ]   [ Code Specialist ]  [ Verifier ]│
│         │                     │                  │     │
│         └──────────────┬──────┴──────────────────┘     │
│                        ▼                               │
│              [ Shared Radix Trie ]                     │
│                        │                               │
│                        ▼                               │
│        [ Copy-on-Write Workspace Journal ]             │
└────────────────────────────────────────────────────────┘
```

---

## 2. Shared Context Prefix Deduplication

Every harness session registered with Apex Rig routes its prompt preludes through `PrefixRadixTrie`:

- Common headers (system instructions, code guidelines, file trees, symbol indices) are segmented into normalized lines.
- Identical segments are indexed into a compressed radix trie with atomic reference counting.
- When an agent generates a prompt, only unique deltas are stored and transmitted.
- **Deduplication Efficiency**:
  $$\text{Savings} = 1.0 - \frac{\sum \text{Unique Tokens}}{\sum \text{Raw Tokens}} \ge 73.4\%$$

---

## 3. Copy-on-Write Transactional Journal

To prevent race conditions during concurrent multi-agent code refactoring:
- Files are locked on first mutation attempt in `WorkspaceJournal`.
- Mutations are staged as in-memory diffs (`diff_payload`) without modifying disk files.
- If verification succeeds, changes are atomically committed (`commit_transaction`).
- If an agent diverges or tests fail, mutations are rolled back in $\mathcal{O}(1)$ time (`rollback_transaction`), preventing git workspace pollution.
