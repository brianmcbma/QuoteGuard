
from statistics import mean, stdev
from math import sqrt

from quoteguard.analysis import analyse_simulation
from quoteguard.simulation import SimulationConfig


def run_experiments() -> None:
    skew_values = [0.00, 0.01, 0.03]
    flow_values = [0.50, 1.00]
    seeds = range(30)

    print("\nQuoteGuard: Inventory Skew Experiment")
    print("=" * 100)
    print(
        f"{'Flow':>6} {'Skew':>7} {'Mean P&L':>12} "
        f"{'P&L SD':>11} {'Mean DD':>11} "
        f"{'Avg Markout':>13} {'Adverse Rate':>13} {'Trades':>9}"
    )
    print("-" * 100)

    for flow in flow_values:
        for skew in skew_values:
            results = []

            for seed in seeds:
                config = SimulationConfig(
                    initial_cash=10_000.0,
                    flow_strength=flow,
                    inventory_skew=skew,
                    steps=1_000,
                    seed=seed,
                )
                results.append(analyse_simulation(config))

            pnls = [r["total_pnl"] for r in results]

            print(
                f"{flow:>6.2f} "
                f"{skew:>7.3f} "
                f"{mean(pnls):>12.3f} "
                f"{stdev(pnls):>11.3f} "
                f"{mean(r['maximum_drawdown_amount'] for r in results):>11.3f} "
                f"{mean(r['average_maker_markout'] for r in results):>13.5f} "
                f"{mean(r['adverse_selection_rate'] for r in results):>12.2%} "
                f"{mean(r['number_of_trades'] for r in results):>9.1f}"
            )


if __name__ == "__main__":
    run_experiments()
