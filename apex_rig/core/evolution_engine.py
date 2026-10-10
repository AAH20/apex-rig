"""
apex_rig.core.evolution_engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Multi-objective Genetic Algorithm optimizing Apex Rig operational hyperparameters:
entropy thresholds, cost/latency weighting, VRAM eviction watermarks, and speculative depth.
"""

from typing import List, Tuple, Callable
import random
import copy
from apex_rig.core.primitives import EvolutionGenome


class RigEvolutionEngine:
    """
    Pareto-optimal evolutionary hyperparameter optimizer for Apex Rig.
    """

    def __init__(
        self,
        population_size: int = 16,
        mutation_rate: float = 0.20,
        crossover_rate: float = 0.70,
        random_seed: int = 42,
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        random.seed(random_seed)
        self.population = self._initialize_population()
        self.best_genome: EvolutionGenome = self.population[0]

    def _initialize_population(self) -> List[EvolutionGenome]:
        pop = []
        for _ in range(self.population_size):
            genome = EvolutionGenome(
                entropy_thresh_local=round(random.uniform(1.2, 2.5), 2),
                entropy_thresh_frontier=round(random.uniform(3.0, 4.5), 2),
                cost_weight=round(random.uniform(0.2, 0.8), 2),
                latency_weight=round(random.uniform(0.2, 0.8), 2),
                vram_eviction_watermark=round(random.uniform(0.75, 0.92), 2),
                speculative_depth=random.randint(1, 6),
                poll_interval_ms=round(random.uniform(20.0, 200.0), 1),
                generation=0,
                fitness_score=0.0,
            )
            pop.append(genome)
        return pop

    def evaluate_fitness(
        self,
        genome: EvolutionGenome,
        simulated_throughput: float,
        simulated_cost_usd: float,
        oom_penalty: float,
    ) -> float:
        """
        Multi-objective scalarized fitness function:
        F = w_lat * (throughput / 100) + w_cost * (10.0 / (cost + 0.1)) - oom_penalty
        """
        cost_term = 10.0 / (simulated_cost_usd + 0.05)
        throughput_term = simulated_throughput / 50.0
        fitness = (genome.latency_weight * throughput_term) + (genome.cost_weight * cost_term) - oom_penalty
        genome.fitness_score = round(max(0.01, fitness), 4)
        return genome.fitness_score

    def evolve_generation(
        self,
        eval_fn: Callable[[EvolutionGenome], float],
        generation_idx: int,
    ) -> EvolutionGenome:
        """
        Runs one evolutionary cycle: Evaluate -> Elitism -> Tournament -> Crossover -> Mutate.
        """
        # 1. Evaluate fitness for all individuals
        for individual in self.population:
            individual.fitness_score = eval_fn(individual)
            individual.generation = generation_idx

        # 2. Sort by fitness descending
        self.population.sort(key=lambda g: g.fitness_score, reverse=True)
        self.best_genome = copy.deepcopy(self.population[0])

        # 3. Preserve Elites (top 2)
        next_gen = [copy.deepcopy(self.population[0]), copy.deepcopy(self.population[1])]
        next_gen[0].generation = generation_idx + 1
        next_gen[1].generation = generation_idx + 1

        # 4. Fill remaining population
        while len(next_gen) < self.population_size:
            parent_a = self._tournament_select()
            parent_b = self._tournament_select()

            if random.random() < self.crossover_rate:
                child = self._crossover(parent_a, parent_b)
            else:
                child = copy.deepcopy(parent_a)

            if random.random() < self.mutation_rate:
                self._mutate(child)

            child.generation = generation_idx + 1
            next_gen.append(child)

        self.population = next_gen
        return self.best_genome

    def _tournament_select(self, k: int = 3) -> EvolutionGenome:
        candidates = random.sample(self.population, min(k, len(self.population)))
        candidates.sort(key=lambda g: g.fitness_score, reverse=True)
        return candidates[0]

    def _crossover(self, a: EvolutionGenome, b: EvolutionGenome) -> EvolutionGenome:
        # Uniform blend crossover
        return EvolutionGenome(
            entropy_thresh_local=round((a.entropy_thresh_local + b.entropy_thresh_local) / 2.0, 2),
            entropy_thresh_frontier=round((a.entropy_thresh_frontier + b.entropy_thresh_frontier) / 2.0, 2),
            cost_weight=round((a.cost_weight + b.cost_weight) / 2.0, 2),
            latency_weight=round((a.latency_weight + b.latency_weight) / 2.0, 2),
            vram_eviction_watermark=round((a.vram_eviction_watermark + b.vram_eviction_watermark) / 2.0, 2),
            speculative_depth=random.choice([a.speculative_depth, b.speculative_depth]),
            poll_interval_ms=round((a.poll_interval_ms + b.poll_interval_ms) / 2.0, 1),
            generation=a.generation,
            fitness_score=0.0,
        )

    def _mutate(self, g: EvolutionGenome) -> None:
        g.entropy_thresh_local = max(0.8, min(3.0, round(g.entropy_thresh_local + random.gauss(0, 0.2), 2)))
        g.entropy_thresh_frontier = max(2.5, min(5.0, round(g.entropy_thresh_frontier + random.gauss(0, 0.3), 2)))
        g.vram_eviction_watermark = max(0.65, min(0.95, round(g.vram_eviction_watermark + random.gauss(0, 0.05), 2)))
        g.speculative_depth = max(1, min(8, g.speculative_depth + random.choice([-1, 0, 1])))
