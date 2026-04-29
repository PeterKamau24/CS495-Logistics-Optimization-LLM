# PLAN.md

## Project Title
LLM-Assisted Generation of Low-Level Discrete Optimization Solvers

## Objective for This Iteration
For this iteration, I want to demonstrate a real binary optimization problem using Hexaly on the 0-1 Knapsack Problem. I will use Claude CLI to help generate and refine the Hexaly model and input file, execute the model in Hexaly, and show actual results in class.

## Problem
### 0-1 Knapsack Problem

The 0-1 Knapsack Problem considers a set of items, where each item has a weight and a value. The goal is to choose a subset of items so that the total weight does not exceed the knapsack capacity while the total value is maximized.

## Why I Chose This Problem
I chose knapsack because it is a standard binary integer optimization problem, easy to explain mathematically, and directly connected to the larger discrete optimization direction of my capstone project.

## Mathematical Formulation

### Decision Variables
For each item i:

- x_i = 1 if item i is selected
- x_i = 0 otherwise

### Objective
Maximize:

sum(v_i x_i)

### Constraint
Subject to:

sum(w_i x_i) <= W

### Variable Domain
x_i in {0,1}

This makes the problem a binary integer optimization problem.

## Example Instance
For my first test instance, I used:

- weights = [4, 3, 2]
- values = [8, 5, 6]
- capacity = 5

Expected best result:
- select the second and third items
- best total value = 11
- total weight = 5

## Files Used
- PLAN.md
- src/knapsack.hxm
- data/knapsack_input.txt

## Claude CLI Step
I used Claude CLI to help generate and organize the files needed for this iteration.

### Claude CLI Task
I asked Claude CLI to help create:
- a Hexaly knapsack model file
- a small input file for the knapsack instance
- a clean workflow for running the model

### Claude CLI Prompt Summary
I prompted Claude CLI to generate a real Hexaly 0-1 knapsack example with:
- Boolean decision variables
- a weight constraint
- a value-maximizing objective
- a small test instance that could be verified by hand

## Hexaly Model Summary
The Hexaly model includes:
- one Boolean decision variable for each item
- one intermediate expression for total weight
- one intermediate expression for total value
- one capacity constraint
- one objective that maximizes total value

## Execution Command
I attempted to execute the model with:

hexaly .\src\knapsack.hxm inFileName=.\data\knapsack_input.txt

## Actual Results
I prepared the Hexaly knapsack model file and the input instance file, but I was not yet able to execute the model locally because the Hexaly executable is not installed or not available in my system PATH on this machine.

## Current Blocker
When I ran:
where.exe hexaly

PowerShell returned that no matching executable was found. I also searched under C:\Program Files and C:\Program Files (x86) and did not find hexaly.exe.

## What Worked
- I created a real Hexaly model for the 0-1 knapsack problem.
- I created a matching input instance file.
- I organized the work in my Git repository.
- I connected the optimization model directly to my capstone topic.

## What Needs Improvement
- I still need to install or locate Hexaly on my machine.
- I need to complete the execution step and save real solver output.
- I want to test more instances after the first successful run.
- I want to compare Hexaly later with my own implementations.

## Connection to My Capstone
This Hexaly knapsack example gives me a real starting point for the capstone. It shows the structure of a binary optimization problem and gives me a concrete model that I can later compare against Python, hand-written C++, and LLM-generated low-level solver implementations.

## Initial Outcome
For this first class checkpoint, I was able to:
- define a real binary optimization problem
- use Claude CLI as part of the setup workflow
- prepare real Hexaly model files
- identify the environment blocker preventing execution
- move from a general project idea to a concrete optimization setup

## Next Step
After class feedback, I will prepare PLAN_V2.md.

My likely next steps are:
- install or locate Hexaly
- execute the knapsack model successfully
- save actual output
- test more knapsack instances
- refine the evaluation plan

## One-Sentence Summary
For this first iteration, I used Claude CLI and Hexaly-based model setup to prepare a real 0-1 knapsack optimization example, and I identified the local environment blocker that must be resolved before full execution.
