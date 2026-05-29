def apply_filters(df):

    df["ema_200_slope"] = df["ema_200"] > df["ema_200"].shift(10)

    df["atr_mean"] = df["atr_14"].rolling(50).mean()

    df["high_volatility"] = df["atr_14"] > df["atr_mean"]

    df["trend_strength"] = (df["ema_50"] - df["ema_200"]) / df["ema_200"]

    df["strong_trend"] = df["trend_strength"] > 0.03

    return df
