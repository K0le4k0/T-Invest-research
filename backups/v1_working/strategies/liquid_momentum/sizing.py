def calculate_position_size(
    capital,
    atr,
    close_price,
    risk_per_trade=0.01,
):

    if atr <= 0:

        return 0

    risk_amount = capital * risk_per_trade

    stop_distance = atr * 3

    shares = risk_amount / stop_distance

    position_size = shares * close_price

    return position_size


def apply_exposure_limit(
    position_size,
    capital,
    max_exposure=0.2,
):

    max_size = capital * max_exposure

    return min(
        position_size,
        max_size,
    )
