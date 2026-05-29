import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT_DIR))

import matplotlib.pyplot as plt

from universes.universes import (
    TOP_LIQUID,
)

from data.loader import (
    load_data,
)

from data.timeframes import (
    resample_timeframe,
)

from core.engine import (
    run_backtest,
)

from core.metrics import (
    calculate_metrics,
)

from core.analytics import (
    print_analytics,
)

from strategies.liquid_momentum.config import (
    CONFIG,
)

# =========================
# LOAD DATA
# =========================


def run_strategy(config):

    START_DATE = "2021-03-01"

    dataframes = {}

    df = load_data("IMOEX")

    df = resample_timeframe(
        df,
        "1h",
    )

    df = df.loc[START_DATE:]

    dataframes["IMOEX"] = df

    for ticker in TOP_LIQUID:

        try:

            df = load_data(ticker)

            df = resample_timeframe(
                df,
                "1h",
            )

            df = df.loc[START_DATE:]

            dataframes[ticker] = df

        except Exception as e:

            print(f"Ошибка {ticker}: {e}")

    equity_df, trades_df = run_backtest(
        dataframes,
        config,
    )

    print(type(equity_df))
    print(equity_df.shape)
    print(equity_df.columns)
    print(equity_df.head())

    metrics = calculate_metrics(
        equity_df,
        trades_df,
    )

    return (
        metrics,
        equity_df,
        trades_df,
    )


if __name__ == "__main__":

    metrics, equity_df, trades_df = run_strategy(CONFIG)

    print()
    print("========== RESULT ==========")

    for key, value in metrics.items():

        print(f"{key}: {round(value, 4)}")

    print_analytics(
        trades_df,
        equity_df,
    )

    plt.figure(figsize=(14, 7))

    plt.plot(
        equity_df["time"],
        equity_df["equity"],
        label="TOP_LIQUID",
    )

    plt.title("Liquid Momentum")

    plt.legend()

    plt.grid()

    plt.show()
