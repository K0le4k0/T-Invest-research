from pathlib import Path

import pandas as pd

DATA_DIR = Path("market_data")


def load_data(ticker: str) -> pd.DataFrame:

    file_path = DATA_DIR / ticker / "candles_1m.parquet"

    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    df = pd.read_parquet(file_path)

    df["time"] = pd.to_datetime(df["time"])

    df = df.sort_values("time")

    df = df.set_index("time")

    return df
