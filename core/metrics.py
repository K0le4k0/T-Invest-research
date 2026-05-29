import numpy as np


def calculate_metrics(
    equity_df,
    trades_df,
):

    equity = equity_df["equity"]

    returns = equity.pct_change().dropna()

    # =========================
    # TOTAL RETURN
    # =========================

    total_return = equity.iloc[-1] / equity.iloc[0] - 1

    # =========================
    # CAGR
    # =========================

    years = (equity_df["time"].iloc[-1] - equity_df["time"].iloc[0]).days / 365

    cagr = ((equity.iloc[-1] / equity.iloc[0]) ** (1 / years)) - 1

    # =========================
    # SHARPE
    # =========================

    sharpe = (returns.mean() / returns.std()) * np.sqrt(252)

    # =========================
    # VOLATILITY
    # =========================

    volatility = returns.std() * np.sqrt(252)

    # =========================
    # DRAWDOWN
    # =========================

    rolling_max = equity.cummax()

    drawdown = (equity - rolling_max) / rolling_max

    max_drawdown = drawdown.min()

    # =========================
    # TRADES
    # =========================

    if len(trades_df) > 0:

        winrate = (trades_df["pnl"] > 0).mean()

        avg_trade = trades_df["pnl"].mean()

        profit_factor = trades_df[trades_df["pnl"] > 0]["pnl"].sum() / abs(
            trades_df[trades_df["pnl"] < 0]["pnl"].sum()
        )

    else:

        winrate = 0
        avg_trade = 0
        profit_factor = 0

    return {
        "Total Return": total_return,
        "CAGR": cagr,
        "Sharpe": sharpe,
        "Volatility": volatility,
        "Max Drawdown": max_drawdown,
        "Winrate": winrate,
        "Average Trade": avg_trade,
        "Profit Factor": profit_factor,
    }
