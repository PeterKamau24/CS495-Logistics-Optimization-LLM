"""Tests for the knapsack solvers.

Verifies both the PuLP and Branch & Bound implementations against the two
known-answer instances documented in PLAN.md:

  - PLAN-v1 instance: weights=[4,3,2], values=[8,5,6], capacity=5 → value=11
  - Disaster relief: 10 items, capacity=50 → value=598
"""

import pytest

from knapsack_branch_bound import knapsack_branch_bound, read_knapsack_instance
from knapsack_pulp import (
    CAPACITY,
    SMALL_CAPACITY,
    items,
    small_items,
    solve_knapsack,
)


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
