# CS495 - Logistics Optimization with LLM Assistance

## Project Title
Integer Optimization under LLM Low Language Levels for Logistics Assignment

## Overview
This capstone project studies how integer optimization can be used to solve a logistics assignment problem, specifically assigning drivers to delivery regions under realistic constraints. The project also explores whether large language models (LLMs) can assist in generating parts of the optimization model or implementation.

The main goal is to build a working optimization system that produces valid driver-to-region assignments while comparing hand-built optimization code against LLM-assisted model generation.

## Motivation
Logistics systems often require fast and correct assignment decisions. Poor assignments can lead to uneven workloads, missed coverage, delays, and inefficiency. Because driver-region assignment is naturally constrained, integer optimization is a strong method for solving this type of problem.

This project is also motivated by interest in understanding whether LLMs can help create structured optimization software in a reliable way, especially for decision problems that depend on correct mathematical constraints.

## Problem Statement
Given a set of drivers and delivery regions, assign drivers to regions in a way that:
- satisfies coverage requirements
- respects driver availability
- avoids invalid driver-region assignments
- balances workload
- minimizes cost, delay, or assignment imbalance

## Project Goals
- Build a baseline integer optimization model for driver-to-region assignment
- Create or simulate a logistics dataset for testing
- Compare hand-built optimization code with LLM-assisted code generation
- Evaluate assignment quality and model correctness
- Document the strengths and weaknesses of LLM support for structured optimization tasks

## Example Formulation
Let:

- `x(i,j) = 1` if driver `i` is assigned to region `j`
- `x(i,j) = 0` otherwise

Possible objective:
- Minimize total assignment cost
- Minimize workload imbalance
- Maximize assignment efficiency

Possible constraints:
- Each driver is assigned to at most one region
- Each region must receive enough driver coverage
- Invalid driver-region combinations are not allowed
- Total workload assigned to a driver must stay within limits

## Dataset
This project will likely use a synthetic or small simulated dataset with fields such as:
- driver_id
- region_id
- driver_availability
- region_demand
- assignment_cost
- workload_score
- eligibility_flag

## Methods
- Integer Linear Programming (ILP)
- Branch and Bound through solver libraries
- LLM-assisted code generation for model drafting or implementation support

## Tools and Technologies
- Python
- Pandas
- NumPy
- PuLP or OR-Tools
- Jupyter Notebook / VS Code
- Matplotlib
- GitHub

## Evaluation
The project will evaluate:
- constraint satisfaction
- total assignment cost
- region coverage rate
- workload balance
- invalid assignment avoidance
- runtime
- quality of LLM-assisted implementation compared to manual implementation

## Expected Deliverables
- source code
- optimization model
- dataset
- experiment results
- final report
- presentation slides

## Repository Structure
- `data/` for raw and processed datasets
- `notebooks/` for experiments and exploration
- `src/` for reusable code
- `results/` for outputs and summaries
- `docs/` for proposal and report materials
- `slides/` for presentation materials

## Status
In progress

## Author
Peter Kamau
