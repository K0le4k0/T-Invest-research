import pandas as pd


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:

    high_low = df["high"] - df["low"]

    high_close = (df["high"] - df["close"].shift()).abs()

    low_close = (df["low"] - df["close"].shift()).abs()

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    df[f"atr_{period}"] = tr.rolling(period).mean()

    return df
