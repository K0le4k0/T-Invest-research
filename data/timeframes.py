import pandas as pd


def resample_timeframe(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:

    result = df.resample(timeframe).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )

    result = result.dropna()

    return result
