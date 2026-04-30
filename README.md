# NSGA-II-FJSP

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Algorithm" src="https://img.shields.io/badge/Algorithm-NSGA--II-4B5563">
  <img alt="Problem" src="https://img.shields.io/badge/Problem-FJSP-0F766E">
  <img alt="Objectives" src="https://img.shields.io/badge/Objectives-Makespan%20%7C%20Energy-B45309">
</p>

A Python implementation of NSGA-II for the Flexible Job Shop Scheduling Problem (FJSP), with two optimization objectives:

- `Makespan`
- `Total energy consumption`

This repository is intended as a lightweight research baseline. It includes the core evolutionary solver, benchmark instance parsers, schedule decoding, Pareto-front export, Pareto plotting, and Gantt-chart generation for the best-`Makespan` Pareto solution.  

## Highlights

- Multi-objective optimization based on `NSGA-II`
- Two-part chromosome representation:
  operation sequence and machine assignment
- `POX` crossover for operation sequencing
- `UX` crossover for machine genes
- Mutation operators for operation and machine decisions
- Fast non-dominated sorting and crowding-distance-based environmental selection
- Energy modeling for:
  machine processing and machine idle time
- Batch experiments with Pareto-history export and Pareto plots
- Gantt-chart generation after optimization:
  machine processing schedule for the best-`Makespan` Pareto solution

## Example Results

Example result folder: `results/Brandimarte_Data/Mk01/`

**Pareto Plot:**

![Combined Pareto Front](results/Brandimarte_Data/Mk01/pareto_fronts.png)

**Gantt Chart:**

![Best Makespan Gantt Chart](results/Brandimarte_Data/Mk01/best_makespan_gantt.png)

## Repository Structure

```text
NSGA-II-FJSP/
|-- datasets/
|   `-- FJSP/
|       `-- Brandimarte_Data/
|-- nsga_fjsp/
|   |-- NSGA_II.py
|   |-- binary_tournament_selection.py
|   |-- decoder.py
|   |-- environment_selection.py
|   |-- operators.py
|   |-- parser.py
|   `-- problem.py
|-- utils/
|   |-- performance_test.py
|   `-- recorder.py
|-- results/
|-- main.py
`-- README.md
```

## Requirements

- Python 3.10+
- Required packages: `numpy`, `matplotlib`
- Optional package: `tqdm`

Install dependencies with:

```bash
pip install numpy matplotlib tqdm
```

If you only need the core optimization logic without plotting, `numpy` is sufficient for the solver itself. However, the default `main.py` workflow now generates a Gantt chart, so `matplotlib` is required for the out-of-the-box run.

## Quick Start

Run the default example:

```bash
python main.py
```

Current default configuration in `main.py`:

- Dataset: `Brandimarte_Data`
- Instance: `Mk01`
- Stopping criterion: `max_fe = 10000`
- Population size: `50`
- Crossover probability: `0.8`
- Mutation probability: `0.15`

Typical console output:

```text
Stopping criterion: 10000 function evaluations
Final Pareto front (makespan, energy):
Solution 1: makespan = 42.00, energy = 6931.00
Solution 2: makespan = 43.00, energy = 6882.00
Solution 3: makespan = 44.00, energy = 6833.00
Gantt chart saved to: results/Brandimarte_Data/Mk01/best_makespan_gantt.png
```

The exact Pareto front may vary between runs if no random seed is fixed.

## Output Files

After running `main.py`, the solver will:

- Print the final Pareto front in the console
- Select the individual with the minimum `Makespan` from the final Pareto front
- Decode that individual again with detailed scheduling information
- Generate a Gantt chart showing the machine processing schedule

Default output path:

```text
results/<dataset>/<instance>/best_makespan_gantt.png
```

## Batch Experiments

To perform repeated runs, save Pareto history, export CSV files, and generate Pareto plots, run:

```bash
python utils/performance_test.py
```

This script can:

- Run a selected dataset multiple times
- Save Pareto-front history for each run
- Merge Pareto points across runs
- Export result tables as CSV files
- Generate scatter plots for Pareto fronts

Example generated files:

- `all_pareto_points.csv`
- `final_pareto_front.csv`
- `pareto_fronts.png`
- `combined_pareto_front.png`
- `history/pareto_history_run_XX.csv`

## Supported Datasets

The parser looks for instance files under:

- `datasets/FJSP/<dataset_name>/`

Supported formats:

- `.txt`
- `.fjs`

Resolution order:

1. `datasets/FJSP/<dataset_name>/<instance_name>.txt`
2. `datasets/FJSP/<dataset_name>/<instance_name>.fjs`

The repository currently includes the `Brandimarte_Data` benchmark set, for example:

- `datasets/FJSP/Brandimarte_Data/Mk01.txt`
- `datasets/FJSP/Brandimarte_Data/Mk02.txt`
- `datasets/FJSP/Brandimarte_Data/Mk03.txt`

## Objective Definition

The solver optimizes:

1. `Makespan`
2. `Total Energy`

The total energy value includes:

- Machine processing energy
- Machine idle energy

Current default energy-model constants in `nsga_fjsp/decoder.py`:

- `processing_power = 30.0`
- `idle_power = 1.0`

## Main Modules

- `nsga_fjsp/problem.py`: problem definition, individual creation, initialization, crossover, and mutation
- `nsga_fjsp/decoder.py`: objective evaluation and detailed schedule decoding
- `nsga_fjsp/NSGA_II.py`: NSGA-II main loop
- `nsga_fjsp/environment_selection.py`: non-dominated sorting and crowding-distance selection
- `nsga_fjsp/binary_tournament_selection.py`: binary tournament parent selection
- `nsga_fjsp/operators.py`: initialization, crossover, and mutation operators
- `nsga_fjsp/parser.py`: instance loading
- `utils/recorder.py`: Pareto-front reporting and Gantt-chart plotting
- `utils/performance_test.py`: repeated experiments, statistics, CSV export, and Pareto plotting

## Customization

You can directly modify parameters in `main.py` or `utils/performance_test.py`, for example:

- Dataset and instance selection
- `max_fe`
- Population size `pop_size`
- Crossover probability `cr`
- Mutation probability `mu`
- Number of repeated runs `num_runs`
