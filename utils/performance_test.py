from __future__ import annotations

import csv
import random
import statistics
import sys
import time
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **_kwargs):
        return iterable

try:
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
except ImportError:
    plt = None
    FontProperties = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from nsga_fjsp.NSGA_II import NSGA_II
from nsga_fjsp.problem import FJSPProblem
from utils.recorder import get_final_pareto_front


random.seed(42)


class NSGAParetoTester:
    def __init__(self, max_fe=10000, popsize=50, cr=0.8, mu=0.15, save_history=True):
        self.max_fe = max_fe
        self.popsize = popsize
        self.cr = cr
        self.mu = mu
        self.save_history = save_history
        self.results_dir = PROJECT_ROOT / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.font = self._build_font()

    def _build_font(self):
        if FontProperties is None:
            return None

        simsun = Path(r"C:\Windows\Fonts\simsun.ttc")
        if simsun.exists():
            return FontProperties(fname=str(simsun), size=12)
        return None

    def run_test(self, datasets, num_runs=10):
        print("开始运行 NSGA-II Pareto 测试...")

        all_results = []
        dataset_summary = []

        for dataset in datasets:
            dataset_name = dataset["name"]
            dataset_source = dataset["da"]

            print(f"\n处理测试集: {dataset_name}")

            dataset_dir = self.results_dir / dataset_source / dataset_name
            dataset_dir.mkdir(parents=True, exist_ok=True)

            dataset_results = []
            all_pareto_fronts = []

            for run_id in tqdm(range(num_runs), desc="重复运行"):
                result = self.run_single_test(dataset, run_id, dataset_dir)
                dataset_results.append(result)
                all_results.append(result)
                if result["pareto_front"]:
                    all_pareto_fronts.append(result["pareto_front"])

            self.save_pareto_fronts(all_pareto_fronts, dataset_dir)
            self.plot_pareto_fronts(all_pareto_fronts, dataset_dir, dataset_name)

            stats = self.calculate_statistics(dataset_results)
            stats["测试集"] = dataset_name
            stats["数据集来源"] = dataset_source
            dataset_summary.append(stats)

        print(f"\n测试完成，结果已保存到: {self.results_dir}")
        return all_results, dataset_summary

    def run_single_test(self, dataset, run_id, dataset_dir):
        dataset_name = dataset["name"]
        dataset_source = dataset["da"]

        start_time = time.perf_counter()

        problem = FJSPProblem(dataset_source, dataset_name, max_fe=self.max_fe)
        algorithm = NSGA_II(problem)
        algorithm.pop_size = self.popsize
        algorithm.cr = self.cr
        algorithm.mu = self.mu

        population = algorithm.run()
        if self.save_history:
            self.save_pareto_history(algorithm.history, dataset_dir, run_id + 1)
        pareto_front = get_final_pareto_front(population)

        runtime = time.perf_counter() - start_time

        return {
            "测试集": dataset_name,
            "运行ID": run_id + 1,
            "pareto_front": pareto_front,
            "运行时间": runtime,
            "工序数": len(problem.work),
            "机器数": self._count_machine_count(problem.machine_time),
            "停止准则": f"max_fe={self.max_fe}",
        }

    def calculate_statistics(self, results):
        runtimes = [result["运行时间"] for result in results]
        return {
            "平均运行时间": statistics.fmean(runtimes),
            "最短运行时间": min(runtimes),
            "最长运行时间": max(runtimes),
        }

    def save_pareto_fronts(self, pareto_fronts, dataset_dir):
        if not pareto_fronts:
            return

        all_points = []
        for run_id, front in enumerate(pareto_fronts, start=1):
            for point in front:
                all_points.append([run_id, point[0], point[1]])

        if not all_points:
            return

        self._write_csv(
            dataset_dir / "all_pareto_points.csv",
            ["运行ID", "目标1_Makespan", "目标2_Energy"],
            all_points,
        )
        print(f"已保存全部 Pareto 点，共 {len(all_points)} 个")

        final_pareto_front = self.get_non_dominated([[point[1], point[2]] for point in all_points])
        if not final_pareto_front:
            return

        final_points_with_id = []
        for point in final_pareto_front:
            for original_point in all_points:
                if original_point[1] == point[0] and original_point[2] == point[1]:
                    final_points_with_id.append([original_point[0], point[0], point[1], True])
                    break

        final_points_with_id.sort(key=lambda item: item[1])
        self._write_csv(
            dataset_dir / "final_pareto_front.csv",
            ["运行ID", "目标1_Makespan", "目标2_Energy", "是否全局非支配"],
            final_points_with_id,
        )
        print(f"已保存最终 Pareto 前沿，共 {len(final_points_with_id)} 个")

    def save_pareto_history(self, history, dataset_dir, run_id):
        history_dir = dataset_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        pareto_history_path = history_dir / f"pareto_history_run_{run_id:02d}.csv"

        pareto_rows = []
        for entry in history:
            objectives = entry.get("objectives", [])
            if not objectives:
                continue

            pareto_front = sorted(
                self.get_non_dominated([list(objective) for objective in objectives]),
                key=lambda item: item[0],
            )

            for point_id, point in enumerate(pareto_front, start=1):
                pareto_rows.append(
                    [
                        entry.get("generation", 0),
                        entry.get("fe", 0),
                        point_id,
                        point[0],
                        point[1],
                    ]
                )

        self._write_csv(
            pareto_history_path,
            ["generation", "fe", "point_id", "makespan", "energy"],
            pareto_rows,
        )

    def plot_pareto_fronts(self, pareto_fronts, dataset_dir, dataset_name):
        if plt is None or not pareto_fronts:
            return

        plt.rcParams["axes.unicode_minus"] = False

        plt.figure(figsize=(12, 8))
        for index, front in enumerate(pareto_fronts, start=1):
            if not front:
                continue
            x_values = [point[0] for point in front]
            y_values = [point[1] for point in front]
            plt.scatter(x_values, y_values, label=f"运行 {index}", alpha=0.6, s=30)

        self._set_title_and_labels(
            f"{dataset_name} - 各次运行 Pareto 前沿",
            "目标1: Makespan",
            "目标2: Energy",
        )
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(prop=self.font)
        plt.tight_layout()
        plt.savefig(dataset_dir / "pareto_fronts.png")
        plt.close()

        plt.figure(figsize=(12, 8))
        all_points = []
        for front in pareto_fronts:
            all_points.extend(front)

        if all_points:
            x_values = [point[0] for point in all_points]
            y_values = [point[1] for point in all_points]
            plt.scatter(x_values, y_values, color="blue", alpha=0.6, s=30)

            non_dominated = self.get_non_dominated(all_points)
            if non_dominated:
                sorted_front = sorted(non_dominated, key=lambda item: item[0])
                front_x = [point[0] for point in sorted_front]
                front_y = [point[1] for point in sorted_front]
                plt.scatter(front_x, front_y, color="red", s=50, label="全局非支配前沿")
                plt.plot(front_x, front_y, "r--", linewidth=2)

        self._set_title_and_labels(
            f"{dataset_name} - 合并 Pareto 前沿",
            "目标1: Makespan",
            "目标2: Energy",
        )
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(prop=self.font)
        plt.tight_layout()
        plt.savefig(dataset_dir / "combined_pareto_front.png")
        plt.close()

    def get_non_dominated(self, points):
        if not points:
            return []

        non_dominated = []
        for point in points:
            dominated = False
            for other_point in points:
                if (
                    other_point[0] <= point[0]
                    and other_point[1] <= point[1]
                    and (other_point[0] < point[0] or other_point[1] < point[1])
                ):
                    dominated = True
                    break
            if not dominated and point not in non_dominated:
                non_dominated.append(point)
        return non_dominated

    def _count_machine_count(self, machine_time):
        machine_ids = []
        for operation in machine_time:
            machine_ids.extend(operation[0::2])
        return max(machine_ids) if machine_ids else 0

    def _set_title_and_labels(self, title, xlabel, ylabel):
        if self.font is not None:
            plt.title(title, fontproperties=self.font)
            plt.xlabel(xlabel, fontproperties=self.font)
            plt.ylabel(ylabel, fontproperties=self.font)
        else:
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)

    def _write_csv(self, file_path, header, rows):
        with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)


def main():
    max_fe = 50000
    popsize = 100
    cr = 0.9
    mu = 0.15
    num_runs = 10

    datasets = [
        {"name": "Mk01", "da": "Brandimarte_Data"},
        # {"name": "Mk02", "da": "Brandimarte_Data"},
        # {"name": "Mk03", "da": "Brandimarte_Data"},
        # {"name": "Mk04", "da": "Brandimarte_Data"},
        # {"name": "Mk05", "da": "Brandimarte_Data"},
        # {"name": "Mk06", "da": "Brandimarte_Data"},
        # {"name": "Mk07", "da": "Brandimarte_Data"},
        # {"name": "Mk08", "da": "Brandimarte_Data"},
        # {"name": "Mk09", "da": "Brandimarte_Data"},
        # {"name": "Mk10", "da": "Brandimarte_Data"},
    ]

    tester = NSGAParetoTester(max_fe=max_fe, popsize=popsize, cr=cr, mu=mu)
    print(f"Stopping criterion: max_fe = {max_fe}")
    tester.run_test(datasets, num_runs=num_runs)


if __name__ == "__main__":
    main()
