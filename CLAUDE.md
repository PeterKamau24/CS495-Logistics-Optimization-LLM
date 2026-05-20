# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS495 capstone project on integer optimization for logistics, with a companion three-language study of Branch & Bound. The project runs on two tracks:

1. **Driver-to-region assignment** — binary ILP modeled in PuLP, solved with COIN-CBC. Minimizes total assignment cost subject to eligibility, at most one region per driver, at least one driver per region.
2. **0-1 Knapsack** — Branch & Bound implemented by hand in Python, C++, and x86-64 NASM (Win64). Verified against brute-force baselines and against a PuLP reference. The PuLP/CBC engine in track 1 is itself a B&B solver, so studying B&B informs the production track.

## Commands

If GNU Make and Poetry are installed:

```bash
make setup        # poetry install
make test         # poetry run pytest    (7 tests, currently all passing)
make lint         # poetry run ruff check .
make run          # python src/main.py   (argparse dispatcher with subcommands)
make clean        # remove .pytest_cache and __pycache__
```

Without Make (Windows / plain pip):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pytest -v
python src/main.py --help
```

Common dispatched commands:

```bash
python src/main.py --help
python src/main.py driver-region
python src/main.py knapsack-pulp
python src/main.py knapsack-bb --input data/knapsack_input.txt
```

Run a single test file:

```bash
poetry run pytest tests/test_knapsack.py -v
```

## Source Layout

### Driver-Region ILP track

| File | Role |
|---|---|
| `src/optimization_model.py` | PuLP ILP — minimizes assignment cost over eligible pairs |
| `src/data_preprocessing.py` | Validates CSV columns `[driver_id, region_id, cost, eligible]` |
| `src/evaluation.py` | Computes coverage and assignment metrics from solver output |
| `data/sample_driver_region_data.csv` | 4-driver × 3-region instance with eligibility flags |

### Knapsack track

| File | Role |
|---|---|
| `src/knapsack_pulp.py` | PuLP reference solver — runs PLAN-v1 (value=11) and disaster relief (value=598) |
| `src/knapsack_branch_bound.py` | Hand-built B&B in Python |
| `src/knapsack_branch_bound.cpp` | Same algorithm in C++ |
| `src/knapsack_branch_bound.asm` + `src/knapsack_bb_asm_wrapper.c` | Same algorithm in x86-64 NASM (Win64 ABI) |
| `src/knapsack_brute_force.{py,cpp,asm}` | O(2^n) baselines on the same instances |
| `src/benchmark_bb.py`, `src/benchmark_all_three.py` | Benchmark drivers |
| `src/visualize_bb.py`, `src/visualize_bb_extras.py`, `src/visualize_all_three.py` | Plot generation |
| `data/knapsack_input.txt` | Canonical 4-line instance (n / weights / values / capacity) |
| `notebooks/instance_n*.txt` | Synthetic n = 10…25 instances in 3-line format (`n capacity` / weights / values) |

The B&B Python and C++ readers accept *both* the 3-line and 4-line formats — `read_knapsack_instance` auto-detects by line count.

### Entry points and tests

| File | Role |
|---|---|
| `src/main.py` | argparse dispatcher with `driver-region`, `knapsack-pulp`, `knapsack-bb` subcommands |
| `tests/test_knapsack.py` | pytest verification — value=11, value=598, and format-reader tests |

## Known Issues / Environment Notes

- **Hexaly** is not installed; `src/knapsack.hxm` is preserved but cannot be executed locally.
- The **LLM-generated-solver comparison** described in PLAN.md Phase 4 is not yet implemented. The hand-built B&B suite is intended as ground truth for that future study.
- On Windows, console output uses Unicode box-drawing characters. `src/main.py` reconfigures `sys.stdout` to UTF-8 to avoid `cp1252` encoding errors. If you call solver modules directly (not via `main.py`), expect possible encoding errors in a default cmd window.
- `tests/` and `src/main.py` were added in May 2026 — the earlier PLAN.md sketched but did not include them.

## Data Formats

Driver-region CSV columns: `driver_id, region_id, cost, eligible` (0/1 flag).

Knapsack — two formats are accepted by the B&B reader:

```
# 3-line (used by notebooks/instance_n*.txt)
<n_items> <capacity>
<w_1> <w_2> ... <w_n>
<v_1> <v_2> ... <v_n>

# 4-line (used by data/knapsack_input.txt — canonical)
<n_items>
<w_1> <w_2> ... <w_n>
<v_1> <v_2> ... <v_n>
<capacity>
```
