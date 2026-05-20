# PLAN.md

## Project Overview

**Title:** Integer Optimization for Logistics Assignment, with a Three-Language Branch & Bound Study
**Author:** Peter Kamau
**Course:** CS495 Capstone in Data Science — Bellevue College
**Date:** May 2026 (updated)

### Description

This capstone investigates discrete optimization in a logistics context (driver-to-region assignment) and the algorithm that powers production ILP solvers (Branch & Bound). To make B&B measurable, it is implemented by hand on the 0-1 knapsack problem in three languages — Python, C++, and x86-64 assembly — and benchmarked against brute-force baselines. The hand-built suite serves as ground truth for a future LLM-generated-solver comparison.

### Objectives

- Build a binary ILP for driver-to-region assignment (PuLP / CBC)
- Verify a PuLP knapsack model against a hand-computed instance (value=11)
- Implement Branch & Bound for 0-1 knapsack in Python, C++, and x86-64 NASM
- Benchmark B&B vs brute force across n = 3…25 in all three languages
- Lay the groundwork (verified solvers, pytest suite, benchmark instances) for a future LLM-vs-hand comparison

---

## Environment Setup

### Requirements

- Python 3.11+ (project uses 3.13 / 3.14)
- Poetry for dependency management (pip + venv fallback in `requirements.txt`)
- A C++ compiler (MSVC or g++) and NASM for the C++/ASM tracks

### Quick Start (Windows — primary)

```powershell
# Install prerequisites (one-time)
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.13

# Install Claude Code (optional)
npm install -g @anthropic-ai/claude-code

# Clone and set up project
git clone https://github.com/PeterKamau24/CS495-Logistics-Optimization-LLM.git
cd CS495-Logistics-Optimization-LLM
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
pytest -v
```

### Makefile Targets

```bash
make setup    # poetry install
make test     # poetry run pytest         (7 tests, all passing)
make lint     # poetry run ruff check .
make run      # python src/main.py        (dispatcher)
make clean    # remove .pytest_cache, __pycache__
```

### Dependencies

Pinned in `pyproject.toml`:

- `pulp` — linear/integer programming modeling library
- `pandas`, `numpy`, `matplotlib`, `scikit-learn` — analysis and visualization
- `pytest` — unit testing framework

---

## Architecture

```
CS495-Logistics-Optimization-LLM/
  PLAN.md                       # This file
  README.md                     # Project description
  CLAUDE.md                     # Codebase guide for Claude Code
  Makefile                      # Automation commands
  pyproject.toml                # Poetry config + dependencies + pytest config
  src/
    main.py                     # argparse dispatcher entry point
    optimization_model.py       # Driver-region PuLP ILP
    data_preprocessing.py       # CSV loading and validation
    evaluation.py               # Coverage/assignment metrics
    knapsack_pulp.py            # PuLP reference solver for 0-1 knapsack
    knapsack_branch_bound.{py,cpp,asm}   # Hand-built B&B in three languages
    knapsack_bb_asm_wrapper.c   # C glue for the ASM B&B
    knapsack_brute_force.{py,cpp,asm}    # O(2^n) baselines for comparison
    benchmark_bb.py             # Benchmark driver — B&B sweep
    benchmark_all_three.py      # Benchmark driver — three-language brute force
    visualize_bb.py, visualize_bb_extras.py, visualize_all_three.py
  tests/
    test_knapsack.py            # PLAN-v1 (value=11) + disaster relief (value=598) + reader
  data/
    sample_driver_region_data.csv
    knapsack_input.txt          # PLAN-v1 instance, 4-line format
  notebooks/
    01_data_exploration.ipynb
    knapsack_benchmark.ipynb
    knapsack_benchmark_3way.ipynb
    instance_n{10,15,20,22,25}.txt   # Synthetic instances, 3-line format
    presentation_bb.html        # 14-slide reveal.js deck
  docs/
    proposal.md, final_report.md, presentation_notes.md
  results/
    experiment_summary.md       # Tabulated benchmark results
```

---

## Tasks

### Phase 1: Environment & Setup — Complete

- [x] Install Python and create virtual environment (.venv)
- [x] Install PuLP via pip and verify import works
- [x] Install Claude CLI and authenticate
- [x] Initialize Git repository and connect to GitHub
- [x] Create Makefile with setup, test, lint, run, clean targets
- [x] Create pyproject.toml with Poetry configuration + pytest config

### Phase 2: Core Solvers — Complete

- [x] Write PuLP 0-1 Knapsack model matching original Hexaly structure
- [x] Verify PLAN-v1 test instance: value=11 confirmed
- [x] Design real-world disaster relief scenario and 10-item dataset
- [x] Run solver on disaster relief instance — optimal value=598
- [x] Write driver-to-region ILP in PuLP (`src/optimization_model.py`)
- [x] Sample CSV produces optimal cost=13 with full coverage
- [x] Write `tests/test_knapsack.py` covering both instances and the format-reader
- [x] Add `src/main.py` argparse dispatcher so `make run` works end-to-end

### Phase 3: Hand-Built Three-Language B&B — Complete

- [x] Implement Branch & Bound in Python
- [x] Implement Branch & Bound in C++
- [x] Implement Branch & Bound in x86-64 NASM (Win64 ABI, integer-floor bound)
- [x] Implement brute-force baselines in Python, C++, and ASM
- [x] Generate synthetic instances n = 10, 15, 20, 22, 25
- [x] Benchmark B&B vs brute force, all three languages
- [x] Plot algorithmic speedup, language speedup, and pruning effectiveness
- [x] Verify B&B matches PuLP on PLAN-v1 (value=11) and disaster relief (value=598) via pytest
- [x] Make the knapsack reader auto-detect 3-line and 4-line formats

### Phase 4: LLM Solver Generation — Not Started

- [ ] Prompt Claude to generate a knapsack solver from a problem statement
- [ ] Evaluate LLM-generated solver against the hand-built B&B baseline for correctness
- [ ] Prompt Claude to generate a C++ knapsack solver
- [ ] Benchmark LLM-generated solvers on the existing n = 10…25 instances
- [ ] Document all prompts used and quality of generated code

### Phase 5: Capstone Writeup — Mostly Complete

- [x] Final report (`docs/final_report.md`) with motivation, methods, results, conclusions
- [x] Experiment summary (`results/experiment_summary.md`) with tabulated benchmarks
- [x] 14-slide reveal.js presentation (`notebooks/presentation_bb.html`) with embedded speaker notes
- [x] Push all code, tests, and documentation to GitHub
- [ ] Record demo video showing CLI in the workflow
- [ ] Submit final capstone deliverable on Canvas

### Phase 6: Stretch / Future Work — Optional

- [ ] Test solver on OR-Library benchmark instances
- [ ] Add parameterized pytest cases for edge cases (n=0, capacity=0, single oversized item)
- [ ] Scale driver-region instance to a realistic size and measure CBC solve time
- [ ] Attempt Hexaly installation to run the original `.hxm` model

**Phase progress: 5/6 phases complete or mostly complete. The LLM-generation phase remains for a future iteration.**

---

## Methods

### Optimization Modeling

- **PuLP** — Python LP/IP modeling library
- **COIN-CBC (PULP_CBC_CMD)** — open-source branch-and-cut solver, which is itself a Branch & Bound implementation
- Driver-region ILP: binary variables, cost minimization, eligibility/coverage constraints
- Knapsack: binary variables, value maximization, single capacity constraint

### Mathematical Formulation — Knapsack

- Decision variables: `x_i ∈ {0,1}` for each item i
- Objective: `maximize Σ v_i · x_i`
- Constraint: `Σ w_i · x_i ≤ W`

### Hand-Built B&B Algorithm

- Items pre-sorted by `value/weight` ratio descending
- DFS over the binary include/exclude tree, include tried first
- Bound = LP relaxation (fractional knapsack)
- Prune when bound ≤ current incumbent

### Evaluation Metrics

- **Correctness** — solver returns proven optimal value (vs hand-computed or PuLP ground truth)
- **Solve time** — wall-clock, single-run, on the same machine
- **Pruning effectiveness** — nodes explored vs 2^n

### Visualization

- Matplotlib for benchmark plots; reveal.js for the presentation deck

---

## Data Sources

### PLAN-v1 small instance (hand-checkable)

- Weights: `[4, 3, 2]` kg
- Values: `[8, 5, 6]`
- Capacity: 5 kg
- Optimal: **11** (items 2 and 3)
- File: `data/knapsack_input.txt`

### Real-world disaster relief instance

- 10 emergency supplies, helicopter capacity 50 kg
- Optimal: **598** (8 of 10 items selected, 50/50 kg used)
- Code: `src/knapsack_pulp.py`

### Synthetic scaling instances

- n = 10, 15, 20, 22, 25 items
- Random integer weights and values
- Files: `notebooks/instance_n{10,15,20,22,25}.txt`

### Driver-region sample

- 4 drivers × 3 regions, eligibility-filtered cost matrix
- Optimal cost: **13**
- File: `data/sample_driver_region_data.csv`

---

## Testing Strategy

- **pytest** in `tests/test_knapsack.py` (configured via `[tool.pytest.ini_options]` in `pyproject.toml`)
- 7 tests, all passing:
  - PuLP returns value=11 on PLAN-v1
  - PuLP returns value=598 on disaster relief
  - B&B returns value=11 on PLAN-v1
  - B&B returns value=598 on disaster relief
  - Reader accepts the 3-line format
  - Reader accepts the 4-line format
  - Reader rejects malformed input
- Run with `make test` or `pytest -v`

---

## Timeline

| Week | Dates | Milestone |
|------|-------|-----------|
| Week 1 | Apr 21–27 | Hexaly model prepared, blocker identified |
| Week 2 | Apr 28–May 4 | PuLP solver complete, disaster relief verified |
| Week 3 | May 5–11 | Hand-built three-language B&B complete (Python, C++, ASM) |
| Week 4 | May 12–18 | Brute-force baselines, three-language benchmarks, plots |
| Week 5 | May 19–25 | Reveal.js deck, final report, test suite, repo cleanup |
| Week 6+ | (future) | LLM-generated-solver comparison; demo video; final submission |

---

## One-Sentence Summary

This capstone implements a driver-to-region binary ILP in PuLP and complements it with a hand-built three-language (Python, C++, x86-64 ASM) Branch & Bound study of 0-1 knapsack, verified against PuLP ground truth and benchmarked against brute force, demonstrating that algorithmic choice (~10^6× from B&B) dominates language choice (~50× from ASM).
