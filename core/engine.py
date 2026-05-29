import pandas as pd

from indicators.trend import add_ema
from indicators.volatility import add_atr

from strategies.liquid_momentum.filters import (
    apply_filters,
)

from strategies.liquid_momentum.signals import (
    build_signals,
)

from strategies.liquid_momentum.exits import (
    check_exit,
    update_highest_price,
)

from strategies.liquid_momentum.sizing import (
    calculate_position_size,
    apply_exposure_limit,
)

from core.portfolio import (
    calculate_equity,
    update_equity_peak,
    calculate_drawdown,
    get_dynamic_max_positions,
    open_position,
    close_position,
)


def run_backtest(
    dataframes,
    config,
):

    all_signals = []

    market_df = dataframes["IMOEX"]

    market_df = add_ema(
        market_df,
        config["ema_trend"],
    )

    market_df["market_trend"] = market_df["close"] > market_df["ema_200"]

    # =====================
    # PREPARE DATA
    # =====================

    for ticker, df in dataframes.items():

        if ticker == "IMOEX":

            continue

        df = add_ema(
            df,
            config["ema_fast"],
        )

        df = add_ema(
            df,
            config["ema_slow"],
        )

        df = add_ema(
            df,
            config["ema_trend"],
        )

        df = add_atr(
            df,
            config["atr_period"],
        )

        df = apply_filters(df)

        df = build_signals(df)

        df["market_trend"] = market_df["market_trend"].reindex(df.index).ffill()

        df["ticker"] = ticker

        all_signals.append(df)

    signals_df = pd.concat(all_signals)

    # =====================
    # RANKING
    # =====================

    signals_df = (
        signals_df.sort_values(["time", "momentum_score"], ascending=[True, False])
        .groupby("time")
        .head(config["top_n"])
    )

    latest_time = signals_df.index.max()

    latest_rows = signals_df.loc[[latest_time]]

    # =====================
    # PORTFOLIO
    # =====================

    market_df = pd.concat(all_signals)

    market_lookup = {(idx, row.ticker): row for idx, row in market_df.iterrows()}

    all_times = sorted(market_df.index.unique())

    capital = config["initial_capital"]

    latest_prices = {}

    open_positions = []

    closed_trades = []

    equity_curve = []

    equity_peak = capital

    signals_count = 0
    entries_count = 0

    # =====================
    # MAIN LOOP
    # =====================

    equity_df = pd.DataFrame(equity_curve)

    trades_df = pd.DataFrame(closed_trades)

    print()
    print("SIGNALS:", signals_count)
    print("ENTRIES:", entries_count)

    return equity_df, trades_df
