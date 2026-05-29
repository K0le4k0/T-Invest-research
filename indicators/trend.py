import pandas as pd


def add_ema(df: pd.DataFrame, period: int) -> pd.DataFrame:

    df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()

    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:

    delta = df["close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    df[f"rsi_{period}"] = 100 - (100 / (1 + rs))

    return df
