from __future__ import annotations

from nsga_fjsp.NSGA_II import NSGA_II
from nsga_fjsp.problem import FJSPProblem
from utils.recorder import get_final_pareto_front, print_pareto_front, record_best_makespan_gantt


def main():
    problem = FJSPProblem("Brandimarte_Data", "Mk01", max_fe=10000)
    algorithm = NSGA_II(problem)
    algorithm.pop_size = 100
    algorithm.cr = 0.9
    algorithm.mu = 0.15

    print(f"Stopping criterion: {problem.max_fe} function evaluations")
    population = algorithm.run()
    pareto_front = get_final_pareto_front(population)
    print_pareto_front("Final Pareto front (makespan, energy):", pareto_front)
    _, _, gantt_path = record_best_makespan_gantt(problem, population)
    print(f"Gantt chart saved to: {gantt_path}")


if __name__ == "__main__":
    main()
