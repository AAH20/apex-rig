"""
Unit tests for Shannon EntropyRouter and model arbitration.
"""

import unittest
from apex_rig.core.entropy_router import EntropyRouter
from apex_rig.core.primitives import TaskSpec, ModelTier


class TestEntropyRouter(unittest.TestCase):

    def setUp(self):
        self.router = EntropyRouter(
            local_threshold=2.0,
            frontier_threshold=3.5,
            cost_weight=0.5,
            latency_weight=0.5,
        )

    def test_shannon_entropy_calculation(self):
        simple_text = "test test test test test"
        complex_text = "Architect a Byzantine fault-tolerant decentralized ledger consensus protocol with zero-knowledge zk-SNARK proofs and formal verification."

        entropy_simple = self.router.calculate_shannon_entropy(simple_text)
        entropy_complex = self.router.calculate_shannon_entropy(complex_text)

        self.assertLess(entropy_simple, 1.0)
        self.assertGreater(entropy_complex, 3.0)

    def test_routing_local_tier(self):
        task = TaskSpec(
            task_id="t_simple",
            prompt="format json log formatting",
            budget_usd=0.01,
        )
        decision = self.router.route_task(task)
        self.assertEqual(decision.chosen_model.tier, ModelTier.LOCAL_SILICON)
        self.assertLess(decision.routing_latency_ms, 5.0)

    def test_routing_frontier_tier(self):
        task = TaskSpec(
            task_id="t_deep",
            prompt="Formulate a mathematical proof and synthesize a cross-compiler architecture optimizing intermediate representations for distributed TPU clusters.",
            priority=10,
        )
        decision = self.router.route_task(task)
        self.assertEqual(decision.chosen_model.tier, ModelTier.FRONTIER_CLOUD)


if __name__ == "__main__":
    unittest.main()
