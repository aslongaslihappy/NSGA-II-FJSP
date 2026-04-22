from nsga_fjsp.environment_selection import fast_non_dominated_sort

def get_final_pareto_front(population):
    objectives = [individual.objectives for individual in population]
    pareto_front = fast_non_dominated_sort(objectives)[0]

    unique_solutions = []
    for index in pareto_front:
        solution = population[index].objectives
        is_duplicate = False

        for existing_solution in unique_solutions:
            if abs(solution[0] - existing_solution[0]) < 1e-6 and abs(solution[1] - existing_solution[1]) < 1e-6:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_solutions.append(solution)

    return sorted(unique_solutions, key=lambda item: item[0])


def print_pareto_front(title, pareto_front):
    print(title)
    for index, solution in enumerate(pareto_front, start=1):
        print(f"Solution {index}: makespan = {solution[0]:.2f}, energy = {solution[1]:.2f}")