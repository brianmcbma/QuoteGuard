
from quoteguard.metrics import (
    adverse_selection_rate,
    average_maker_markout,
)
from quoteguard.simulation import SimulationConfig, run_simulation


def analyse_simulation(
    config: SimulationConfig,
) -> dict[str, float | int]:
    result = run_simulation(config)

    equity = [row["equity"] for row in result.history]
    fills = [
        row for row in result.history
        if row["trade_direction"] != 0
    ]
    markouts = [row["maker_markout"] for row in fills]

    initial_equity = config.initial_cash
    total_pnl = result.final_equity - initial_equity

    peak = initial_equity
    max_drawdown_amount = 0.0
    max_drawdown_pct = 0.0

    for value in equity:
        peak = max(peak, value)
        drawdown = peak - value

        max_drawdown_amount = max(
            max_drawdown_amount, drawdown
        )

        if peak > 0:
            max_drawdown_pct = max(
                max_drawdown_pct, drawdown / peak
            )

    return {
        "starting_capital": initial_equity,
        "final_equity": result.final_equity,
        "total_pnl": total_pnl,
        "maximum_drawdown_amount": max_drawdown_amount,
        "maximum_drawdown_pct": max_drawdown_pct,
        "average_maker_markout": (
            average_maker_markout(markouts) if markouts else 0.0
        ),
        "adverse_selection_rate": (
            adverse_selection_rate(markouts) if markouts else 0.0
        ),
        "number_of_trades": len(fills),
    }


if __name__ == "__main__":
    results = analyse_simulation(SimulationConfig())

    print("\nQuoteGuard Simulation Report")
    print("-" * 32)

    for metric, value in results.items():
        if isinstance(value, float):
            print(f"{metric}: {value:.6f}")
        else:
            print(f"{metric}: {value}")
