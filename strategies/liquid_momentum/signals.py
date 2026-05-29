def add_momentum_score(df):

    df["ret_20"] = df["close"] / df["close"].shift(20) - 1

    df["ret_60"] = df["close"] / df["close"].shift(60) - 1

    df["ret_120"] = df["close"] / df["close"].shift(120) - 1

    df["ret_180"] = df["close"] / df["close"].shift(180) - 1

    df["relative_strength"] = df["close"] / df["close"].shift(20)

    df["momentum_score"] = (
        df["ret_20"] * 0.4
        + df["ret_60"] * 0.3
        + df["ret_120"] * 0.2
        + df["ret_180"] * 0.1
    )

    df["volatility_penalty"] = df["atr_mean"] / df["close"]

    df["momentum_score"] = df["momentum_score"] / (1 + df["volatility_penalty"])

    return df


def add_breakout_signal(df):

    df["rolling_high"] = df["high"].rolling(50).max()

    df["breakout_signal"] = df["close"] >= df["rolling_high"]

    return df


def add_trend_signal(df):

    df["trend_signal"] = (
        (df["ema_50"] > df["ema_200"])
        & (df["close"] > df["ema_20"])
        & (df["ema_200_slope"])
        & (df["high_volatility"])
        & (df["strong_trend"])
        & (df["momentum_score"] > 0)
    )

    return df


def build_signals(df):

    df = add_momentum_score(df)

    df = add_breakout_signal(df)

    df = add_trend_signal(df)

    return df
