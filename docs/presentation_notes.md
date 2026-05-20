# Presentation Notes

## Current Deck

Slides live in `notebooks/presentation_bb.html` — a 14-slide reveal.js deck with speaker notes embedded on every slide. Open the file in a browser (use `python -m http.server 8000` from the repo root so the `../*.png` image paths resolve) and press `S` to open speaker view.

## Title

**Branch & Bound for the 0-1 Knapsack Problem — Python, C++, and x86-64 Assembly**

## Talk Outline

1. Title / introduction
2. The 0-1 knapsack problem and why it matters for logistics
3. A concrete 4-item, capacity-8 instance to trace through
4. Brute force baseline — 2^n enumeration
5. Branch & Bound — the idea (branch / bound / prune)
6. Decision tree on the tiny instance — what pruning looks like
7. The LP relaxation upper bound
8. How much pruning saves at scale (2^n vs nodes explored)
9. Same algorithm in three languages
10. Algorithmic win — B&B vs brute force (~10^6× at n = 25)
11. Language win — Python vs C++ vs ASM (ASM ~52× over Python)
12. Connection to the capstone — CBC is B&B
13. Capstone pipeline diagram showing both tracks
14. Takeaways and Q&A

## Target Length

7 minutes. Speaker notes pace each slide individually.

## Supporting Visuals (referenced by the deck)

- `bb_decision_tree.png` — annotated B&B tree on the tiny instance, slide 6
- `pruning_effectiveness.png` — 2^n vs nodes explored, slide 8
- `bb_vs_brute_force_speedup.png` — language-by-language algorithmic speedup, slide 10
- `benchmark_bb_comparison.png` — three-way B&B language comparison, slide 11
- `project_pipeline.png` — capstone pipeline with both tracks, slide 13

## Key Messages

1. **Algorithmic choice dominates language choice.** A million-fold gain from B&B over brute force; a fifty-fold gain from ASM over Python. Both matter, but they aren't on the same scale.
2. **Running the same algorithm in three languages cleanly separates language overhead from algorithm overhead.** The language ranking (ASM > C++ > Python) is consistent regardless of algorithm.
3. **The B&B work directly informs the capstone's production track** — PuLP/CBC is a Branch & Bound solver, so studying B&B is studying the engine the ILP track depends on.

## Q&A Prep

See speaker notes on slide 14. Anticipated questions: why not dynamic programming, why assembly, whether the LLM track uses this work.
