
from statistics import mean
from html import escape

from quoteguard.simulation import SimulationConfig, run_simulation


SKEW_VALUES = [
    0.000, 0.005, 0.010, 0.015, 0.020, 0.025, 0.030
]
FLOW_VALUES = [0.50, 1.00]
SEEDS = list(range(30))


def analyse_run(config):
    result = run_simulation(config)

    equity = [config.initial_cash] + [
        row["equity"] for row in result.history
    ]
    inventory = [
        abs(row["inventory"]) for row in result.history
    ]

    peak = equity[0]
    max_drawdown = 0.0

    for value in equity[1:]:
        peak = max(peak, value)
        max_drawdown = max(max_drawdown, peak - value)

    return {
        "pnl": result.final_equity - config.initial_cash,
        "drawdown": max_drawdown,
        "avg_abs_inventory": mean(inventory),
    }


def svg_chart(points, filename="risk_return.svg"):
    """Create a risk-return scatter plot without external packages."""
    width, height = 900, 600
    left, right, top, bottom = 95, 40, 65, 90
    plot_width = width - left - right
    plot_height = height - top - bottom

    x_max = max(p["drawdown"] for p in points) * 1.12
    y_min = min(0.0, min(p["pnl"] for p in points) - 2)
    y_max = max(p["pnl"] for p in points) + 2

    def x_pos(value):
        return left + value / x_max * plot_width

    def y_pos(value):
        return top + (y_max - value) / (y_max - y_min) * plot_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#222}'
        '.grid{stroke:#ddd;stroke-width:1}'
        '.axis{stroke:#333;stroke-width:1.5}</style>',
        '<text x="450" y="30" text-anchor="middle" '
        'font-size="21" font-weight="bold">'
        'QuoteGuard: Risk–Return Trade-off</text>',
    ]

    # Horizontal gridlines and P&L labels.
    for i in range(6):
        value = y_min + (y_max - y_min) * i / 5
        y = y_pos(value)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" '
            f'x2="{width-right}" y2="{y:.1f}" class="grid"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{y+5:.1f}" '
            f'text-anchor="end" font-size="12">'
            f'{value:.1f}</text>'
        )

    # Vertical gridlines and drawdown labels.
    for i in range(6):
        value = x_max * i / 5
        x = x_pos(value)
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" '
            f'x2="{x:.1f}" y2="{height-bottom}" class="grid"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{height-bottom+23}" '
            f'text-anchor="middle" font-size="12">'
            f'{value:.1f}</text>'
        )

    parts.extend([
        f'<line x1="{left}" y1="{top}" x2="{left}" '
        f'y2="{height-bottom}" class="axis"/>',
        f'<line x1="{left}" y1="{height-bottom}" '
        f'x2="{width-right}" y2="{height-bottom}" class="axis"/>',
        f'<text x="{left + plot_width/2}" y="{height-25}" '
        f'text-anchor="middle" font-size="15">'
        'Mean maximum drawdown (€) — lower is better</text>',
        f'<text x="23" y="{top + plot_height/2}" '
        f'transform="rotate(-90 23 {top + plot_height/2})" '
        f'text-anchor="middle" font-size="15">'
        'Mean P&amp;L (€) — higher is better</text>',
    ])

    colors = {0.50: "#2563eb", 1.00: "#dc2626"}

    # Slightly offset labels to reduce overlap.
    for point in points:
        x = x_pos(point["drawdown"])
        y = y_pos(point["pnl"])
        color = colors[point["flow"]]

        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" '
            f'fill="{color}" stroke="white" stroke-width="1.5"/>'
        )
        parts.append(
            f'<text x="{x+8:.1f}" y="{y-8:.1f}" '
            f'font-size="10">{point["skew"]:.3f}</text>'
        )

    # Legend.
    for index, flow in enumerate(FLOW_VALUES):
        y = 85 + index * 25
        color = colors[flow]
        parts.append(
            f'<circle cx="745" cy="{y}" r="5" fill="{color}"/>'
            f'<text x="758" y="{y+4}" font-size="12">'
            f'Flow {flow:.2f}</text>'
        )

    parts.append("</svg>")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(parts))


def main():
    points = []

    print("\nRISK–RETURN SENSITIVITY")
    print("-" * 75)
    print(
        f"{'Flow':>6} {'Skew':>8} {'Mean P&L':>12} "
        f"{'Mean DD':>12} {'Avg |Inv|':>12}"
    )

    for flow in FLOW_VALUES:
        for skew in SKEW_VALUES:
            results = []

            for seed in SEEDS:
                config = SimulationConfig(
                    initial_cash=10_000.0,
                    flow_strength=flow,
                    inventory_skew=skew,
                    steps=1000,
                    seed=seed,
                )
                results.append(analyse_run(config))

            point = {
                "flow": flow,
                "skew": skew,
                "pnl": mean(r["pnl"] for r in results),
                "drawdown": mean(r["drawdown"] for r in results),
                "avg_inventory": mean(
                    r["avg_abs_inventory"] for r in results
                ),
            }
            points.append(point)

            print(
                f"{flow:6.2f} {skew:8.3f} "
                f"{point['pnl']:12.3f} "
                f"{point['drawdown']:12.3f} "
                f"{point['avg_inventory']:12.3f}"
            )

    svg_chart(points)

    print("\nChart saved as risk_return.svg")
    print("Open it with: open risk_return.svg")


if __name__ == "__main__":
    main()
