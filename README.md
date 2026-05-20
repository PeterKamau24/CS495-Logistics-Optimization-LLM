# CS495 — Logistics Optimization with LLM Assistance

A capstone project on integer optimization for logistics assignment, with a companion study of the Branch & Bound algorithm in three languages.

## Two Tracks

### 1. Production — Driver-to-Region ILP

A binary integer linear program in PuLP that assigns drivers to regions subject to eligibility, coverage, and per-driver capacity constraints. Solved via COIN-CBC.

- Code: `src/optimization_model.py`, `src/data_preprocessing.py`, `src/evaluation.py`
- Data: `data/sample_driver_region_data.csv`
- Run: `python src/main.py driver-region`

### 2. Research — Branch & Bound on 0-1 Knapsack

The same algorithm implemented in three languages so language overhead and algorithm overhead are separately measurable.

- Python: `src/knapsack_branch_bound.py`
- C++: `src/knapsack_branch_bound.cpp`
- x86-64 ASM (NASM, Win64): `src/knapsack_branch_bound.asm` + C wrapper
- Brute-force baselines for comparison: `src/knapsack_brute_force.{py,cpp,asm}`
- Benchmarks: `notebooks/knapsack_benchmark_3way.ipynb`, `benchmark_results_all_three.json`, `benchmark_results_bb.json`
- Run: `python src/main.py knapsack-bb --input data/knapsack_input.txt`

The two tracks are connected: the CBC solver in track 1 is itself a Branch & Bound implementation. Studying B&B is studying the engine that solves the ILP.

## Headline Results

- **Algorithmic effect.** At n = 25, B&B is approximately 1,000,000× faster than brute force, returning the identical optimum (value = 1153).
- **Language effect (within B&B).** C++ averages ~13× over Python; hand-tuned ASM averages ~52× over Python and ~3× over C++.
- **Driver-region ILP.** On the 4×3 sample dataset, optimal cost = 13 with full region coverage.

Full numbers in [`docs/final_report.md`](docs/final_report.md) and [`results/experiment_summary.md`](results/experiment_summary.md).

## Setup

If you have GNU Make and Poetry installed:

```bash
make setup       # poetry install
make test        # poetry run pytest   (7 tests, all passing)
make lint        # poetry run ruff check .
```

### Without Make (Windows / plain pip)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pytest -v
python src/main.py --help
```

## CLI

```bash
python src/main.py --help
python src/main.py driver-region
python src/main.py knapsack-pulp
python src/main.py knapsack-bb --input data/knapsack_input.txt
```

## Presentation

`notebooks/presentation_bb.html` — 14-slide reveal.js deck with speaker notes. Serve locally so the image paths resolve:

```bash
python -m http.server 8000
# then open http://localhost:8000/notebooks/presentation_bb.html
```

## Repository Layout

| Path | Purpose |
|---|---|
| `src/` | Solver source — ILP, knapsack PuLP, three-language B&B and brute force |
| `tests/` | pytest verification of known-answer instances |
| `data/` | Sample driver-region CSV; canonical knapsack instance |
| `notebooks/` | Jupyter benchmarking notebooks; reveal.js slide deck; synthetic instances |
| `docs/` | Proposal, final report, presentation notes |
| `results/` | Experiment summaries and tabulated benchmarks |
| `*.json` (root) | Raw benchmark output |
| `*.png` (root) | Generated benchmark plots and pipeline diagrams |

## Known Limitations

- The LLM-generated-solver comparison (originally proposed Phase 4) is not yet completed; the hand-built B&B suite serves as ground truth for a future iteration.
- Hexaly is not installed locally; `src/knapsack.hxm` is preserved for reference.
- The driver-region dataset is a small synthetic instance; production-scale evaluation is future work.

## Author

Peter Kamau — Bellevue College, CS495
