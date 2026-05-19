"""
Brute Force Solver for 0-1 Knapsack Problem

This module implements a complete enumeration approach to solve the 0-1 knapsack problem.
Time complexity: O(2^n) where n is the number of items.
Space complexity: O(n) for storing the solution.

The brute force approach evaluates all possible subsets of items (2^n combinations)
and selects the one with maximum value that doesn't exceed the capacity constraint.
"""

from typing import List, Tuple
import time


def read_knapsack_instance(filepath: str) -> Tuple[int, int, List[int], List[int]]:
    """
    Read a knapsack instance from a text file.

    Expected format:
        Line 1: n_items capacity
        Line 2: weight_1 weight_2 ... weight_n
        Line 3: value_1 value_2 ... value_n

    Args:
        filepath: Path to the instance file

    Returns:
        Tuple of (n_items, capacity, weights, values)
    """
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # Parse first line: n_items and capacity
    first_line = lines[0].split()
    n_items = int(first_line[0])
    capacity = int(first_line[1])

    # Parse weights (line 2)
    weights = list(map(int, lines[1].split()))

    # Parse values (line 3)
    values = list(map(int, lines[2].split()))

    # Validation
    assert len(weights) == n_items, f"Expected {n_items} weights, got {len(weights)}"
    assert len(values) == n_items, f"Expected {n_items} values, got {len(values)}"

    return n_items, capacity, weights, values


def knapsack_brute_force(weights: List[int], values: List[int], capacity: int) -> Tuple[int, List[int]]:
    """
    Solve 0-1 knapsack problem using complete enumeration (brute force).

    Evaluates all 2^n possible subsets of items and returns the optimal solution.

    Algorithm:
        For each subset S ⊆ {0, 1, ..., n-1}:
            if sum(weights[i] for i in S) ≤ capacity:
                compute total_value = sum(values[i] for i in S)
                track maximum value and corresponding subset

    Args:
        weights: List of item weights
        values: List of item values
        capacity: Knapsack capacity constraint

    Returns:
        Tuple of (max_value, selected_items) where selected_items is list of selected item indices
    """
    n = len(weights)
    max_value = 0
    best_selection = []

    # Enumerate all 2^n subsets using binary representation
    # Each integer from 0 to 2^n - 1 represents a unique subset
    # Bit i indicates whether item i is included (1) or not (0)
    for subset_mask in range(1 << n):  # 2^n iterations
        total_weight = 0
        total_value = 0
        current_selection = []

        # Decode the binary representation
        for item_idx in range(n):
            # Check if bit item_idx is set in subset_mask
            if subset_mask & (1 << item_idx):
                total_weight += weights[item_idx]
                total_value += values[item_idx]
                current_selection.append(item_idx)

        # Check feasibility constraint and optimality
        if total_weight <= capacity and total_value > max_value:
            max_value = total_value
            best_selection = current_selection.copy()

    return max_value, best_selection


def solve_instance(filepath: str, verbose: bool = True) -> dict:
    """
    Solve a knapsack instance from file and return detailed results.

    Args:
        filepath: Path to instance file
        verbose: Whether to print solution details

    Returns:
        Dictionary containing solution details and timing information
    """
    # Read instance
    n_items, capacity, weights, values = read_knapsack_instance(filepath)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Solving instance: {filepath}")
        print(f"{'='*60}")
        print(f"Number of items: {n_items}")
        print(f"Capacity: {capacity}")
        print(f"Total combinations to evaluate: {2**n_items:,}")

    # Solve with timing
    start_time = time.perf_counter()
    max_value, selected_items = knapsack_brute_force(weights, values, capacity)
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time

    # Calculate solution statistics
    total_weight = sum(weights[i] for i in selected_items)
    n_selected = len(selected_items)

    if verbose:
        print(f"\n{'─'*60}")
        print(f"SOLUTION")
        print(f"{'─'*60}")
        print(f"Optimal value: {max_value}")
        print(f"Total weight: {total_weight}/{capacity}")
        print(f"Items selected: {n_selected}/{n_items}")
        print(f"Selected item indices: {sorted(selected_items)}")
        print(f"\nItem details:")
        print(f"  {'Item':<6} {'Weight':<8} {'Value':<8}")
        print(f"  {'-'*6} {'-'*8} {'-'*8}")
        for idx in sorted(selected_items):
            print(f"  {idx:<6} {weights[idx]:<8} {values[idx]:<8}")
        print(f"\n{'─'*60}")
        print(f"Computation time: {elapsed_time:.6f} seconds")
        print(f"{'='*60}\n")

    return {
        'instance': filepath,
        'n_items': n_items,
        'capacity': capacity,
        'optimal_value': max_value,
        'total_weight': total_weight,
        'n_selected': n_selected,
        'selected_items': sorted(selected_items),
        'time_seconds': elapsed_time,
        'weights': weights,
        'values': values
    }


def main():
    """
    Main entry point - solve all knapsack instances in notebooks/ directory.
    """
    import os

    # List of instance files
    instance_files = [
        'notebooks/plan_md_instance.txt',
        'notebooks/instance_n10.txt',
        'notebooks/instance_n15.txt',
        'notebooks/instance_n20.txt',
        'notebooks/instance_n22.txt',
        'notebooks/instance_n25.txt',
    ]

    results = []

    print("\n" + "="*60)
    print("0-1 KNAPSACK PROBLEM - BRUTE FORCE SOLVER")
    print("="*60)

    for instance_file in instance_files:
        if os.path.exists(instance_file):
            try:
                result = solve_instance(instance_file, verbose=True)
                results.append(result)
            except Exception as e:
                print(f"Error solving {instance_file}: {e}\n")
        else:
            print(f"File not found: {instance_file}\n")

    # Summary table
    if results:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"{'Instance':<25} {'n':<4} {'Opt Val':<8} {'Time (s)':<12}")
        print("-"*60)
        for res in results:
            instance_name = os.path.basename(res['instance'])
            print(f"{instance_name:<25} {res['n_items']:<4} {res['optimal_value']:<8} {res['time_seconds']:<12.6f}")
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
