from math import sqrt
from statistics import mean, stdev


def total_pnl(equity_history: list[float]) -> float:
    if len(equity_history) < 1:
        raise ValueError("Equity history cannot be empty.")

    return equity_history[-1] - equity_history[0]


def maximum_drawdown(equity_history: list[float]) -> float:
    if not equity_history:
        raise ValueError("Equity history cannot be empty.")

    peak = equity_history[0]
    max_drawdown = 0.0

    for equity in equity_history:
        peak = max(peak, equity)
        if peak > 0:
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)

    return max_drawdown


def sharpe_ratio(
    returns: list[float],
    periods_per_year: int = 252,
) -> float:
    if len(returns) < 2:
        raise ValueError("At least two returns are required.")
    if periods_per_year <= 0:
        raise ValueError("Periods per year must be positive.")

    volatility = stdev(returns)
    if volatility == 0:
        return 0.0

    return sqrt(periods_per_year) * mean(returns) / volatility

def average_maker_markout(markouts: list[float]) -> float:
    """Return the average markout across executed trades."""
    if not markouts:
        raise ValueError("Markouts cannot be empty.")

    return mean(markouts)


def adverse_selection_rate(markouts: list[float]) -> float:
    """Return the fraction of executed trades with negative markouts."""
    if not markouts:
        raise ValueError("Markouts cannot be empty.")

    return sum(markout < 0 for markout in markouts) / len(markouts)

