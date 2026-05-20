"""
Branch and Bound Solver for 0-1 Knapsack Problem

Replaces the O(2^n) brute force enumeration with a DFS Branch and Bound
search guided by a linear (LP) relaxation upper bound.

Pipeline:
    1. Items are pre-sorted by value/weight ratio descending.
    2. DFS tries "include" before "exclude" so a strong incumbent appears early.
    3. Bound = current_value + fractional knapsack over remaining items.
       If bound <= best_value, the subtree is pruned.
    4. Infeasible (weight > capacity) branches are pruned immediately.

Worst case is still O(2^n), but the bound typically collapses the search
by orders of magnitude on non-pathological instances.
"""

from typing import List, Tuple
import time


def read_knapsack_instance(filepath: str) -> Tuple[int, int, List[int], List[int]]:
    """
    Read a knapsack instance from a text file. Accepts either format:

        3-line:
            Line 1: n_items capacity
            Line 2: weight_1 ... weight_n
            Line 3: value_1 ... value_n

        4-line (canonical, see data/knapsack_input.txt):
            Line 1: n_items
            Line 2: weight_1 ... weight_n
            Line 3: value_1 ... value_n
            Line 4: capacity
    """
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) == 4:
        n_items = int(lines[0])
        weights = list(map(int, lines[1].split()))
        values = list(map(int, lines[2].split()))
        capacity = int(lines[3])
    elif len(lines) == 3:
        first = lines[0].split()
        n_items = int(first[0])
        capacity = int(first[1])
        weights = list(map(int, lines[1].split()))
        values = list(map(int, lines[2].split()))
    else:
        raise ValueError(
            f"Expected 3 or 4 non-empty lines in {filepath}, got {len(lines)}"
        )

    assert len(weights) == n_items, f"Expected {n_items} weights, got {len(weights)}"
    assert len(values) == n_items, f"Expected {n_items} values, got {len(values)}"

    return n_items, capacity, weights, values


def knapsack_branch_bound(weights: List[int], values: List[int], capacity: int) -> Tuple[int, List[int]]:
    """
    Solve 0-1 knapsack using DFS Branch and Bound with LP-relaxation bounding.

    Returns (max_value, selected_items) where selected_items uses the
    caller's original item indices (not the internal sorted order).
    """
    n = len(weights)
    if n == 0 or capacity <= 0:
        return 0, []

    order = sorted(range(n), key=lambda i: values[i] / weights[i], reverse=True)
    w = [weights[i] for i in order]
    v = [values[i] for i in order]

    best_value = 0
    best_mask = [False] * n
    cur_mask = [False] * n

    def upper_bound(level: int, cur_weight: int, cur_value: int) -> float:
        bound = cur_value
        remaining = capacity - cur_weight
        for i in range(level, n):
            if w[i] <= remaining:
                bound += v[i]
                remaining -= w[i]
            else:
                bound += v[i] * remaining / w[i]
                break
        return bound

    def branch(level: int, cur_weight: int, cur_value: int) -> None:
        nonlocal best_value, best_mask

        if cur_value > best_value:
            best_value = cur_value
            best_mask = cur_mask.copy()

        if level == n:
            return

        if upper_bound(level, cur_weight, cur_value) <= best_value:
            return

        if cur_weight + w[level] <= capacity:
            cur_mask[level] = True
            branch(level + 1, cur_weight + w[level], cur_value + v[level])
            cur_mask[level] = False

        branch(level + 1, cur_weight, cur_value)

    branch(0, 0, 0)

    selected_original = sorted(order[i] for i in range(n) if best_mask[i])
    return best_value, selected_original


def solve_instance(filepath: str, verbose: bool = True) -> dict:
    """
    Solve a knapsack instance from file and return detailed results.
    """
    n_items, capacity, weights, values = read_knapsack_instance(filepath)

    if verbose:
        print(f"\n{'='*60}")
        print(f"Solving instance: {filepath}")
        print(f"{'='*60}")
        print(f"Number of items: {n_items}")
        print(f"Capacity: {capacity}")

    start_time = time.perf_counter()
    max_value, selected_items = knapsack_branch_bound(weights, values, capacity)
    elapsed_time = time.perf_counter() - start_time

    total_weight = sum(weights[i] for i in selected_items)
    n_selected = len(selected_items)

    if verbose:
        print(f"\n{'─'*60}")
        print(f"SOLUTION")
        print(f"{'─'*60}")
        print(f"Optimal value: {max_value}")
        print(f"Total weight: {total_weight}/{capacity}")
        print(f"Items selected: {n_selected}/{n_items}")
        print(f"Selected item indices: {selected_items}")
        print(f"\nItem details:")
        print(f"  {'Item':<6} {'Weight':<8} {'Value':<8}")
        print(f"  {'-'*6} {'-'*8} {'-'*8}")
        for idx in selected_items:
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
        'selected_items': selected_items,
        'time_seconds': elapsed_time,
        'weights': weights,
        'values': values,
    }


def main():
    import os

    instance_files = [
        'notebooks/plan_md_instance.txt',
        'notebooks/instance_n10.txt',
        'notebooks/instance_n15.txt',
        'notebooks/instance_n20.txt',
        'notebooks/instance_n22.txt',
        'notebooks/instance_n25.txt',
    ]

    results = []

    print("\n" + "=" * 60)
    print("0-1 KNAPSACK PROBLEM - BRANCH AND BOUND SOLVER (Python)")
    print("=" * 60)

    for instance_file in instance_files:
        if os.path.exists(instance_file):
            try:
                results.append(solve_instance(instance_file, verbose=True))
            except Exception as e:
                print(f"Error solving {instance_file}: {e}\n")
        else:
            print(f"File not found: {instance_file}\n")

    if results:
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"{'Instance':<25} {'n':<4} {'Opt Val':<8} {'Time (s)':<12}")
        print("-" * 60)
        for r in results:
            print(f"{os.path.basename(r['instance']):<25} {r['n_items']:<4} "
                  f"{r['optimal_value']:<8} {r['time_seconds']:<12.6f}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
