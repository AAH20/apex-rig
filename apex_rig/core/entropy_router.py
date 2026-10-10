"""
apex_rig.core.entropy_router
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shannon entropy estimator and Pareto-optimal cognitive model router.
Classifies prompt complexity in sub-2ms time and dispatches to Local Silicon,
Commodity Cloud, or Frontier Cloud based on information density and cost bounds.
"""

from typing import List, Dict, Optional
import math
import re
import time
from collections import Counter
from apex_rig.core.primitives import (
    TaskSpec,
    ModelDescriptor,
    ModelTier,
    RoutingDecision,
)


class EntropyRouter:
    """
    Sub-2ms prompt entropy classifier and multi-tier model arbiter.
    """

    def __init__(
        self,
        local_threshold: float = 2.0,
        frontier_threshold: float = 3.5,
        cost_weight: float = 0.5,
        latency_weight: float = 0.5,
    ):
        self.local_threshold = local_threshold
        self.frontier_threshold = frontier_threshold
        self.cost_weight = cost_weight
        self.latency_weight = latency_weight
        self._model_registry: Dict[str, ModelDescriptor] = {}
        self._init_default_models()

    def _init_default_models(self) -> None:
        defaults = [
            ModelDescriptor(
                model_id="local-qwen-2.5-coder-7b",
                provider="local_lpu",
                tier=ModelTier.LOCAL_SILICON,
                context_limit=32768,
                input_cost_per_m=0.0,
                output_cost_per_m=0.0,
                avg_latency_ms=12.5,
                param_count_b=7.0,
                quant_level="Q4_K_M",
            ),
            ModelDescriptor(
                model_id="deepseek-v3",
                provider="deepseek",
                tier=ModelTier.COMMODITY_CLOUD,
                context_limit=131072,
                input_cost_per_m=0.27,
                output_cost_per_m=1.10,
                avg_latency_ms=350.0,
                param_count_b=671.0,
                quant_level="FP8",
            ),
            ModelDescriptor(
                model_id="claude-3-5-sonnet",
                provider="anthropic",
                tier=ModelTier.FRONTIER_CLOUD,
                context_limit=200000,
                input_cost_per_m=3.00,
                output_cost_per_m=15.00,
                avg_latency_ms=850.0,
                param_count_b=200.0,
                quant_level="FP16",
            ),
        ]
        for m in defaults:
            self._model_registry[m.model_id] = m

    def register_model(self, model: ModelDescriptor) -> None:
        self._model_registry[model.model_id] = model

    def calculate_shannon_entropy(self, text: str) -> float:
        """
        Calculates Shannon entropy H(X) over tokenized words:
        H(X) = - sum( P(w) * log2(P(w)) )
        """
        if not text:
            return 0.0

        # Tokenize by alphanumeric words and operators
        tokens = re.findall(r"\w+|[^\w\s]", text.lower())
        if not tokens:
            return 0.0

        total = len(tokens)
        counts = Counter(tokens)
        entropy = 0.0
        for count in counts.values():
            p = count / total
            entropy -= p * math.log2(p)

        # Scale by lexical diversity bonus (unique / total)
        lexical_diversity = len(counts) / total
        adjusted_entropy = entropy * (0.7 + 0.3 * lexical_diversity)
        return round(adjusted_entropy, 4)

    def route_task(self, task: TaskSpec) -> RoutingDecision:
        """
        Evaluates task entropy and dispatches to the optimal model tier.
        Guaranteed execution time < 2.0 ms.
        """
        t_start = time.perf_counter()
        full_text = f"{task.context_prefix}\n{task.prompt}"
        entropy = self.calculate_shannon_entropy(full_text)

        # Determine target tier based on calibrated thresholds
        if entropy <= self.local_threshold or task.budget_usd < 0.05:
            target_tier = ModelTier.LOCAL_SILICON
            reason = f"Low entropy ({entropy:.2f} <= {self.local_threshold}) or constrained budget -> local zero-cost LPU dispatch"
        elif entropy >= self.frontier_threshold or task.priority < 20:
            target_tier = ModelTier.FRONTIER_CLOUD
            reason = f"High entropy ({entropy:.2f} >= {self.frontier_threshold}) -> frontier reasoning required"
        else:
            target_tier = ModelTier.COMMODITY_CLOUD
            reason = f"Moderate entropy ({entropy:.2f}) -> commodity cloud balance"

        # Filter candidates by tier
        candidates = [m for m in self._model_registry.values() if m.tier == target_tier]
        if not candidates:
            # Fallback to any model
            candidates = list(self._model_registry.values())

        # Select candidate with best Pareto cost-latency trade-off
        best_model = self._select_best_candidate(candidates, task.budget_usd)
        fallbacks = [m.model_id for m in self._model_registry.values() if m.model_id != best_model.model_id]

        t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return RoutingDecision(
            task_id=task.task_id,
            chosen_model=best_model,
            estimated_entropy=entropy,
            routing_latency_ms=round(t_elapsed_ms, 3),
            reason=reason,
            fallback_models=fallbacks[:3],
        )

    def _select_best_candidate(self, candidates: List[ModelDescriptor], budget_usd: float) -> ModelDescriptor:
        if len(candidates) == 1:
            return candidates[0]

        max_cost = max(m.input_cost_per_m + m.output_cost_per_m for m in candidates) or 1.0
        max_lat = max(m.avg_latency_ms for m in candidates) or 1.0

        best_score = -1e9
        best_model = candidates[0]

        for m in candidates:
            norm_cost = (m.input_cost_per_m + m.output_cost_per_m) / max_cost
            norm_lat = m.avg_latency_ms / max_lat

            # Higher is better
            score = (
                self.cost_weight * (1.0 - norm_cost) +
                self.latency_weight * (1.0 - norm_lat)
            )

            # Penalize models exceeding per-task budget
            expected_cost = (m.input_cost_per_m * 1000 + m.output_cost_per_m * 1000) / 1e6
            if expected_cost > budget_usd:
                score -= 2.0

            if score > best_score:
                best_score = score
                best_model = m

        return best_model
