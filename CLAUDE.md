# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CS495 capstone project studying integer optimization for logistics driver-to-region assignment, with a secondary track comparing hand-built solvers against LLM-assisted code generation. Two optimization problems are in scope:

1. **Driver-to-region assignment** — binary ILP solved with PuLP (minimize total assignment cost, one driver per region minimum, one region per driver maximum, eligibility-filtered)
2. **0-1 Knapsack** — modeled in Hexaly (`.hxm`), but Hexaly is not installed locally (documented blocker in PLAN.md)

## Commands

```bash
# Install dependencies
make setup        # runs: poetry install

# Run tests
make test         # runs: poetry run pytest

# Lint
make lint         # runs: poetry run ruff check .

# Run main entry point (src/main.py does not exist yet)
make run

# Clean build artifacts
make clean
```

Run a single test file:
```bash
poetry run pytest tests/test_optimization_model.py
```

## Architecture

The pipeline flows: CSV input → preprocessing → ILP model → solver → evaluation

| File | Role |
|---|---|
| `src/data_preprocessing.py` | Loads and validates the assignment CSV; enforces required columns `[driver_id, region_id, cost, eligible]` |
| `src/optimization_model.py` | Builds and solves the PuLP ILP. Filters to eligible pairs only, minimizes cost, one assignment per driver (≤1), full region coverage (≥1 per region) |
| `src/evaluation.py` | Computes metrics from solver output: total assignments, covered regions, assigned drivers |
| `src/llm_model_generation.py` | Placeholder for LLM-assisted model generation experiments (currently stub) |
| `src/knapsack.hxm` | Hexaly model for the 0-1 knapsack problem (alternative solver track) |
| `data/sample_driver_region_data.csv` | Sample assignment data (4 drivers × 3 regions, with eligibility and costs) |
| `data/knapsack_input.txt` | Knapsack instance: line 1 = n items, line 2 = weights, line 3 = values, line 4 = capacity |

## Known Issues / Environment Notes

- **PuLP** is used in `src/optimization_model.py` but is missing from `pyproject.toml` dependencies. Add it with `poetry add pulp` before running the optimization model.
- **`src/main.py`** is referenced in `make run` but does not exist yet.
- **Hexaly** is not installed; the `.hxm` model cannot be executed until Hexaly is available in PATH. Test with: `where.exe hexaly` (Windows) or `which hexaly`.
- No tests exist yet; `make test` will pass vacuously.

## Data Format

Assignment CSV columns: `driver_id`, `region_id`, `cost`, `eligible` (1/0 flag).

Knapsack input format (plain text, space-separated):
```
<n_items>
<weight_1> <weight_2> ... <weight_n>
<value_1> <value_2> ... <value_n>
<capacity>
```
