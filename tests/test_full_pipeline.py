"""
Integration tests for ApexRigOrchestrator full pipeline.
"""

import unittest
from apex_rig.orchestrator import ApexRigOrchestrator
from apex_rig.core.primitives import ModelTier


class TestFullPipeline(unittest.TestCase):

    def setUp(self):
        self.orchestrator = ApexRigOrchestrator(auto_initialize=True, total_vram_mb=32768.0)

    def test_end_to_end_task_submission(self):
        prefix = "System: Codebase Context Map\n- module_a.py\n- module_b.py\n"
        prompt = "Refactor module_a to use fast vector instructions."

        res, decision, meta = self.orchestrator.submit_task(
            prompt=prompt,
            context_prefix=prefix,
            priority=50,
            budget_usd=0.20,
        )

        self.assertEqual(res.status, "completed")
        self.assertIsNotNone(decision.chosen_model)
        self.assertGreater(meta["shared_tokens"] + meta["unique_tokens"], 0)
        self.assertIn("finops", meta)
        self.assertGreaterEqual(meta["vram_headroom_sec"], 0.0)

    def test_adapters_integration(self):
        pdn = self.orchestrator.firmware_adapter.get_pdn_health()
        self.assertEqual(pdn["peak_droop_mv"], 9.48)

        paging = self.orchestrator.contextfabric_adapter.get_paging_metrics()
        self.assertIn("total_paged_mb", paging)

        acceptance = self.orchestrator.specagent_adapter.get_acceptance_rate()
        self.assertGreaterEqual(acceptance, 0.0)

        decision_eval = self.orchestrator.decisioncore_adapter.evaluate_arbitration("task_01", 3)
        self.assertIn("arbitration_latency_us", decision_eval)

    def test_evolution_optimization(self):
        summary = self.orchestrator.evolve_hyperparameters(generations=2)
        self.assertIn("best_fitness", summary)
        self.assertGreater(summary["best_fitness"], 0.0)

    def test_mesh_status_report(self):
        status = self.orchestrator.get_mesh_status()
        self.assertIn("harnesses", status)
        self.assertIn("radix_dedup", status)
        self.assertIn("hardware", status)


if __name__ == "__main__":
    unittest.main()
