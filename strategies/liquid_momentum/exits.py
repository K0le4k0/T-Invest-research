def update_highest_price(
    row,
    position,
):

    if row.close > position["highest_price"]:

        position["highest_price"] = row.close

    return position


def atr_trailing_stop(
    row,
    position,
    config,
):

    return position["highest_price"] - (row.atr_14 * config["atr_multiplier"])


def ema_exit(row):
    return row.close < row.ema_200


def time_exit(
    row,
    position,
    max_bars=200,
):

    holding_time = row.Index - position["entry_time"]

    return holding_time.days > max_bars


def check_exit(
    row,
    position,
    config,
):

    atr_stop = atr_trailing_stop(
        row,
        position,
        config,
    )

    atr_exit = row.close < atr_stop

    ema_filter = ema_exit(row)

    timed_exit = time_exit(
        row,
        position,
    )

    return atr_exit or ema_filter or timed_exit
