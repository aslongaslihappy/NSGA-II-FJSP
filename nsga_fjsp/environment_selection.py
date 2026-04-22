from __future__ import annotations


def fast_non_dominated_sort(objectives):
    n = len(objectives)
    domination_count = [0] * n
    domination_sets = [[] for _ in range(n)]
    fronts = [[]]

    for i in range(n):
        for j in range(n):
            if i != j:
                if all(objectives[i][k] <= objectives[j][k] for k in range(len(objectives[i]))) and any(
                    objectives[i][k] < objectives[j][k] for k in range(len(objectives[i]))
                ):
                    domination_sets[i].append(j)
                elif all(objectives[j][k] <= objectives[i][k] for k in range(len(objectives[i]))) and any(
                    objectives[j][k] < objectives[i][k] for k in range(len(objectives[i]))
                ):
                    domination_count[i] += 1

        if domination_count[i] == 0:
            fronts[0].append(i)

    i = 0
    while fronts[i]:
        next_front = []
        for j in fronts[i]:
            for k in domination_sets[j]:
                domination_count[k] -= 1
                if domination_count[k] == 0:
                    next_front.append(k)
        i += 1
        fronts.append(next_front)

    return fronts[:-1]


def calculate_crowding_distance(objectives, front):
    if len(front) <= 2:
        return {i: float("inf") for i in front}

    distances = {i: 0.0 for i in front}

    for m in range(len(objectives[0])):
        sorted_front = sorted(front, key=lambda i: objectives[i][m])
        distances[sorted_front[0]] = float("inf")
        distances[sorted_front[-1]] = float("inf")

        f_max = objectives[sorted_front[-1]][m]
        f_min = objectives[sorted_front[0]][m]
        if f_max == f_min:
            continue

        for i in range(1, len(sorted_front) - 1):
            distances[sorted_front[i]] += (
                objectives[sorted_front[i + 1]][m] - objectives[sorted_front[i - 1]][m]
            ) / (f_max - f_min)

    return distances


def assign_rank_and_crowding(population):
    if not population:
        return []

    objectives = [individual.objectives for individual in population]
    fronts = fast_non_dominated_sort(objectives)

    for rank, front in enumerate(fronts):
        crowding_distances = calculate_crowding_distance(objectives, front)
        for index in front:
            population[index].rank = rank
            population[index].crowding_distance = crowding_distances[index]

    return fronts


def environment_selection(pop_size, population, offspring):
    combined_population = population + offspring
    if not combined_population:
        return []

    objectives = [individual.objectives for individual in combined_population]
    fronts = fast_non_dominated_sort(objectives)

    next_population = []
    front_index = 0

    while front_index < len(fronts) and len(next_population) + len(fronts[front_index]) <= pop_size:
        crowding_distances = calculate_crowding_distance(objectives, fronts[front_index])
        for index in fronts[front_index]:
            individual = combined_population[index]
            individual.rank = front_index
            individual.crowding_distance = crowding_distances[index]
            next_population.append(individual)
        front_index += 1

    if len(next_population) < pop_size and front_index < len(fronts):
        crowding_distances = calculate_crowding_distance(objectives, fronts[front_index])
        sorted_front = sorted(fronts[front_index], key=lambda index: -crowding_distances[index])

        for index in sorted_front[: pop_size - len(next_population)]:
            individual = combined_population[index]
            individual.rank = front_index
            individual.crowding_distance = crowding_distances[index]
            next_population.append(individual)

    assign_rank_and_crowding(next_population)
    return next_population
