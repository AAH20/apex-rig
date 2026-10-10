"""
Unit tests for KeyPooler, LatencyArbiter, BedrockBridge, and OpenRouterBridge.
"""

import unittest
from apex_rig.router.key_pooler import KeyPooler
from apex_rig.router.latency_arbiter import LatencyArbiter
from apex_rig.router.bedrock_bridge import BedrockBridge
from apex_rig.router.openrouter_bridge import OpenRouterBridge
from apex_rig.core.primitives import TaskSpec, ModelDescriptor, ModelTier


class TestRouterComponents(unittest.TestCase):

    def test_key_pooler_cooldown(self):
        pooler = KeyPooler(cooldown_duration_sec=2.0)
        pooler.register_key("anthropic", "key-1", "sk-ant-test-1111", max_rpm=2)

        # Acquire 2 requests
        s1 = pooler.acquire_key("anthropic")
        s2 = pooler.acquire_key("anthropic")
        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)

        # 3rd should exceed max_rpm
        s3 = pooler.acquire_key("anthropic")
        self.assertIsNone(s3)

        # Rate limit trip
        pooler.record_outcome("key-1", "anthropic", success=False, is_rate_limited=True)
        status = pooler.get_status()
        self.assertEqual(status["anthropic"]["cooling_down"], 1)

    def test_latency_arbiter_outlier(self):
        arbiter = LatencyArbiter(window_size=10, outlier_sigma=2.0)
        # Normal samples around 200ms
        for _ in range(8):
            arbiter.record_latency("provider_a", 200.0)

        # Check normal vs spike
        self.assertFalse(arbiter.is_degraded("provider_a", 210.0))
        self.assertTrue(arbiter.is_degraded("provider_a", 650.0))

    def test_bedrock_bridge_routing(self):
        bridge = BedrockBridge(complexity_threshold=2.5)
        task = TaskSpec(task_id="t1", prompt="Explain sorting")

        # Low complexity -> Light model
        model_light, meta_light = bridge.route_prompt(task, entropy_score=1.5)
        self.assertEqual(meta_light["routed_tier"], "light_fast")
        self.assertGreater(meta_light["cost_savings_pct"], 0.0)

        # High complexity -> Heavy model
        model_heavy, meta_heavy = bridge.route_prompt(task, entropy_score=3.8)
        self.assertEqual(meta_heavy["routed_tier"], "heavy_reasoning")


if __name__ == "__main__":
    unittest.main()
