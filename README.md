QuoteGuard — Quantitative Market-Making Simulator

A Python research project exploring market-making strategy, inventory management, quote competitiveness, adverse selection and risk-adjusted performance.

Overview

QuoteGuard simulates a market maker quoting bid and ask prices while managing inventory risk. It investigates how directional order flow and inventory-based quote skew affect profitability and drawdown.

The project uses reproducible simulations and paired random seeds to compare strategy configurations.

Key Features

Inventory-aware bid and ask quotes.

Quote-dependent fill probabilities.

Synthetic directional order flow and price movements.

P&L, maximum drawdown and inventory-exposure metrics.

Maker markout and adverse-selection analysis.

Paired-seed comparisons with approximate 95% confidence intervals.

Training-seed parameter selection and evaluation on fresh seeds.

Risk–return chart generated as an SVG file.

Strategy

The reservation price is defined as:

[
r_t=m_t-q_t\kappa
]

where (m_t) is the simulated mid-price, (q_t) is inventory and (\kappa) is the inventory-skew parameter.

The bid and ask are placed around this reservation price using a fixed half-spread. Positive inventory shifts both quotes downwards to encourage selling and discourage further inventory accumulation.

The fill model increases estimated fill probability for more competitive quotes and decreases it for less competitive quotes.

Experimental Findings

Across the tested synthetic scenarios:

Stronger directional flow generally reduced mean P&L.

Inventory skew reduced average absolute inventory.

Greater skew often reduced drawdown but also reduced profitability.

Under moderate flow, skew 0.005 reduced mean drawdown by approximately €3.12 relative to zero skew on 50 fresh seeds.

The estimated P&L difference for that comparison was approximately +€0.27, with an approximate 95% confidence interval from -€1.08 to +€1.63.

These findings apply to the implemented simulation and do not establish real-world trading profitability.

Risk-Adjusted Objective

The experiments use the illustrative score:

[
S=\overline{\mathrm{P&L}}-\lambda\overline{\mathrm{DD}}
]

Here, (\lambda) controls the penalty applied to maximum drawdown. Different penalties can favour different inventory-skew settings.

Project Structure

QuoteGuard/
├── quoteguard/
│   ├── market.py
│   ├── strategy.py
│   ├── simulation.py
│   ├── metrics.py
│   ├── analysis.py
│   └── experiments.py
├── tests/
├── risk_return.svg
└── README.md

Setup

Requires Python 3 and pytest.

Create and activate a virtual environment on macOS or Linux:

python3 -m venv .venv
source .venv/bin/activate
python -m pip install pytest

Running QuoteGuard

Run the test suite:

python -m pytest -q

Run a simulation:

python -m quoteguard.simulation

Run the risk–return experiment:

python -m quoteguard.experiments

Open the generated chart on macOS:

open risk_return.svg

Limitations

QuoteGuard is an educational research simulator, not a production trading system.

It does not model a full limit order book, queue position, latency, exchange fees, market impact or competition between market makers. Its price dynamics, fill probabilities and risk-adjusted objective are simplified assumptions.

Further work could investigate transaction costs, alternative execution models, dynamic spreads, broader market conditions and more extensive out-of-sample testing.

Project Objective

The goal is to investigate strategy behaviour through reproducible experiments, quantify uncertainty and understand the assumptions behind quantitative trading models.