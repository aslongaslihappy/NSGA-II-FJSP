from __future__ import annotations

import random

from nsga_fjsp.decoder import FJSPDecoder
from nsga_fjsp.operators import FJSPCrossover, FJSPInitialization, FJSPMutation
from nsga_fjsp.parser import read_fjsp_instance


class Individual:
    def __init__(self, genes, objectives):
        self.genes = tuple(list(gene) for gene in genes)
        self.objectives = objectives
        self.rank = None
        self.crowding_distance = 0.0

    @property
    def job_code(self):
        return self.genes[0]

    @property
    def machine_code(self):
        return self.genes[1]


class BaseAlgorithm:
    def __init__(self, problem):
        self.problem = problem
        self.history = []
        self.generation = 0

    def reset_history(self):
        self.history = []
        self.generation = 0
        self.problem.reset_fe()

    def not_terminated(self, population):
        self._record_history(population)
        self.generation += 1
        if self.generation % 10 == 0:
            print(f"Generation {self.generation}") #每10代打印一次当前代数
        return self.problem.fe < self.problem.max_fe

    def _record_history(self, population):
        self.history.append(
            {
                "generation": self.generation,
                "fe": self.problem.fe,
                "objectives": [tuple(individual.objectives) for individual in population],
            }
        )


class FJSPProblem:
    def __init__(self, dataset_name, instance_name, max_fe=10000):
        self.dataset_name = dataset_name
        self.instance_name = instance_name
        self.max_fe = max_fe
        self.fe = 0

        self.work, self.machine_time = read_fjsp_instance(dataset_name, instance_name)
        self.decoder = FJSPDecoder(self.work, self.machine_time)
        self.initialization = FJSPInitialization(self.work, self.machine_time)
        self.crossover_operator = FJSPCrossover()
        self.mutation_operator = FJSPMutation(self.machine_time)

    def reset_fe(self):
        self.fe = 0

    def copy_solution(self, *genes):
        return tuple(list(gene) for gene in genes)

    def create_individual(self, *genes):
        copied_genes = self.copy_solution(*genes)
        objectives = self.evaluate(*copied_genes)
        self.fe += 1
        return Individual(copied_genes, objectives)

    def initialize_population(self, pop_size):
        population = []

        for _ in range(pop_size):
            chromosome = self.initialization.create_chromosome_random()
            population.append(self.create_individual(*chromosome))

        return population

    def generate_offspring(self, parents, cr, mu):
        offspring = []

        for index in range(0, len(parents), 2):
            parent1 = parents[index]
            parent2 = parents[index + 1]
            parent1_genes = self.copy_solution(*parent1.genes)
            parent2_genes = self.copy_solution(*parent2.genes)

            if random.random() < cr:
                child1_genes, child2_genes = self.crossover(parent1_genes, parent2_genes)
            else:
                child1_genes = self.copy_solution(*parent1_genes)
                child2_genes = self.copy_solution(*parent2_genes)

            if random.random() < mu:
                child1_genes = self.mutate(child1_genes)
                child2_genes = self.mutate(child2_genes)

            offspring.append(self.create_individual(*child1_genes))
            offspring.append(self.create_individual(*child2_genes))

        return offspring

    def evaluate(self, job_code, machine_code):
        return self.decoder.calculate(job_code, machine_code)

    def crossover(self, parent1_genes, parent2_genes):
        parent1_job, parent1_machine = parent1_genes
        parent2_job, parent2_machine = parent2_genes
        child1_job, child2_job = self.crossover_operator.pox(parent1_job, parent2_job)
        child1_machine, child2_machine = self.crossover_operator.ux(parent1_machine, parent2_machine)
        return (child1_job, child1_machine), (child2_job, child2_machine)

    def mutate(self, genes):
        job_code, machine_code = genes
        job_code = self.mutation_operator.mutate_operation_sequence(job_code)
        machine_code = self.mutation_operator.mutate_machine_selection(machine_code)
        return job_code, machine_code
