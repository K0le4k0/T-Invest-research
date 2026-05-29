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

    print("IMOEX")
    print(market_df.index[:5])

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

        print(ticker, df["market_trend"].isna().sum())

        df["ticker"] = ticker

        all_signals.append(df)

        print(ticker)
        print(df.index[:5])

    signals_df = pd.concat(all_signals)

    print()
    print(signals_df.head())

    print(signals_df.columns.tolist())

    # =====================
    # RANKING
    # =====================

    signals_df = (
        signals_df.sort_values(["time", "momentum_score"], ascending=[True, False])
        .groupby("time")
        .head(config["top_n"])
    )

    # =====================
    # PORTFOLIO
    # =====================

    print(signals_df[["ticker", "momentum_score"]].head(50))

    capital = config["initial_capital"]

    open_positions = []

    closed_trades = []

    equity_curve = []

    equity_peak = capital

    # =====================
    # MAIN LOOP
    # =====================

    for row in signals_df.itertuples():

        current_time = row.Index

        # =====================
        # UPDATE HIGHS
        # =====================

        for position in open_positions:

            if row.ticker == position["ticker"]:

                position = update_highest_price(
                    row,
                    position,
                )

        # =====================
        # EQUITY
        # =====================

        current_equity = calculate_equity(
            capital,
            open_positions,
            row,
        )

        # =====================
        # EQUITY PEAK
        # =====================

        equity_peak = update_equity_peak(
            current_equity,
            equity_peak,
        )

        # =====================
        # DRAWDOWN
        # =====================

        drawdown = calculate_drawdown(
            current_equity,
            equity_peak,
        )

        # =====================
        # EXPOSURE
        # =====================

        dynamic_max_positions = get_dynamic_max_positions(
            drawdown,
            config["max_positions"],
        )

        # =====================
        # EXITS
        # =====================

        positions_to_close = []

        for position in open_positions:

            if row.ticker != position["ticker"]:

                continue

            if check_exit(
                row,
                position,
            ):

                exit_price = row.close

                capital, pnl = close_position(
                    position,
                    exit_price,
                    capital,
                )

                closed_trades.append(
                    {
                        "ticker": position["ticker"],
                        "entry_time": position["entry_time"],
                        "exit_time": current_time,
                        "pnl": pnl,
                    }
                )

                positions_to_close.append(position)

        for position in positions_to_close:

            open_positions.remove(position)

        # =====================
        # ENTRIES
        # =====================

        already_open = any(p["ticker"] == row.ticker for p in open_positions)

        if (
            len(open_positions) < dynamic_max_positions
            and not already_open
            and row.trend_signal
            and row.market_trend
        ):

            position_size = calculate_position_size(
                capital,
                row.atr_14,
                row.close,
            )

            position_size = apply_exposure_limit(
                position_size,
                capital,
            )

            capital = open_position(
                open_positions,
                capital,
                row.ticker,
                current_time,
                row.close,
                position_size,
            )

        # =====================
        # EQUITY CURVE
        # =====================

        equity_curve.append(
            {
                "time": current_time,
                "equity": current_equity,
                "open_positions": len(open_positions),
            }
        )

    equity_df = pd.DataFrame(equity_curve)

    trades_df = pd.DataFrame(closed_trades)

    return equity_df, trades_df
