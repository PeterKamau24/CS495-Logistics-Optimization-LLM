"""CS495 Capstone — dispatcher entry point.

Subcommands:
  driver-region    Driver-to-region binary ILP via PuLP (production track)
  knapsack-pulp    0-1 knapsack via PuLP on PLAN-v1 + disaster relief instances
  knapsack-bb      0-1 knapsack via the hand-built Branch & Bound solver

Examples:
  python src/main.py driver-region
  python src/main.py knapsack-pulp
  python src/main.py knapsack-bb --input notebooks/instance_n20.txt
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Windows consoles default to cp1252, which chokes on the Unicode box-drawing
# characters used by the solver output. Force UTF-8 so output renders cleanly.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def cmd_driver_region(args: argparse.Namespace) -> None:
    from data_preprocessing import load_assignment_data
    from evaluation import evaluate_assignments
    from optimization_model import solve_driver_region_assignment

    csv_path = args.input or "data/sample_driver_region_data.csv"
    print(f"Loading: {csv_path}")
    df = load_assignment_data(csv_path)
    result = solve_driver_region_assignment(df, df)

    print("\nAssignments:")
    print(result.to_string(index=False) if not result.empty else "  (no feasible assignment)")
    print(f"\nMetrics: {evaluate_assignments(result)}")


def cmd_knapsack_pulp(args: argparse.Namespace) -> None:
    import knapsack_pulp

    knapsack_pulp.solve_knapsack(
        knapsack_pulp.small_items,
        knapsack_pulp.SMALL_CAPACITY,
        "PLAN.md Test Instance",
    )
    knapsack_pulp.solve_knapsack(
        knapsack_pulp.items,
        knapsack_pulp.CAPACITY,
        "Disaster Relief Helicopter Packing",
    )


def cmd_knapsack_bb(args: argparse.Namespace) -> None:
    from knapsack_branch_bound import solve_instance

    path = args.input or "data/knapsack_input.txt"
    solve_instance(path, verbose=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CS495 capstone dispatcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Examples:", 1)[1] if "Examples:" in __doc__ else "",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_dr = sub.add_parser("driver-region", help="driver-to-region ILP (PuLP)")
    p_dr.add_argument(
        "--input",
        help="CSV path (default: data/sample_driver_region_data.csv)",
    )
    p_dr.set_defaults(func=cmd_driver_region)

    p_kp = sub.add_parser("knapsack-pulp", help="0-1 knapsack via PuLP")
    p_kp.set_defaults(func=cmd_knapsack_pulp)

    p_kb = sub.add_parser(
        "knapsack-bb",
        help="0-1 knapsack via hand-built Branch & Bound",
    )
    p_kb.add_argument(
        "--input",
        help="instance file (default: data/knapsack_input.txt)",
    )
    p_kb.set_defaults(func=cmd_knapsack_bb)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
