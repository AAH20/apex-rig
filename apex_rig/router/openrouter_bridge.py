"""
apex_rig.router.openrouter_bridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Client adapter for OpenRouter and OmniRouter API gateway protocols.
Provides dynamic failover chaining, cost estimation, and provider arbitrage.
"""

from typing import List, Dict, Optional, Any
from apex_rig.core.primitives import TaskSpec, ModelDescriptor, ModelTier


class OpenRouterBridge:
    """
    Gateway bridge for multi-provider routing and token pricing arbitration.
    """

    def __init__(self, default_provider_chain: Optional[List[str]] = None):
        self.provider_chain = default_provider_chain or [
            "deepinfra",
            "together",
            "groq",
            "anthropic",
            "openai",
        ]

    def select_best_provider(
        self,
        model_id: str,
        available_providers: List[str],
        prioritize_latency: bool = False,
    ) -> str:
        """
        Picks the optimal provider from available host options for a given model checkpoint.
        """
        if not available_providers:
            return self.provider_chain[0]

        if prioritize_latency and "groq" in available_providers:
            return "groq"

        # Check against preference chain
        for preferred in self.provider_chain:
            if preferred in available_providers:
                return preferred

        return available_providers[0]

    def estimate_transaction_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: ModelDescriptor,
    ) -> float:
        cost = (input_tokens * model.input_cost_per_m + output_tokens * model.output_cost_per_m) / 1e6
        return round(cost, 6)
