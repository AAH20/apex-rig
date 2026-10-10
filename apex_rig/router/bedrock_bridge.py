"""
apex_rig.router.bedrock_bridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapter mimicking and integrating with Amazon Bedrock Intelligent Prompt Routing.
Dispatches between configured model pairs based on prompt complexity and SLA constraints.
"""

from typing import Tuple, Dict, Any
from apex_rig.core.primitives import TaskSpec, ModelDescriptor, ModelTier


class BedrockBridge:
    """
    Intelligent prompt router modeled after Amazon Bedrock's two-tier family routing.
    """

    def __init__(
        self,
        light_model: Optional[ModelDescriptor] = None,
        heavy_model: Optional[ModelDescriptor] = None,
        complexity_threshold: float = 2.5,
    ):
        self.light_model = light_model or ModelDescriptor(
            model_id="anthropic.claude-3-5-haiku",
            provider="aws_bedrock",
            tier=ModelTier.COMMODITY_CLOUD,
            context_limit=200000,
            input_cost_per_m=0.80,
            output_cost_per_m=4.00,
            avg_latency_ms=250.0,
            param_count_b=30.0,
        )
        self.heavy_model = heavy_model or ModelDescriptor(
            model_id="anthropic.claude-3-5-sonnet",
            provider="aws_bedrock",
            tier=ModelTier.FRONTIER_CLOUD,
            context_limit=200000,
            input_cost_per_m=3.00,
            output_cost_per_m=15.00,
            avg_latency_ms=850.0,
            param_count_b=200.0,
        )
        self.complexity_threshold = complexity_threshold

    def route_prompt(self, task: TaskSpec, entropy_score: float) -> Tuple[ModelDescriptor, Dict[str, Any]]:
        """
        Dynamically selects between the paired light and heavy foundation models.
        """
        if entropy_score >= self.complexity_threshold or task.priority < 25:
            chosen = self.heavy_model
            tier_desc = "heavy_reasoning"
            savings_pct = 0.0
        else:
            chosen = self.light_model
            tier_desc = "light_fast"
            # Calculate savings vs always using heavy
            savings_pct = round(
                (1.0 - (self.light_model.input_cost_per_m / self.heavy_model.input_cost_per_m)) * 100.0,
                1,
            )

        metadata = {
            "routed_tier": tier_desc,
            "cost_savings_pct": savings_pct,
            "model_pair": f"{self.light_model.model_id} <-> {self.heavy_model.model_id}",
            "complexity_score": entropy_score,
        }
        return (chosen, metadata)
