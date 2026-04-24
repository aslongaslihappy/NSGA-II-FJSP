from __future__ import annotations

from pathlib import Path

from nsga_fjsp.environment_selection import fast_non_dominated_sort

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
except ImportError:
    plt = None
    Patch = None

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


def get_best_makespan_pareto_individual(population):
    if not population:
        raise ValueError("Population is empty.")

    objectives = [individual.objectives for individual in population]
    fronts = fast_non_dominated_sort(objectives)
    if not fronts or not fronts[0]:
        raise ValueError("No Pareto front found in population.")

    best_index = min(fronts[0], key=lambda index: (population[index].objectives[0], population[index].objectives[1]))
    return population[best_index]


def plot_gantt_from_details(schedule_details, save_path):
    if plt is None or Patch is None:
        raise ImportError("matplotlib is required for Gantt plotting.")

    operations = schedule_details.get("operations", [])
    machine_num = int(schedule_details.get("machine_num", 0))

    if not operations:
        raise ValueError("No operation details available for Gantt plotting.")

    makespan = schedule_details["objectives"]["makespan"]
    energy = schedule_details["objectives"]["energy"]
    job_ids = sorted({operation["job_id"] for operation in operations})
    pastel_colors = [
        "#A8DADC",
        "#F7C6C7",
        "#CDB4DB",
        "#FAEDCD",
        "#BDE0FE",
        "#CCD5AE",
        "#D8E2DC",
        "#F9DCC4",
        "#CFE1B9",
        "#B8C0FF",
        "#E4C1F9",
        "#FFD6A5",
    ]
    job_colors = {job_id: pastel_colors[index % len(pastel_colors)] for index, job_id in enumerate(job_ids)}

    lane_labels = [f"M{machine_id}" for machine_id in range(1, machine_num + 1)]
    lane_positions = list(range(len(lane_labels)))

    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor("#F8FAFC")
    ax.set_facecolor("#FCFCF9")
    bar_height = 0.72

    for operation in operations:
        y = operation["machine_id"] - 1
        start_time = operation["start_time"]
        duration = operation["process_time"]
        job_id = operation["job_id"]
        label = f"J{job_id}-O{operation['op_id']}"
        ax.barh(
            y,
            duration,
            left=start_time,
            height=bar_height,
            color=job_colors[job_id],
            edgecolor="black",
            linewidth=0.8,
        )
        if duration > 1:
            ax.text(
                start_time + duration / 2,
                y,
                label,
                ha="center",
                va="center",
                fontsize=8,
                color="black",
            )

    ax.set_yticks(lane_positions)
    ax.set_yticklabels(lane_labels)
    ax.invert_yaxis()
    ax.set_xlabel("Time")
    ax.set_ylabel("Machines")
    ax.set_title(f"Best Makespan Gantt Chart (Makespan={makespan:.2f}, Energy={energy:.2f})")
    ax.set_xlim(0, max(makespan, 1))
    ax.grid(True, axis="x", linestyle="--", alpha=0.35, color="#9AA5B1")
    for spine in ax.spines.values():
        spine.set_color("#B8C4CE")

    legend_handles = [Patch(facecolor=job_colors[job_id], edgecolor="black", label=f"Job {job_id}") for job_id in job_ids]
    ax.legend(handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=min(len(legend_handles), 6), frameon=False)

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return save_path


def record_best_makespan_gantt(problem, population, save_path=None):
    best_individual = get_best_makespan_pareto_individual(population)
    schedule_details = problem.decoder.decode_with_details(
        best_individual.job_code,
        best_individual.machine_code,
    )

    makespan = schedule_details["objectives"]["makespan"]
    energy = schedule_details["objectives"]["energy"]
    if abs(makespan - best_individual.objectives[0]) > 1e-6 or abs(energy - best_individual.objectives[1]) > 1e-6:
        raise ValueError("Detailed decoding result does not match the selected individual's objectives.")

    if save_path is None:
        project_root = Path(__file__).resolve().parent.parent
        save_path = project_root / "results" / problem.dataset_name / problem.instance_name / "best_makespan_gantt.png"

    chart_path = plot_gantt_from_details(schedule_details, save_path)
    return best_individual, schedule_details, chart_path
