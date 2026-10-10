"""
apex_rig.orchestrator
~~~~~~~~~~~~~~~~~~~~~

ApexRigOrchestrator: The sovereign coordination loop uniting multi-harness swarms,
entropy-governed model routing, dynamic silicon VRAM memory horizon, and enterprise adapters.
"""

from typing import Dict, List, Optional, Any, Tuple
import time

from apex_rig.core.primitives import (
    TaskSpec,
    TaskResult,
    RoutingDecision,
    HardwareTelemetry,
    ModelTier,
    HarnessType,
)
from apex_rig.core.radix_trie import PrefixRadixTrie
from apex_rig.core.entropy_router import EntropyRouter
from apex_rig.core.vram_projector import VRAMProjector
from apex_rig.core.workspace_journal import WorkspaceJournal
from apex_rig.core.evolution_engine import RigEvolutionEngine

from apex_rig.harness.process_supervisor import ProcessSupervisor
from apex_rig.harness.mock_harness import MockHarness
from apex_rig.harness.claude_code_harness import ClaudeCodeHarness
from apex_rig.harness.aider_harness import AiderHarness
from apex_rig.harness.openhands_harness import OpenHandsHarness

from apex_rig.router.key_pooler import KeyPooler
from apex_rig.router.latency_arbiter import LatencyArbiter
from apex_rig.router.bedrock_bridge import BedrockBridge
from apex_rig.router.openrouter_bridge import OpenRouterBridge

from apex_rig.silicon.hardware_prober import HardwareProber
from apex_rig.silicon.llmfit_engine import LLMFitEngine
from apex_rig.silicon.local_runner import LocalRunner

from apex_rig.adapters.firmware_adapter import FirmwareAdapter
from apex_rig.adapters.contextfabric_adapter import ContextFabricAdapter
from apex_rig.adapters.specagent_adapter import SpecAgentAdapter
from apex_rig.adapters.decisioncore_adapter import DecisionCoreAdapter
from apex_rig.adapters.capitalmatrix_adapter import CapitalMatrixAdapter


class ApexRigOrchestrator:
    """
    Master coordination engine for Apex Rig.
    """

    def __init__(
        self,
        auto_initialize: bool = True,
        total_vram_mb: float = 24576.0,
    ):
        # 1. Mathematical Core
        self.radix_trie = PrefixRadixTrie()
        self.entropy_router = EntropyRouter()
        self.vram_projector = VRAMProjector(total_vram_mb=total_vram_mb)
        self.journal = WorkspaceJournal()
        self.evolution_engine = RigEvolutionEngine()

        # 2. Multi-Harness Supervisor
        self.supervisor = ProcessSupervisor()

        # 3. Router & Balancer
        self.key_pooler = KeyPooler()
        self.latency_arbiter = LatencyArbiter()
        self.bedrock_bridge = BedrockBridge()
        self.openrouter_bridge = OpenRouterBridge()

        # 4. Silicon & Hardware
        self.hardware_prober = HardwareProber()
        self.llmfit_engine = LLMFitEngine(host_vram_mb=total_vram_mb)
        self.local_runner = LocalRunner()

        # 5. Enterprise Grid Adapters
        self.firmware_adapter = FirmwareAdapter()
        self.contextfabric_adapter = ContextFabricAdapter()
        self.specagent_adapter = SpecAgentAdapter()
        self.decisioncore_adapter = DecisionCoreAdapter()
        self.capitalmatrix_adapter = CapitalMatrixAdapter()

        if auto_initialize:
            self._bootstrap_rig()

    def _bootstrap_rig(self) -> None:
        """Initializes default harnesses, credential slots, and system probes."""
        # Register standard harnesses
        self.supervisor.register_harness(ClaudeCodeHarness("claude-01"))
        self.supervisor.register_harness(AiderHarness("aider-01"))
        self.supervisor.register_harness(OpenHandsHarness("openhands-01"))
        self.supervisor.register_harness(MockHarness("mock-fast-01", synthetic_latency_ms=1.0))

        # Register credential slots
        self.key_pooler.register_key("anthropic", "ant-key-01", "sk-ant-prod-key-1111", max_rpm=120)
        self.key_pooler.register_key("deepseek", "ds-key-01", "sk-ds-prod-key-2222", max_rpm=200)
        self.key_pooler.register_key("aws_bedrock", "aws-key-01", "AKIA-PROD-KEY-3333", max_rpm=300)

    def submit_task(
        self,
        prompt: str,
        task_id: Optional[str] = None,
        context_prefix: str = "",
        priority: int = 100,
        budget_usd: float = 0.50,
        harness_override: Optional[str] = None,
    ) -> Tuple[TaskResult, RoutingDecision, Dict[str, Any]]:
        """
        Executes a task across the sovereign multi-layer pipeline:
        1. Context deduplication via PrefixRadixTrie
        2. Sub-2ms Shannon entropy classification & routing
        3. Dynamic VRAM horizon check & potential KV-cache spill
        4. Power delivery pacing with apex-firmware
        5. Execution via selected harness
        6. FinOps logging via apex-capitalmatrix
        """
        tid = task_id or f"task_{int(time.time() * 1000)}"
        task = TaskSpec(
            task_id=tid,
            prompt=prompt,
            context_prefix=context_prefix,
            priority=priority,
            budget_usd=budget_usd,
        )

        # 1. Deduplicate Context Prefix
        prefix_hash, shared_tok, unique_tok = self.radix_trie.register_prefix(context_prefix, "orchestrator")

        # 2. Entropy Routing
        routing_decision = self.entropy_router.route_task(task)

        # 3. Dynamic Memory Horizon Check
        active_kv_mb = VRAMProjector.estimate_kv_cache_size_mb(
            context_tokens=shared_tok + unique_tok + (len(prompt) // 4)
        )
        telemetry = self.vram_projector.record_sample(
            allocated_vram_mb=8192.0 + active_kv_mb,
            active_kv_cache_mb=active_kv_mb,
        )
        needs_spill, excess_mb = self.vram_projector.should_evict(telemetry.total_vram_mb - telemetry.free_vram_mb)
        if needs_spill:
            self.contextfabric_adapter.trigger_kv_spill("orchestrator", excess_mb)

        # 4. Silicon Power Pacing
        active_harnesses = len(self.supervisor.list_harnesses())
        stagger_us = self.firmware_adapter.calculate_batch_pacing_us(active_harnesses)

        # 5. Acquire Credential from Key Pooler
        key_slot = self.key_pooler.acquire_key(routing_decision.chosen_model.provider, requested_tokens=500)

        # 6. Execute Task via Supervisor
        target_harness = harness_override
        if not target_harness:
            if routing_decision.chosen_model.tier == ModelTier.LOCAL_SILICON:
                target_harness = "mock-fast-01"
            elif routing_decision.chosen_model.tier == ModelTier.FRONTIER_CLOUD:
                target_harness = "claude-01"
            else:
                target_harness = "aider-01"

        result = self.supervisor.execute_immediate(task, preferred_harness_id=target_harness)

        # 7. Record FinOps Expenditure
        finops_entry = self.capitalmatrix_adapter.record_expenditure(
            model_id=routing_decision.chosen_model.model_id,
            tokens=result.input_tokens + result.output_tokens,
            cost_usd=result.cost_usd,
        )

        metadata = {
            "prefix_hash": prefix_hash,
            "shared_tokens": shared_tok,
            "unique_tokens": unique_tok,
            "tokens_saved_ratio": self.radix_trie.get_deduplication_ratio(),
            "vram_headroom_sec": telemetry.projected_headroom_sec,
            "stagger_pacing_us": stagger_us,
            "key_used": key_slot.key_id if key_slot else "local",
            "finops": finops_entry,
        }

        return (result, routing_decision, metadata)

    def evolve_hyperparameters(self, generations: int = 3) -> Dict[str, Any]:
        """Runs Pareto evolutionary optimization for Rig parameters."""
        for gen in range(generations):
            self.evolution_engine.evolve_generation(
                eval_fn=lambda g: self.evolution_engine.evaluate_fitness(
                    genome=g,
                    simulated_throughput=85.0,
                    simulated_cost_usd=0.08,
                    oom_penalty=0.0,
                ),
                generation_idx=gen,
            )

        best = self.evolution_engine.best_genome
        # Apply evolved parameters to active router
        self.entropy_router.local_threshold = best.entropy_thresh_local
        self.entropy_router.frontier_threshold = best.entropy_thresh_frontier
        self.entropy_router.cost_weight = best.cost_weight
        self.entropy_router.latency_weight = best.latency_weight

        return {
            "best_generation": best.generation,
            "best_fitness": best.fitness_score,
            "evolved_local_threshold": best.entropy_thresh_local,
            "evolved_frontier_threshold": best.entropy_thresh_frontier,
            "evolved_cost_weight": best.cost_weight,
            "evolved_latency_weight": best.latency_weight,
            "evolved_vram_watermark": best.vram_eviction_watermark,
        }

    def get_mesh_status(self) -> Dict[str, Any]:
        return {
            "harnesses": [h.__dict__ for h in self.supervisor.list_harnesses()],
            "radix_dedup": self.radix_trie.get_metrics(),
            "key_pools": self.key_pooler.get_status(),
            "hardware": self.hardware_prober.probe(),
            "finops_cumulative_spend": self.capitalmatrix_adapter.cumulative_spend_usd,
            "firmware_droop_mv": self.firmware_adapter.get_pdn_health()["peak_droop_mv"],
        }
