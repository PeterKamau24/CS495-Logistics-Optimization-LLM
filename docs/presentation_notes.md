# Presentation Notes

## Current Deck

Slides live in `notebooks/presentation_bb.html` — a 15-slide reveal.js deck with speaker notes embedded on every slide. Image paths reference `../results/figures/*.png`, so serve from the repo root (`python -m http.server 8000`) and open `http://localhost:8000/notebooks/presentation_bb.html`. Press `S` to open speaker view.

## Title

**Branch & Bound for the 0-1 Knapsack Problem — Python, C++, and x86-64 Assembly**

## Talk Outline

1. Title / introduction
2. The 0-1 knapsack problem and why it matters for logistics
3. A concrete 4-item, capacity-8 instance to trace through
4. Brute force baseline — 2^n enumeration (code)
5. Brute force benchmark — Python vs C++ vs ASM
6. Exponential scaling quantified — curve fits, growth rate, performance gap evolution
7. Branch & Bound — the idea (branch / bound / prune)
8. Decision tree on the tiny instance — what pruning looks like
9. The LP relaxation upper bound
10. Same algorithm in three languages (code)
11. B&B benchmark — Python vs C++ vs ASM (microseconds)
12. Connection to the capstone — CBC is B&B
13. Capstone pipeline diagram showing both tracks
14. Algorithm beats hardware — B&B vs brute force across languages
15. Takeaways and Q&A

## Target Length

7 minutes. Speaker notes pace each slide individually.

## Supporting Visuals (referenced by the deck)

- `results/figures/benchmark_all_three.png` — brute-force benchmark across three languages, slide 5
- `results/figures/scaling_all_three.png` — exponential scaling analysis (curve fits, growth rate, performance gap), slide 6
- `results/figures/bb_decision_tree.png` — annotated B&B tree on the tiny instance, slide 8
- `results/figures/benchmark_bb_comparison.png` — three-way B&B language comparison, slide 11
- `results/figures/project_pipeline.png` — capstone pipeline with both tracks, slide 13
- `results/figures/benchmark_presentation.png` — algorithm-beats-hardware head-to-head (B&B vs brute force, all languages), slide 14

## Key Messages

1. **Algorithmic choice dominates language choice.** A million-fold gain from B&B over brute force; a fifty-fold gain from ASM over Python. Both matter, but they aren't on the same scale.
2. **Running the same algorithm in three languages cleanly separates language overhead from algorithm overhead.** The language ranking (ASM > C++ > Python) is consistent regardless of algorithm.
3. **The B&B work directly informs the capstone's production track** — PuLP/CBC is a Branch & Bound solver, so studying B&B is studying the engine the ILP track depends on.

## Added Slides — Speaker Notes

### Slide 6 — Exponential Scaling, Quantified

This slide is the rigor check on the brute-force claim. Left panel: I fit T = a · 2^n to each language's data — the fits are nearly perfect, which confirms the asymptotic. Middle panel: between consecutive instance sizes, the runtime ratio sits right on the theoretical doubling line. Right panel: the speedup gap between Python and the compiled languages isn't constant — it grows, because a constant-factor advantage applied to exponential work shows up more dramatically as n increases. This is the empirical case for "you can't out-engineer 2^n."

### Slide 14 — Algorithm Beats Hardware

This is the headline chart. Three lines climbing the exponential — C++ brute force, x86-64 ASM brute force — and one flat line near the bottom: PuLP/CBC, which uses Branch & Bound. The crossover annotation marks where brute force becomes slower than the smart algorithm. At n=25 the gap is two orders of magnitude. The punchline: PuLP is written in Python and calls a C solver, so it's not even the fastest stack — but the algorithm choice dominates the language choice. This is the visual proof of the takeaway I'll land on next.

## Q&A Prep

See speaker notes on the final slide. Anticipated questions: why not dynamic programming, why assembly, whether the LLM track uses this work.
