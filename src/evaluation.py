import pandas as pd


def evaluate_assignments(result_df: pd.DataFrame) -> dict:
    return {
        "total_assignments": len(result_df),
        "covered_regions": result_df["region_id"].nunique() if not result_df.empty else 0,
        "assigned_drivers": result_df["driver_id"].nunique() if not result_df.empty else 0,
    }
