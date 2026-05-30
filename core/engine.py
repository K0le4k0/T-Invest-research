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

    market_df = signals_df.copy()

    # =====================
    # RANKING
    # =====================

    signals_df = (
        signals_df.sort_values(["time", "momentum_score"], ascending=[True, False])
        .groupby("time")
        .head(config["top_n"])
    )

    market_lookup = {(row.Index, row.ticker): row for row in market_df.itertuples()}

    all_times = sorted(market_df.index.unique())

    latest_time = signals_df.index.max()

    latest_rows = signals_df.loc[[latest_time]]

    # =====================
    # PORTFOLIO
    # =====================

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

    for current_time in all_times:

        current_rows = signals_df.loc[signals_df.index == current_time]

        if len(current_rows.shape) == 1:
            current_rows = current_rows.to_frame().T

        # =====================
        # UPDATE PRICES
        # =====================

        for position in open_positions:

            market_row = market_lookup.get((current_time, position["ticker"]))

            if market_row is None:
                continue

            latest_prices[position["ticker"]] = market_row.close

            update_highest_price(
                market_row,
                position,
            )

        # =====================
        # EXITS
        # =====================

        positions_to_close = []

        for position in open_positions:

            market_row = market_lookup.get((current_time, position["ticker"]))

            if market_row is None:
                continue

            if check_exit(
                market_row,
                position,
            ):

                exit_price = market_row.close

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
        # EQUITY
        # =====================

        current_equity = calculate_equity(
            capital,
            open_positions,
            latest_prices,
        )

        equity_peak = update_equity_peak(
            current_equity,
            equity_peak,
        )

        drawdown = calculate_drawdown(
            current_equity,
            equity_peak,
        )

        dynamic_max_positions = get_dynamic_max_positions(
            drawdown,
            config["max_positions"],
        )

        # =====================
        # ENTRIES
        # =====================

        for row in current_rows.itertuples():

            already_open = any(p["ticker"] == row.ticker for p in open_positions)

            if row.trend_signal and row.market_trend:
                signals_count += 1

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

                entries_count += 1

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

    print()
    print("SIGNALS:", signals_count)
    print("ENTRIES:", entries_count)

    return equity_df, trades_df
