def calculate_equity(
    capital,
    open_positions,
    latest_prices,
):

    current_equity = capital

    for position in open_positions:

        ticker = position["ticker"]

        if ticker not in latest_prices:
            continue

        current_price = latest_prices[ticker]

        current_equity += position["size"] * current_price / position["entry_price"]

    return current_equity


def update_equity_peak(
    current_equity,
    equity_peak,
):

    if current_equity > equity_peak:

        return current_equity

    return equity_peak


def calculate_drawdown(
    current_equity,
    equity_peak,
):

    return (current_equity - equity_peak) / equity_peak


def get_dynamic_max_positions(
    drawdown,
    default_positions,
):
    return default_positions


def open_position(
    open_positions,
    capital,
    ticker,
    current_time,
    entry_price,
    position_size,
):

    capital -= position_size

    open_positions.append(
        {
            "ticker": ticker,
            "entry_time": current_time,
            "entry_price": entry_price,
            "size": position_size,
            "highest_price": entry_price,
        }
    )

    return capital


def close_position(
    position,
    exit_price,
    capital,
):

    pnl = ((exit_price / position["entry_price"]) - 1) * position["size"]

    capital += position["size"] + pnl

    return capital, pnl
