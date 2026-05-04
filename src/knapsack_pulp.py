"""
0-1 Knapsack Problem — PuLP Implementation
==========================================
Real-world scenario: Emergency Supply Packing for Disaster Relief
-----------------------------------------------------------------
A relief organization must pack the most valuable set of supplies
into a helicopter with a 50 kg weight limit.
Each supply item has a weight (kg) and an impact score (value).
The goal: maximize total impact while staying within the weight limit.

This mirrors the PLAN.md Hexaly model structure:
  - Boolean decision variables (x_i in {0,1})
  - One capacity constraint (sum of weights <= W)
  - One maximization objective (sum of values)
"""

import pulp

# ── Real-world instance ──────────────────────────────────────────────────────
# Disaster relief helicopter packing problem
items = [
    # (name,                    weight_kg,  impact_score)
    ("Water Purification Kit",      8,          85),
    ("Medical First Aid Pack",      5,          95),
    ("Emergency Food Rations",     12,          70),
    ("Portable Generator",         20,          60),
    ("Blankets (10x)",              6,          50),
    ("Communication Radio",         3,          90),
    ("Shelter Tarp",                4,          65),
    ("Flashlights & Batteries",     2,          40),
    ("Baby Supplies Kit",           5,          88),
    ("Solar Charging Panel",        7,          55),
]

CAPACITY = 50  # helicopter weight limit in kg

# ── PLAN.md small test instance (for verification) ───────────────────────────
# weights=[4,3,2], values=[8,5,6], capacity=5 → expected value=11
small_items = [
    ("Item_1", 4, 8),
    ("Item_2", 3, 5),
    ("Item_3", 2, 6),
]
SMALL_CAPACITY = 5

def solve_knapsack(items, capacity, title="Knapsack"):
    """
    Solve a 0-1 Knapsack problem using PuLP (COIN-BC solver).
    Mirrors the Hexaly model from PLAN.md exactly:
      - Boolean vars  →  pulp.LpBinary
      - Weight constraint  →  lpSum(w_i * x_i) <= W
      - Objective  →  maximize lpSum(v_i * x_i)
    """
    names   = [item[0] for item in items]
    weights = [item[1] for item in items]
    values  = [item[2] for item in items]
    n = len(items)

    # Create the model
    model = pulp.LpProblem(name=title.replace(" ", "_"), sense=pulp.LpMaximize)

    # Decision variables: x_i ∈ {0, 1}
    x = [pulp.LpVariable(name=f"x_{i}", cat=pulp.const.LpBinary) for i in range(n)]

    # Objective: maximize total value
    model += pulp.lpSum(values[i] * x[i] for i in range(n)), "Total_Value"

    # Constraint: total weight <= capacity
    model += pulp.lpSum(weights[i] * x[i] for i in range(n)) <= capacity, "Weight_Limit"

    # Solve (suppress solver output)
    solver = pulp.PULP_CBC_CMD(msg=0)
    status = model.solve(solver)

    # ── Results ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"  Solver Status : {pulp.LpStatus[status]}")
    print(f"  Capacity      : {capacity} kg")
    print(f"  Items         : {n}\n")

    selected = []
    total_weight = 0
    total_value  = 0

    for i in range(n):
        if pulp.value(x[i]) == 1:
            selected.append(names[i])
            total_weight += weights[i]
            total_value  += values[i]
            print(f"  ✓  {names[i]:<30}  weight={weights[i]:>3} kg   value={values[i]:>3}")

    not_selected = [names[i] for i in range(n) if pulp.value(x[i]) != 1]
    for name in not_selected:
        idx = names.index(name)
        print(f"  ✗  {name:<30}  weight={weights[idx]:>3} kg   value={values[idx]:>3}")

    print(f"\n  {'─'*50}")
    print(f"  Items selected   : {len(selected)} / {n}")
    print(f"  Total weight     : {total_weight} kg  (limit: {capacity} kg)")
    print(f"  Total value      : {total_value}")
    print(f"{'='*60}\n")

    return selected, total_weight, total_value


if __name__ == "__main__":
    print("\n" + "─"*60)
    print("  0-1 Knapsack Solver  |  PuLP + COIN-BC")
    print("  Equivalent Hexaly model from PLAN.md")
    print("─"*60)

    # 1. Verify PLAN.md small instance first
    print("\n[TEST] Verifying PLAN.md instance (expected value = 11)...")
    sel, tw, tv = solve_knapsack(small_items, SMALL_CAPACITY, "PLAN.md Test Instance")
    assert tv == 11, f"Expected 11, got {tv}"
    print(f"  PLAN.md instance verified: value={tv}, weight={tw}\n")

    # 2. Real-world disaster relief instance
    solve_knapsack(items, CAPACITY, "Disaster Relief Helicopter Packing")
