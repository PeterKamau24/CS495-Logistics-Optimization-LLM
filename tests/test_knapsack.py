"""Tests for the knapsack solvers.

Verifies the PuLP, Branch & Bound, and brute-force implementations against
the two known-answer instances documented in PLAN.md plus cross-solver
agreement on random instances:

  - PLAN-v1 instance: weights=[4,3,2], values=[8,5,6], capacity=5 → value=11
  - Disaster relief: 10 items, capacity=50 → value=598
  - 50 random instances (n=1..12): B&B must agree with brute force AND
    every reported solution must satisfy the knapsack invariants.
"""

import io
import random
from contextlib import redirect_stdout

import pytest

from knapsack_branch_bound import knapsack_branch_bound, read_knapsack_instance
from knapsack_brute_force import knapsack_brute_force
from knapsack_pulp import (
    CAPACITY,
    SMALL_CAPACITY,
    items,
    small_items,
    solve_knapsack,
)


def _assert_valid_solution(selected, weights, values, capacity, reported_value):
    """Knapsack feasibility + accounting invariants any solver must satisfy."""
    assert len(set(selected)) == len(selected), "duplicate indices in solution"
    assert all(0 <= i < len(weights) for i in selected), "out-of-range index"
    assert sum(weights[i] for i in selected) <= capacity, "infeasible weight"
    assert sum(values[i] for i in selected) == reported_value, \
        "reported value does not match selected items"


def test_pulp_plan_v1_instance():
    _, _, total_value = solve_knapsack(small_items, SMALL_CAPACITY, "test_small")
    assert total_value == 11


def test_pulp_disaster_relief_instance():
    _, _, total_value = solve_knapsack(items, CAPACITY, "test_relief")
    assert total_value == 598


def test_bb_matches_pulp_on_plan_v1():
    bb_value, _ = knapsack_branch_bound([4, 3, 2], [8, 5, 6], 5)
    assert bb_value == 11


def test_bb_matches_pulp_on_disaster_relief():
    weights = [item[1] for item in items]
    values = [item[2] for item in items]
    bb_value, _ = knapsack_branch_bound(weights, values, CAPACITY)
    assert bb_value == 598


def test_reader_accepts_three_line_format(tmp_path):
    f = tmp_path / "three_line.txt"
    f.write_text("3 5\n4 3 2\n8 5 6\n")
    n, capacity, weights, values = read_knapsack_instance(str(f))
    assert (n, capacity, weights, values) == (3, 5, [4, 3, 2], [8, 5, 6])


def test_reader_accepts_four_line_format(tmp_path):
    f = tmp_path / "four_line.txt"
    f.write_text("3\n4 3 2\n8 5 6\n5\n")
    n, capacity, weights, values = read_knapsack_instance(str(f))
    assert (n, capacity, weights, values) == (3, 5, [4, 3, 2], [8, 5, 6])


def test_reader_rejects_malformed(tmp_path):
    f = tmp_path / "bad.txt"
    f.write_text("only one line\n")
    with pytest.raises(ValueError):
        read_knapsack_instance(str(f))


def test_all_solvers_agree_on_canonical_instance():
    """PuLP, B&B, and brute force must all return value=11 on PLAN-v1."""
    weights = [4, 3, 2]
    values = [8, 5, 6]
    capacity = 5

    bb_value, bb_selected = knapsack_branch_bound(weights, values, capacity)
    bf_value, bf_selected = knapsack_brute_force(weights, values, capacity)
    with redirect_stdout(io.StringIO()):
        _, _, pulp_value = solve_knapsack(small_items, SMALL_CAPACITY, "agreement")

    assert bb_value == bf_value == pulp_value == 11
    _assert_valid_solution(bb_selected, weights, values, capacity, bb_value)
    _assert_valid_solution(bf_selected, weights, values, capacity, bf_value)


def test_bb_matches_brute_force_on_random_instances():
    """B&B must agree with brute force on 50 random instances (n=1..12).

    Brute force is the oracle — it is correct by exhaustive enumeration, so
    any divergence is a B&B bug. Also checks both solutions are feasible and
    that the reported value matches the selected items.
    """
    rng = random.Random(42)
    for trial in range(50):
        n = rng.randint(1, 12)
        weights = [rng.randint(1, 20) for _ in range(n)]
        vals = [rng.randint(1, 100) for _ in range(n)]
        capacity = rng.randint(1, sum(weights))

        bb_value, bb_selected = knapsack_branch_bound(weights, vals, capacity)
        bf_value, bf_selected = knapsack_brute_force(weights, vals, capacity)

        assert bb_value == bf_value, (
            f"trial {trial}: B&B={bb_value} BF={bf_value} "
            f"w={weights} v={vals} C={capacity}"
        )
        _assert_valid_solution(bb_selected, weights, vals, capacity, bb_value)
        _assert_valid_solution(bf_selected, weights, vals, capacity, bf_value)
