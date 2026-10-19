
from statistics import mean, stdev
from math import sqrt

from quoteguard.analysis import analyse_simulation
from quoteguard.simulation import SimulationConfig


def compare_flow_strengths() -> None:
    flow_strengths = [0.0, 0.25, 0.5, 0.75, 1.0]
    seeds = list(range(30))
    results_by_flow = {}

    for flow in flow_strengths:
        results_by_flow[flow] = []

        for seed in seeds:
            config = SimulationConfig(
                initial_cash=10_000.0,
                flow_strength=flow,
                steps=1_000,
                seed=seed,
            )
            results_by_flow[flow].append(
                analyse_simulation(config)
            )

    baseline_pnls = [
        result["total_pnl"]
        for result in results_by_flow[0.0]
    ]

    print("\nQuoteGuard: Paired Order Flow Experiment")
    print("=" * 112)
    print(
        f"{'Flow':>6} {'Mean P&L':>11} {'Delta vs 0':>12} "
        f"{'95% CI for delta':>25} {'Mean DD':>10} "
        f"{'Avg Markout':>13} {'Adverse Rate':>13}"
    )
    print("-" * 112)

    for flow in flow_strengths:
        results = results_by_flow[flow]
        pnls = [r["total_pnl"] for r in results]

        deltas = [
            pnl - baseline
            for pnl, baseline in zip(pnls, baseline_pnls)
        ]

        delta_mean = mean(deltas)

        if len(deltas) > 1:
            margin = 1.96 * stdev(deltas) / sqrt(len(deltas))
        else:
            margin = 0.0

        ci_low = delta_mean - margin
        ci_high = delta_mean + margin

        mean_dd = mean(
            r["maximum_drawdown_amount"] for r in results
        )
        mean_markout = mean(
            r["average_maker_markout"] for r in results
        )
        mean_adverse = mean(
            r["adverse_selection_rate"] for r in results
        )

        print(
            f"{flow:>6.2f} "
            f"{mean(pnls):>11.3f} "
            f"{delta_mean:>12.3f} "
            f"[{ci_low:>9.3f}, {ci_high:>9.3f}] "
            f"{mean_dd:>10.3f} "
            f"{mean_markout:>13.5f} "
            f"{mean_adverse:>12.2%}"
        )


if __name__ == "__main__":
    compare_flow_strengths()
