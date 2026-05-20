# Capstone Proposal

## Project Title

Integer Optimization for Logistics Assignment, with a Three-Language Branch & Bound Study

## Project Summary

This project builds a binary integer linear program for driver-to-region assignment and complements it with a study of the Branch & Bound algorithm that powers the underlying solver. To make B&B concrete and measurable, the project implements it on the 0-1 knapsack problem in three languages — Python, C++, and x86-64 assembly — and benchmarks each against a brute-force baseline.

A secondary research direction (not completed in the current iteration) is whether large language models can generate correct, efficient solver code. The hand-built B&B implementations serve as ground truth for that future comparison.

## Motivation

Real logistics assignments are integer programming problems: binary decisions, capacity and coverage constraints, a cost objective. Production-grade solvers — PuLP, COIN-CBC — handle these via Branch & Bound. Studying B&B directly is therefore studying the engine the production track depends on. Holding the algorithm fixed across three languages then isolates implementation overhead from algorithmic overhead.

## Goals

- Build a working ILP for driver-to-region assignment (PuLP / CBC)
- Implement and verify B&B on the 0-1 knapsack in three languages
- Benchmark B&B against brute force across n = 3…25 to quantify the algorithmic speedup
- Establish a pytest-verified ground truth for a future LLM-generated-solver comparison

## Deliverables

- Source code for the ILP and the three B&B implementations
- A pytest suite verifying both solvers against known-answer instances (`tests/test_knapsack.py`)
- Reveal.js presentation (`notebooks/presentation_bb.html`)
- Benchmark JSON, plots, and a tabulated summary (`results/experiment_summary.md`)
- Final report (`docs/final_report.md`)
