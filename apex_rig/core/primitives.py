"""
apex_rig.core.primitives
~~~~~~~~~~~~~~~~~~~~~~~~

Core domain primitives, descriptors, and typed telemetry schemas for Apex Rig.
Standard library only; zero external dependencies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import time


class HarnessType(str, Enum):
    LEAD_REASONER = "lead_reasoner"
    CLAUDE_CODE = "claude_code"
    AIDER = "aider"
    OPENHANDS = "openhands"
    AST_VERIFIER = "ast_verifier"
    MOCK = "mock"


class HarnessState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class ModelTier(str, Enum):
    LOCAL_SILICON = "local_silicon"       # 0.5B - 8B on-device quantized (GGUF / MLX)
    COMMODITY_CLOUD = "commodity_cloud"   # DeepSeek-V3, Llama-3.3-70B, Qwen
    FRONTIER_CLOUD = "frontier_cloud"     # Claude 3.5 Sonnet, GPT-4o, DeepSeek-R1


@dataclass(frozen=True)
class ModelDescriptor:
    model_id: str
    provider: str
    tier: ModelTier
    context_limit: int
    input_cost_per_m: float       # USD per 1M tokens
    output_cost_per_m: float      # USD per 1M tokens
    avg_latency_ms: float
    param_count_b: float
    quant_level: str = "FP16"


@dataclass
class TaskSpec:
    task_id: str
    prompt: str
    priority: int = 100           # Lower value = higher priority
    required_capability: str = "general"
    context_prefix: str = ""
    max_tokens: int = 4096
    budget_usd: float = 0.50
    created_at: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    task_id: str
    status: str                   # "completed", "failed", "rolled_back"
    output_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    provider: str
    model_id: str
    harness_id: str
    speculative_accepted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessDescriptor:
    harness_id: str
    harness_type: HarnessType
    state: HarnessState = HarnessState.IDLE
    current_task_id: Optional[str] = None
    active_context_tokens: int = 0
    resident_memory_mb: float = 0.0
    tasks_completed: int = 0
    uptime_sec: float = 0.0


@dataclass
class RoutingDecision:
    task_id: str
    chosen_model: ModelDescriptor
    estimated_entropy: float
    routing_latency_ms: float
    reason: str
    fallback_models: List[str] = field(default_factory=list)


@dataclass
class HardwareTelemetry:
    host_os: str
    total_ram_mb: float
    free_ram_mb: float
    total_vram_mb: float
    free_vram_mb: float
    compute_device: str
    active_kv_cache_mb: float
    memory_growth_rate_mb_s: float
    projected_headroom_sec: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class JournalEntry:
    entry_id: str
    harness_id: str
    file_path: str
    action: str                   # "create", "modify", "delete"
    original_content_hash: str
    new_content_hash: str
    diff_payload: str
    committed: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class EvolutionGenome:
    entropy_thresh_local: float       # Below this -> Local Silicon
    entropy_thresh_frontier: float    # Above this -> Frontier Cloud
    cost_weight: float                # 0.0 - 1.0 importance of price
    latency_weight: float             # 0.0 - 1.0 importance of latency
    vram_eviction_watermark: float    # 0.50 - 0.95 capacity trigger
    speculative_depth: int            # 1 - 8 lookahead depth
    poll_interval_ms: float           # 10.0 - 500.0 ms telemetry rate
    generation: int = 0
    fitness_score: float = 0.0
