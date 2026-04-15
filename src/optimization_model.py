import pandas as pd
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpBinary, value


def solve_driver_region_assignment(drivers_df: pd.DataFrame, assignments_df: pd.DataFrame):
    """
    Solve a driver-to-region assignment problem.

    drivers_df columns:
        driver_id

    assignments_df columns:
        driver_id, region_id, cost, eligible
    """

    valid_rows = assignments_df[assignments_df["eligible"] == 1].copy()

    drivers = valid_rows["driver_id"].unique().tolist()
    regions = valid_rows["region_id"].unique().tolist()
    pairs = [(row.driver_id, row.region_id) for row in valid_rows.itertuples()]

    cost_dict = {(row.driver_id, row.region_id): row.cost for row in valid_rows.itertuples()}

    model = LpProblem("Driver_Region_Assignment", LpMinimize)

    x = LpVariable.dicts("assign", pairs, cat=LpBinary)

    model += lpSum(cost_dict[i, j] * x[i, j] for i, j in pairs)

    for driver in drivers:
        model += lpSum(x[i, j] for i, j in pairs if i == driver) <= 1

    for region in regions:
        model += lpSum(x[i, j] for i, j in pairs if j == region) >= 1

    model.solve()

    results = []
    for i, j in pairs:
        if value(x[i, j]) == 1:
            results.append({"driver_id": i, "region_id": j, "selected": 1})

    return pd.DataFrame(results)
