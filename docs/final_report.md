# CS495 Capstone — Final Report

**Title:** Integer Optimization for Logistics Assignment, with a Three-Language Branch & Bound Study
**Author:** Peter Kamau
**Course:** CS495 Capstone in Data Science — Bellevue College
**Date:** May 2026

## Abstract

This capstone studies discrete optimization in a logistics setting and extends the inquiry into how the same algorithm performs across implementation languages. The project has two tracks:

1. **Production track** — A driver-to-region assignment binary ILP, modeled with PuLP and solved with COIN-CBC.
2. **Research track** — A hand-built Branch & Bound (B&B) 0-1 knapsack solver implemented in three languages (Python, C++, x86-64 assembly), benchmarked against brute-force enumeration.

The unifying observation is that the ILP solver underpinning the production track (CBC) *is* a Branch & Bound implementation. Studying B&B directly therefore informs the engine the production model depends on.

## 1. Motivation

Driver-to-region assignment is a canonical assignment problem: binary choices, linear capacity/coverage constraints, a cost-minimizing objective. Logistics operators encounter variants daily, and bad assignments produce uneven workloads, missed coverage, and avoidable cost. Integer linear programming is a well-understood method for these problems and is solved in practice by Branch & Bound (with cuts and heuristics).

To understand how that engine behaves, this project also implements B&B by hand on a related, smaller problem (0-1 knapsack) where the optimum can be hand-verified. The same algorithm is implemented in three languages so language overhead can be cleanly separated from algorithmic overhead.

## 2. Production Track — Driver-to-Region ILP

### 2.1 Formulation

Let `x_{ij} ∈ {0,1}` be 1 if driver `i` is assigned to region `j`. Given costs `c_{ij}` and an eligibility flag `e_{ij}`:

```
minimize     Σ c_{ij} · x_{ij}    (over eligible pairs only)
subject to   Σ_j x_{ij} ≤ 1       (each driver covers at most one region)
             Σ_i x_{ij} ≥ 1       (each region receives at least one driver)
             x_{ij} ∈ {0,1}
```

Implementation in `src/optimization_model.py`. Sample data in `data/sample_driver_region_data.csv`: 4 drivers, 3 regions, eligibility-filtered cost matrix.

### 2.2 Result

On the sample instance:

- **Optimal cost:** 13
- **Assignments:** D2 → R2 (cost 4), D3 → R3 (cost 5), D4 → R1 (cost 4)
- **Coverage:** 3/3 regions covered with 3 of 4 drivers
- **Solver status:** Optimal solution found (PuLP / COIN-CBC, default settings)

D1 is unassigned — every D1 pair was more expensive than the alternatives selected for those regions. All constraints satisfied.

## 3. Research Track — Branch & Bound in Three Languages

### 3.1 Algorithm

Items are pre-sorted by `value/weight` ratio descending. DFS over the binary include/exclude tree, ordered so include is tried first (the greedy choice). At each node, an upper bound is computed by the LP relaxation (fractional knapsack). If the bound ≤ the current incumbent, the subtree is pruned.

Implementations:

- Python — `src/knapsack_branch_bound.py`
- C++ — `src/knapsack_branch_bound.cpp`
- x86-64 NASM (Win64 ABI, integer-floor bound) — `src/knapsack_branch_bound.asm` + `src/knapsack_bb_asm_wrapper.c`

Brute-force baselines (`src/knapsack_brute_force.{py,cpp,asm}`) enumerate all 2^n subsets and were run on the same instances for comparison.

### 3.2 Benchmark Results

Single-run wall-clock times on six instances (n = 3 to 25):

| n  | Optimum | Brute Python | Brute C++ | B&B Python | B&B C++ | B&B ASM | B&B/Brute (Python) |
|----|---------|--------------|-----------|------------|---------|---------|--------------------|
| 10 | 490     | 1.26 ms      | 0.36 ms   | 20.9 μs    | 6 μs    | 0.5 μs  | ~60×               |
| 15 | 489     | 60.2 ms      | 13.6 ms   | 55.5 μs    | 3 μs    | 0.9 μs  | ~1,085×            |
| 20 | 880     | 2.74 s       | 0.46 s    | 94.6 μs    | 5 μs    | 1.8 μs  | ~28,960×           |
| 22 | 914     | 11.79 s      | 1.90 s    | 57.6 μs    | 4 μs    | 1.0 μs  | ~204,627×          |
| 25 | 1153    | **102.22 s** | 15.60 s   | **96.5 μs**| 5 μs    | 1.7 μs  | **~1,059,000×**    |

Raw data: `benchmark_results_all_three.json`, `benchmark_results_bb.json`.

### 3.3 What the Numbers Show

- **Algorithmic effect.** B&B closes the gap with brute force by orders of magnitude that grow with n. At n = 25, Python B&B is approximately one million times faster than Python brute force and returns the identical optimum.
- **Language effect.** Holding the algorithm fixed, the ranking is consistent: ASM > C++ > Python. Within B&B, C++ averages ~13× over Python and ASM averages ~52× over Python (~3× over C++).
- **Independence.** Algorithmic and language wins multiply. The language ranking is the same regardless of which algorithm is used.

## 4. Connection Between the Two Tracks

PuLP delegates to COIN-CBC, which is a branch-and-cut solver — a Branch & Bound spine extended with cutting planes and heuristics. The driver-to-region ILP is small enough that CBC solves it in milliseconds, but on production-sized instances the same algorithmic structure governs solve time.

The knapsack problem also serves as the right testbed for a future LLM-generated-code study: small, well-defined, with a hand-verifiable ground truth (PLAN-v1 instance, optimal value = 11) and now an automated test suite that detects regressions.

## 5. Verification

A pytest suite (`tests/test_knapsack.py`) verifies both implementations against known-answer instances:

- PLAN-v1 small instance: value = 11 (PuLP and B&B)
- Disaster relief instance: value = 598 (PuLP and B&B)
- The format-reader accepts both 3-line and 4-line input formats and rejects malformed input

```
$ pytest -v
======================== 7 passed in 0.29s ========================
```

## 6. Reproducibility

| Command | Effect |
|---------|--------|
| `make setup` | install dependencies via Poetry |
| `make test` | run the pytest suite |
| `python src/main.py driver-region` | solve the ILP on the sample CSV |
| `python src/main.py knapsack-pulp` | solve PLAN-v1 and disaster-relief via PuLP |
| `python src/main.py knapsack-bb --input data/knapsack_input.txt` | solve via hand-built B&B |

## 7. Limitations & Future Work

- **LLM-generated-solver comparison** was the originally proposed Phase 4 of this project and was not completed within this iteration. The hand-built B&B suite serves as ground truth for a future study that asks Claude to generate a solver and measures whether it finds B&B or defaults to brute force.
- **OR-Library benchmark instances** were planned but not run; synthetic n = 10…25 instances were sufficient to demonstrate the algorithmic effect.
- **Hexaly** could not be installed locally and was replaced by the PuLP/CBC track. The originally written `src/knapsack.hxm` is preserved for future reference.
- The driver-region model uses a synthetic 4×3 dataset; scaling to a realistic dataset would stress CBC on the same problem structure.

## 8. Conclusion

The headline result is a verified ~10^6× speedup on n = 25 from B&B over brute force, holding both the language and the machine constant. Language gains exist but are dwarfed by the algorithmic gain — algorithmic choice dominates language choice. The same B&B algorithm sits inside CBC, the solver that handles the driver-to-region track. The two tracks of this capstone are not separate projects but two views of the same machinery.
