from __future__ import annotations

import random

import numpy as np


class FJSPInitialization:
    def __init__(self, work, machine_time):
        self.work = work
        self.machine_time = machine_time

    def create_chromosome_random(self):
        os_code = np.copy(self.work)
        np.random.shuffle(os_code)
        os_code = os_code.tolist()

        ms_code = []
        for idx in range(len(os_code)):
            operation_machine_time = self.machine_time[idx]
            candidate_machines = [operation_machine_time[j] for j in range(0, len(operation_machine_time), 2)]
            machine_index = np.random.randint(0, len(candidate_machines), 1)[0]
            ms_code.append(candidate_machines[machine_index])

        return os_code, ms_code


class FJSPCrossover:
    def pox(self, parent1, parent2):
        job_list = list(set(parent1))
        split_index = np.random.randint(0, len(job_list), 1)[0]
        job_set1 = job_list[: split_index + 1]

        offspring1, offspring2 = [], []
        genes_to_fill1, genes_to_fill2 = [], []

        for idx in range(len(parent1)):
            gene1 = parent1[idx]
            gene2 = parent2[idx]
            if gene1 in job_set1:
                offspring1.append(gene1)
            else:
                genes_to_fill2.append(gene1)
                offspring1.append(-1)

            if gene2 in job_set1:
                offspring2.append(gene2)
            else:
                genes_to_fill1.append(gene2)
                offspring2.append(-1)

        for idx in range(len(parent1)):
            if offspring1[idx] == -1:
                offspring1[idx] = genes_to_fill1.pop(0)
            if offspring2[idx] == -1:
                offspring2[idx] = genes_to_fill2.pop(0)

        return offspring1, offspring2

    def ux(self, parent1_machine, parent2_machine):
        child1_machine = parent1_machine.copy()
        child2_machine = parent2_machine.copy()
        mask = [random.randint(0, 1) for _ in range(len(parent1_machine))]

        for idx in range(len(parent1_machine)):
            if mask[idx] == 1:
                child1_machine[idx], child2_machine[idx] = child2_machine[idx], child1_machine[idx]

        return child1_machine, child2_machine


class FJSPMutation:
    def __init__(self, machine_time):
        self.machine_time = machine_time

    def mutate_operation_sequence(self, os_code):
        if len(os_code) <= 1:
            return os_code.copy()

        pos1, pos2 = random.sample(range(len(os_code)), 2)
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1

        mutated = os_code.copy()
        value = mutated[pos2]
        del mutated[pos2]
        mutated.insert(pos1, value)
        return mutated

    def mutate_machine_selection(self, ms_code):
        if len(ms_code) == 0:
            return ms_code.copy()

        pos = random.randint(0, len(ms_code) - 1)
        operation_machine_time = self.machine_time[pos]
        available_machines = [operation_machine_time[idx] for idx in range(0, len(operation_machine_time), 2)]

        if available_machines:
            mutated = ms_code.copy()
            mutated[pos] = random.choice(available_machines)
            return mutated

        return ms_code.copy()
