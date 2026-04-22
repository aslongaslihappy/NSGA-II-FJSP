from __future__ import annotations

import random


def binary_tournament_selection(population):
    pop_size = len(population)
    selected_parents = []

    for _ in range(pop_size):
        idx1, idx2 = random.sample(range(pop_size), 2)
        winner = better_individual(population[idx1], population[idx2])
        selected_parents.append(winner)

    return selected_parents


def better_individual(individual1, individual2):
    if individual1.rank < individual2.rank:
        return individual1
    if individual2.rank < individual1.rank:
        return individual2
    if individual1.crowding_distance > individual2.crowding_distance:
        return individual1
    if individual2.crowding_distance > individual1.crowding_distance:
        return individual2
    return random.choice([individual1, individual2])
