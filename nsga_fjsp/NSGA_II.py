from __future__ import annotations

from nsga_fjsp.environment_selection import environment_selection
from nsga_fjsp.problem import BaseAlgorithm
from nsga_fjsp.binary_tournament_selection import binary_tournament_selection


class NSGA_II(BaseAlgorithm):
    def __init__(self, problem):
        super().__init__(problem)
        self.reset_history()
        self.pop_size = 50
        self.cr = 0.8
        self.mu = 0.15

    def run(self):
        population = self.problem.initialize_population(self.pop_size)
        population = environment_selection(self.pop_size, population, [])

        while self.not_terminated(population):
            parents = binary_tournament_selection(population)
            offspring = self.problem.generate_offspring(parents, self.cr, self.mu)
            population = environment_selection(self.pop_size, population, offspring)

        return population
