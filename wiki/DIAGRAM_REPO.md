# Diagram Repository: Apex Rig (`apex-rig`)

---

## 1. Macro-System Component Graph

```mermaid
graph TD
    classDef slate fill:#1e293b,stroke:#475569,stroke-width:1px,color:#f8fafc;
    classDef edgeLabel fill:#0f172a,stroke:#334155,color:#94a3b8;

    Client["Client / IDE / CLI"]:::slate
    Orch["ApexRigOrchestrator"]:::slate

    subgraph HarnessSubsystem ["Multi-Harness Subsystem"]
        Sup["ProcessSupervisor"]:::slate
        Trie["PrefixRadixTrie"]:::slate
        Journ["WorkspaceJournal"]:::slate
    end

    subgraph RoutingSubsystem ["Cognitive Router Subsystem"]
        Ent["EntropyRouter"]:::slate
        Pool["KeyPooler"]:::slate
        Arb["LatencyArbiter"]:::slate
    end

    subgraph SiliconSubsystem ["Silicon & Memory Subsystem"]
        Fit["LLMFitEngine"]:::slate
        VRAM["VRAMProjector"]:::slate
        Run["LocalRunner"]:::slate
    end

    subgraph GridAdapters ["Enterprise Grid & Ecosystem Adapters"]
        FW["FirmwareAdapter (apex-firmware)"]:::slate
        CF["ContextFabricAdapter (apex-contextfabric)"]:::slate
        CM["CapitalMatrixAdapter (apex-capitalmatrix)"]:::slate
        SN["StarNetAdapter (Desktop Station)"]:::slate
        HD["HeraldOSAdapter (Hermes Agent)"]:::slate
        PC["PaperclipAdapter (Company OS)"]:::slate
        TP["TelepathyBusAdapter (IPC Ring)"]:::slate
        IK["ImmuneKernelAdapter (Zero-Trust)"]:::slate
        AD["AgentDiffAdapter (AST Validator)"]:::slate
    end

    Client --> Orch
    Orch --> Sup & Ent & Fit
    Sup --> Trie & Journ
    Ent --> Pool & Arb
    Fit --> VRAM & Run
    Orch --> FW & CF & CM & SN & HD & PC & TP & IK & AD
```

---

## 2. Sub-Millisecond Task Arbitration Sequence ($\le 5$ Lifelines)

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Developer
    participant Rig as Apex Rig
    participant Router as Entropy Router
    participant Silicon as Silicon Engine
    participant Target as Target Model

    Dev->>Rig: Submit Prompt Task
    Rig->>Router: Classify Shannon Entropy
    Router->>Silicon: Check VRAM Headroom
    alt Entropy Low & Fits Local
        Silicon->>Target: Dispatch to Local LPU (0ms latency)
    else High Entropy
        Router->>Target: Dispatch to Frontier API (Pooled Key)
    end
    Target-->>Rig: Return Validated Result
    Rig-->>Dev: Stream Output & FinOps Metrics
```

---

## 3. Paperclip Employee Governance & Herald Mission Flow ($\le 5$ Lifelines)

```mermaid
sequenceDiagram
    autonumber
    actor User as Herald OS User
    participant Herald as Herald OS Bridge
    participant Rig as Apex Rig Mesh
    participant Paperclip as Paperclip Corp OS
    participant Diff as Agent Diff Scanner

    User->>Herald: Submit Mission Directive
    Herald->>Rig: Initialize Task Spec
    Rig->>Paperclip: Verify Employee Budget & Clearance
    alt Budget Exceeded or Unauthorized
        Paperclip-->>Rig: Halt Task (Budget Exceeded)
    else Budget Approved
        Rig->>Diff: Scan Staged AST Diff & Blast Radius
        Diff-->>Rig: Diff Approved (Guards Intact)
        Rig->>Paperclip: Record Payroll Spend
        Rig-->>Herald: Mission Completed
    end
```

---

## 4. Speculative Workspace Transaction State Machine

```mermaid
stateDiagram-v2
    direction TB
    [*] --> Idle: Harness Ready
    Idle --> Staging: Mutate Code File
    Staging --> ConflictCheck: Verify Path Lock
    
    state TransactionState {
        ConflictCheck --> Validated: No Lock Collision
        ConflictCheck --> Aborted: Conflict Detected
        Validated --> ASTVerification: Run Static Tests
        ASTVerification --> Committed: All Tests Pass
        ASTVerification --> Rollback: Test Failure / Anomaly
    }

    Committed --> [*]: Flush to Git
    Rollback --> [*]: O(1) Discard in Journal
    Aborted --> [*]: Prompt Retry
```
