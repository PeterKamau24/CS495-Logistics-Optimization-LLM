# PLAN.md

## Project Overview

**Title:** LLM-Assisted Generation of Low-Level Discrete Optimization Solvers
**Author:** Peter Kamau
**Course:** CS495 Capstone in Data Science — Bellevue College
**Date:** April 27, 2026

### Description
This capstone investigates whether large language models (LLMs) can assist in generating correct, efficient, low-level implementations of discrete optimization solvers. Starting with the classical 0-1 Knapsack Problem (a binary integer programming problem), the project compares LLM-generated code against hand-written implementations and established solver libraries.

### Objectives
- Implement a verified 0-1 Knapsack solver using PuLP and demonstrate it on a real-world scenario
- Use Claude CLI as an active participant in the code generation and planning workflow
- Establish a baseline optimal solution to use as ground truth for future solver comparisons
- Compare PuLP, hand-written branch-and-bound, and LLM-generated low-level solver implementations

---

## Environment Setup

### Requirements
- Python 3.13
- Poetry (or pip + venv) for dependency management
- Virtual environment (.venv)
- Git

### Quick Start (Windows — primary)
```powershell
# Install prerequisites
winget install OpenJS.NodeJS.LTS
winget install Python.Python.3.13

# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Clone and set up project
git clone https://github.com/YOUR_USER/YOUR_REPO.git
cd YOUR_REPO
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Launch Claude
claude
```

### Quick Start (macOS / Linux)
```bash
# Install Node.js + Python (macOS)
brew install node python@3.13

# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Clone and set up project
git clone https://github.com/YOUR_USER/YOUR_REPO.git
cd YOUR_REPO
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test

# Launch Claude
claude
```

### Makefile Alternative (Windows)
If `make` is not available on Windows, run the equivalent commands directly:
```powershell
python -m pytest tests/        # replaces: make test
python -m ruff check .         # replaces: make lint
python src/main.py             # replaces: make run
```

### Dependencies
- `pulp` — linear/integer programming modeling library
- `pytest` — unit testing framework
- `ruff` — fast Python linter
- `numpy` — numerical operations (future iterations)
- `pandas` — data manipulation (future iterations)

---

## Architecture

```
my-capstone-project/
  PLAN.md                       # This file
  README.md                     # Project description
  Makefile                      # Automation commands
  pyproject.toml                # Poetry config & dependencies
  requirements.txt              # Pip fallback
  .gitignore                    # Ignore .venv, __pycache__, etc.
  src/
    __init__.py
    main.py                     # Entry point
    knapsack_pulp.py            # Core PuLP 0-1 knapsack solver
  tests/
    test_knapsack.py            # Verifies PLAN.md instance (value=11)
  data/
    raw/
      knapsack_input.txt        # Original PLAN.md test instance
    processed/                  # Cleaned data (future iterations)
  notebooks/
    exploration.ipynb           # EDA and experimentation
```

---

## Tasks

### Phase 1: Environment & Setup
- [x] Install Python 3.13 and create virtual environment (.venv)
- [x] Install PuLP via pip and verify import works
- [x] Install Claude CLI and authenticate
- [x] Initialize Git repository and connect to GitHub
- [ ] Create Makefile with setup, test, lint, run, clean targets
- [ ] Create pyproject.toml with Poetry configuration

### Phase 2: Core Solver (Iteration 2 — Complete)
- [x] Write PuLP 0-1 Knapsack model matching Hexaly structure from PLAN v1
- [x] Verify PLAN v1 test instance: value=11 confirmed
- [x] Design real-world disaster relief scenario and 10-item dataset
- [x] Run solver on disaster relief instance — optimal value=598
- [x] Write unit test in tests/test_knapsack.py using pytest

### Phase 3: Expansion & Analysis
- [ ] Test solver on OR-Library benchmark instances
- [ ] Add parameterized pytest cases for edge cases
- [ ] Measure solve time as function of instance size (n = 10 to 500)
- [ ] Plot solve time vs. instance size using matplotlib
- [ ] Attempt Hexaly installation to run original PLAN v1 model

### Phase 4: LLM Solver Generation
- [ ] Prompt Claude CLI to generate a branch-and-bound solver in Python
- [ ] Evaluate LLM-generated solver against PuLP baseline for correctness
- [ ] Prompt Claude CLI to generate a C++ knapsack solver
- [ ] Benchmark C++ solver vs. PuLP on large instances
- [ ] Document all prompts used and quality of generated code

### Phase 5: Capstone Writeup
- [ ] Write PLAN_V3.md after class feedback
- [ ] Produce final comparison report: Hexaly vs. PuLP vs. LLM solvers
- [ ] Record demo video showing Claude CLI in the workflow
- [ ] Push all code, tests, and documentation to GitHub
- [ ] Submit final capstone deliverable on Canvas

**Total tasks: 25  |  Completed: 9  |  Remaining: 16**

---

## Methods

### Optimization Modeling
- **PuLP** — Python LP/IP modeling library
- **COIN-BC (PULP_CBC_CMD)** — open-source branch-and-cut solver
- Problem type: Binary Integer Program (LpBinary variables, LpMaximize sense)

### Mathematical Formulation
- Decision variables: `x_i ∈ {0, 1}` for each item i
- Objective: `maximize Σ v_i · x_i`
- Constraint: `Σ w_i · x_i ≤ W`

### Future Solvers (for comparison)
- Hand-written branch-and-bound in Python
- Hand-written branch-and-bound in C++
- LLM-generated solvers (Claude CLI)
- Hexaly (commercial solver, if installation succeeds)

### Evaluation Metrics
- **Correctness** — does the solver find the proven optimal value?
- **Solve time** — wall-clock time vs. instance size
- **Code quality** — readability, lines of code, test coverage

### Visualization
- Matplotlib for solve-time scaling plots
- Markdown tables for comparison results

---

## Data Sources

### Iteration 2 Test Instance (PLAN v1)
- **Source:** Hand-constructed in original PLAN.md (Iteration 1)
- **Weights:** [4, 3, 2] kg
- **Values:** [8, 5, 6]
- **Capacity:** 5 kg
- **Optimal value:** 11 (items 2 and 3 selected)
- **Purpose:** Hand-checkable verification baseline

### Real-World Instance — Disaster Relief
- **Source:** Scenario designed by author based on publicly documented humanitarian relief priorities (UNHCR, Red Cross emergency supply guidelines)
- **Items:** 10 emergency supplies with weights (kg) and impact scores
- **Capacity:** 50 kg (helicopter weight limit)
- **Optimal value:** 598 (8 of 10 items selected, 50/50 kg used)

### Future Data Sources
- **OR-Library** — Brunel knapsack benchmarks: http://people.brunel.ac.uk/~mastjjb/jeb/orlib/knapinfo.html
- **Pisinger's instances** — large-scale academic benchmarks
- **Custom generated instances** — for scaling analysis (n = 10, 50, 100, 500 items)

---

## Testing Strategy

- **Unit tests** with pytest in `tests/test_knapsack.py`
- **Verification test:** assert solver returns value=11 for PLAN v1 instance
- **Edge cases (planned):** empty item set, capacity=0, single item exceeds capacity
- **Parameterized tests (planned):** OR-Library benchmark instances with known optimal values
- **Run tests:** `pytest tests/` or `make test`

---

## Timeline

| Week | Dates | Milestone | Deliverable |
|------|-------|-----------|-------------|
| Week 1 | Apr 21–27 | Iteration 1 — Hexaly model prepared, blocker identified | PLAN.md (v1) |
| Week 2 | Apr 28–May 4 | Iteration 2 — PuLP solver complete, real-world results verified | **PLAN.md (this) + knapsack_pulp.py — DUE MAY 4** |
| Week 3 | May 5–11 | Environment hardened — Makefile, Poetry, pytest suite | Makefile, pyproject.toml |
| Week 4 | May 12–18 | OR-Library benchmarks — scaling analysis and plots | benchmark.py, solve_time_plot.png |
| Week 5 | May 19–25 | LLM solver generation — Claude generates branch-and-bound | llm_solver.py, prompt_log.md |
| Week 6 | May 26–Jun 1 | C++ solver — Claude generates, compile and benchmark | knapsack.cpp, comparison table |
| Week 7 | Jun 2–8 | Full comparison — Hexaly vs PuLP vs LLM solvers | PLAN_V3.md, comparison_report.md |
| Week 8 | Jun 9–15 | Capstone writeup, demo video, final polish | Final submission on Canvas + GitHub |

---

## One-Sentence Summary

In this iteration, Claude read the original PLAN.md, resolved the Hexaly environment blocker by implementing an equivalent 0-1 Knapsack solver in PuLP, verified the model against the original hand-checked instance (value=11), applied it to a real-world disaster relief scenario producing an optimal result (value=598), and produced this fully structured PLAN.md covering all required capstone sections.
