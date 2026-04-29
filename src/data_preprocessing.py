import pandas as pd


def load_assignment_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    required_cols = ["driver_id", "region_id", "cost", "eligible"]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df
