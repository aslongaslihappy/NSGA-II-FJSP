# NSGA-II-FJSP

An implementation of NSGA-II for the Flexible Job Shop Scheduling Problem (FJSP) with two objectives:

- Minimize makespan
- Minimize energy consumption

The current codebase has been refactored into a cleaner layout with separate algorithm, dataset, and utility modules.

## Features

- NSGA-II for bi-objective optimization
- OS/MS chromosome representation
- Fast non-dominated sorting and crowding-distance based environmental selection
- Binary tournament parent selection
- Support for `.txt` and `.fjs` FJSP instances
- Single-run execution and repeated experiment testing
- Pareto front export to CSV and visualization to PNG

## Project Structure

```text
.
├── main.py
├── datasets/
│   └── FJSP/
│       └── Brandimarte_Data/
├── nsga_fjsp/
│   ├── NSGA_II.py
│   ├── binary_tournament_selection.py
│   ├── decoder.py
│   ├── environment_selection.py
│   ├── operators.py
│   ├── parser.py
│   └── problem.py
├── utils/
│   ├── performance_test.py
│   └── recorder.py
└── results/
```

## Requirements

- Python 3.8+
- Required: `numpy`
- Optional: `matplotlib`, `tqdm`

Install dependencies:

```bash
pip install numpy matplotlib tqdm
```

Notes:

- `main.py` only requires `numpy`
- `utils/performance_test.py` needs `matplotlib` to generate figures
- If `tqdm` is not installed, repeated experiments still run without a progress bar

## Quick Start

### Run a single experiment

```bash
python main.py
```

Current default settings in `main.py`:

- Dataset: `Brandimarte_Data`
- Instance: `Mk01`
- Stopping criterion: `max_fe = 10000`
- Population size: `50`
- Crossover rate: `0.8`
- Mutation rate: `0.15`

The program prints the final Pareto front to the console.

### Run repeated performance tests

```bash
python utils/performance_test.py
```

Current default settings in `utils/performance_test.py`:

- Stopping criterion: `max_fe = 50000`
- Population size: `100`
- Crossover rate: `0.9`
- Mutation rate: `0.15`
- Number of runs: `10`
- Default test instance: `Brandimarte_Data/Mk01`

## Output Files

Repeated experiment results are saved under:

```text
results/<dataset_name>/<instance_name>/
```

For example:

```text
results/Brandimarte_Data/Mk01/
```

The current experiment pipeline produces:

- `all_pareto_points.csv`: all Pareto points from all runs
- `final_pareto_front.csv`: merged global non-dominated front
- `pareto_fronts.png`: Pareto fronts from repeated runs
- `combined_pareto_front.png`: merged Pareto front visualization
- `history/pareto_history_run_XX.csv`: Pareto history recorded during each run

## Example Result

Pareto fronts generated from repeated runs on `Brandimarte_Data/Mk01`:

![Pareto Fronts](results/Brandimarte_Data/Mk01/pareto_fronts.png)

## Dataset Format

The parser currently looks for instance files in:

```text
datasets/FJSP/<dataset_name>/
```

Supported formats:

- `.txt`
- `.fjs`

Resolution order:

1. `datasets/FJSP/<dataset_name>/<instance_name>.txt`
2. `datasets/FJSP/<dataset_name>/<instance_name>.fjs`

The repository currently includes:

- `datasets/FJSP/Brandimarte_Data/Mk01.txt`
- `datasets/FJSP/Brandimarte_Data/Mk02.txt`
- `datasets/FJSP/Brandimarte_Data/Mk03.txt`
- `datasets/FJSP/Brandimarte_Data/Mk04.txt`
- `datasets/FJSP/Brandimarte_Data/Mk05.txt`
- `datasets/FJSP/Brandimarte_Data/Mk06.txt`
- `datasets/FJSP/Brandimarte_Data/Mk07.txt`
- `datasets/FJSP/Brandimarte_Data/Mk08.txt`
- `datasets/FJSP/Brandimarte_Data/Mk09.txt`
- `datasets/FJSP/Brandimarte_Data/Mk10.txt`

## Main Modules

- `main.py`: entry point for a single run
- `nsga_fjsp/problem.py`: problem definition, evaluation, initialization, crossover, mutation
- `nsga_fjsp/NSGA_II.py`: NSGA-II main loop
- `nsga_fjsp/environment_selection.py`: non-dominated sorting and crowding-distance based environmental selection
- `nsga_fjsp/binary_tournament_selection.py`: binary tournament parent selection
- `nsga_fjsp/operators.py`: initialization, crossover, and mutation operators
- `nsga_fjsp/decoder.py`: decoding and objective calculation
- `nsga_fjsp/parser.py`: instance file loading
- `utils/performance_test.py`: repeated experiments, CSV export, plotting, history recording
- `utils/recorder.py`: final Pareto front extraction and printing

## Parameter Configuration

To change the experiment settings:

- Edit `main.py` for single-run parameters
- Edit `utils/performance_test.py` for repeated test parameters
- Edit `nsga_fjsp/decoder.py` for the energy model

Current energy model constants:

- `processing_power = 30.0`
- `idle_power = 1.0`

## Current Default Example

With the current `main.py`, the default run uses:

- Dataset: `Brandimarte_Data`
- Instance: `Mk01`
- `max_fe = 10000`
- `pop_size = 50`
- `cr = 0.8`
- `mu = 0.15`

## Future Improvements

- Add command-line arguments for dataset and parameter selection
- Add benchmark automation for multiple instances
- Add more evaluation metrics and experiment summaries
- Add reproducibility support for logging and seed control
