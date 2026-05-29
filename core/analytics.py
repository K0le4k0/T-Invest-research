import pandas as pd


def print_analytics(
    trades_df,
    equity_df,
):

    print()
    print("========== ANALYTICS ==========")

    # =========================
    # YEARLY RETURNS
    # =========================

    equity_df["year"] = pd.to_datetime(equity_df["time"]).dt.year

    yearly = equity_df.groupby("year")["equity"].last().pct_change()

    print()
    print("YEARLY RETURNS")

    for year, value in yearly.items():

        if pd.isna(value):
            continue

        print(f"{year}: " f"{round(value * 100, 2)}%")

    # =========================
    # BEST TRADES
    # =========================

    if len(trades_df) == 0:
        return

    best_trades = trades_df.sort_values("pnl", ascending=False).head(5)

    print()
    print("BEST TRADES")

    for _, trade in best_trades.iterrows():

        print(f"{trade['ticker']} | " f"{round(trade['pnl'], 2)}")

    # =========================
    # WORST TRADES
    # =========================

    worst_trades = trades_df.sort_values("pnl", ascending=True).head(5)

    print()
    print("WORST TRADES")

    for _, trade in worst_trades.iterrows():

        print(f"{trade['ticker']} | " f"{round(trade['pnl'], 2)}")

    # =========================
    # TOP TICKERS
    # =========================

    ticker_stats = trades_df.groupby("ticker")["pnl"].sum()

    top_tickers = ticker_stats.sort_values(ascending=False).head(10)

    print()
    print("TOP TICKERS")

    for ticker, pnl in top_tickers.items():

        print(f"{ticker}: " f"{round(pnl, 2)}")

    # =========================
    # WORST TICKERS
    # =========================

    worst_tickers = ticker_stats.sort_values(ascending=True).head(10)

    print()
    print("WORST TICKERS")

    for ticker, pnl in worst_tickers.items():

        print(f"{ticker}: " f"{round(pnl, 2)}")
