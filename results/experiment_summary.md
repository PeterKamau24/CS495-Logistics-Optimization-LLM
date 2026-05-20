# Experiment Summary

All benchmark numbers are wall-clock single-run times. Raw data sources:

- `benchmark_results.json` — brute force, Python vs C++
- `benchmark_results_all_three.json` — brute force, three languages
- `benchmark_results_bb.json` — Branch & Bound, three languages
- `notebooks/benchmark_3way_summary.csv` — averaged runs for n = 5…17 (PuLP/CBC vs C++ B&B vs ASM B&B)

## A. Brute Force vs Branch & Bound (Python)

| n  | Optimum | Brute Force  | Branch & Bound | Speedup            |
|----|---------|--------------|----------------|--------------------|
| 3  | 11      | 4.8 μs       | 7.7 μs         | 0.6× (B&B overhead) |
| 10 | 490     | 1.26 ms      | 20.9 μs        | 60×                |
| 15 | 489     | 60.2 ms      | 55.5 μs        | 1,085×             |
| 20 | 880     | 2.74 s       | 94.6 μs        | 28,960×            |
| 22 | 914     | 11.79 s      | 57.6 μs        | 204,627×           |
| 25 | 1153    | **102.22 s** | **96.5 μs**    | **~1,059,000×**    |

At very small n the bookkeeping overhead of B&B costs more than the saved enumeration — the crossover happens around n ≈ 10. Past that point the gap grows geometrically.

## B. Three-Language Comparison — Branch & Bound

| n  | Python B&B | C++ B&B | ASM B&B | C++ / Python | ASM / Python | ASM / C++ |
|----|------------|---------|---------|--------------|--------------|-----------|
| 3  | 7.7 μs     | 2 μs    | 0.2 μs  | 3.85×        | 38.5×        | 10×       |
| 10 | 20.9 μs    | 6 μs    | 0.5 μs  | 3.48×        | 41.8×        | 12×       |
| 15 | 55.5 μs    | 3 μs    | 0.9 μs  | 18.5×        | 61.7×        | 3.3×      |
| 20 | 94.6 μs    | 5 μs    | 1.8 μs  | 18.9×        | 52.6×        | 2.8×      |
| 22 | 57.6 μs    | 4 μs    | 1.0 μs  | 14.4×        | 57.6×        | 4.0×      |
| 25 | 96.5 μs    | 5 μs    | 1.7 μs  | 19.3×        | 56.8×        | 2.9×      |

Across n = 3…25:

- **C++ avg over Python:** ~13×
- **ASM avg over Python:** ~52×
- **ASM avg over C++:** ~3×

Note: at n = 22 the B&B time *decreases* from n = 20, because the LP-relaxation bound happens to fire early on that particular instance — a reminder that B&B's wall-clock cost is instance-specific, not strictly monotone in n.

## C. Three-Language Comparison — Brute Force

| n  | Python Brute | C++ Brute | ASM Brute | ASM / Python |
|----|--------------|-----------|-----------|--------------|
| 10 | 1.26 ms      | 0.36 ms   | 0.089 ms  | 14.2×        |
| 15 | 60.2 ms      | 13.6 ms   | 3.7 ms    | 16.3×        |
| 20 | 2.74 s       | 0.46 s    | 0.131 s   | 20.9×        |
| 22 | 11.79 s      | 1.90 s    | 0.558 s   | 21.1×        |
| 25 | 102.22 s     | 15.60 s   | 4.88 s    | 21.0×        |

## D. Driver-to-Region ILP

Instance: `data/sample_driver_region_data.csv` (4 drivers, 3 regions, eligibility-filtered).

- **Optimal cost:** 13
- **Solver:** PuLP / COIN-CBC, default settings
- **Status:** Optimal solution found
- **Assignments:** D2 → R2 (cost 4), D3 → R3 (cost 5), D4 → R1 (cost 4)
- **Coverage:** 3/3 regions; 3 of 4 drivers assigned

## E. Verification

`tests/test_knapsack.py` covers:

| Test | Result |
|---|---|
| PuLP on PLAN-v1 instance returns value=11 | pass |
| PuLP on disaster-relief returns value=598 | pass |
| B&B on PLAN-v1 returns value=11 | pass |
| B&B on disaster-relief returns value=598 | pass |
| Reader accepts the 3-line format | pass |
| Reader accepts the 4-line format | pass |
| Reader rejects malformed input | pass |

`pytest -v` — 7/7 passing.

## Key Observations

1. **Algorithm dominates language.** A ~10^6× speedup from B&B vs ~50× from ASM. Both dimensions matter, but they aren't comparable in magnitude.
2. **B&B speedup grows with n.** From 60× at n = 10 to over a million× at n = 25.
3. **ASM's edge over C++ is modest (~3×) but consistent.** The cost is implementation complexity and lost portability.
4. **The PuLP/CBC solver is built on the same B&B algorithm** studied here — the two tracks of this project converge on the same engine.
