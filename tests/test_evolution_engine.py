"""
Unit tests for RigEvolutionEngine genetic hyperparameter optimizer.
"""

import unittest
from apex_rig.core.evolution_engine import RigEvolutionEngine


class TestRigEvolutionEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RigEvolutionEngine(population_size=10, random_seed=123)

    def test_population_initialization(self):
        self.assertEqual(len(self.engine.population), 10)
        for g in self.engine.population:
            self.assertGreaterEqual(g.entropy_thresh_local, 0.5)
            self.assertLessEqual(g.vram_eviction_watermark, 0.95)

    def test_fitness_and_evolution_cycle(self):
        best_initial = self.engine.evolve_generation(
            eval_fn=lambda g: self.engine.evaluate_fitness(g, simulated_throughput=60.0, simulated_cost_usd=0.10, oom_penalty=0.0),
            generation_idx=0,
        )
        self.assertGreater(best_initial.fitness_score, 0.0)

        best_next = self.engine.evolve_generation(
            eval_fn=lambda g: self.engine.evaluate_fitness(g, simulated_throughput=75.0, simulated_cost_usd=0.08, oom_penalty=0.0),
            generation_idx=1,
        )
        self.assertEqual(best_next.generation, 1)
        self.assertGreaterEqual(len(self.engine.population), 10)


if __name__ == "__main__":
    unittest.main()
