from quoteguard.simulation import SimulationConfig, run_simulation


def test_simulation_is_reproducible():
    config = SimulationConfig(steps=100, seed=7)

    first = run_simulation(config)
    second = run_simulation(config)

    assert first == second


def test_simulation_records_every_step():
    result = run_simulation(SimulationConfig(steps=50))

    assert len(result.history) == 50


def test_final_equity_matches_cash_and_inventory():
    result = run_simulation(SimulationConfig(steps=100))

    expected = (
        result.final_cash
        + result.final_inventory * result.final_price
    )

    assert abs(result.final_equity - expected) < 1e-9


def test_zero_fill_probability_produces_no_trades():
    result = run_simulation(
        SimulationConfig(steps=100, fill_probability=0)
    )

    assert result.trades == 0
    assert result.final_inventory == 0
    assert result.final_cash == 0
    assert result.final_equity == 0

def test_trade_records_have_consistent_markout():
    result = run_simulation(SimulationConfig(steps=200))

    fills = [
        row for row in result.history
        if row["trade_direction"] != 0
    ]

    assert fills, "Expected at least one fill."

    for row in fills:
        direction = row["trade_direction"]
        fill_price = row["fill_price"]
        next_mid = row["next_mid_price"]

        expected = -direction * (next_mid - fill_price)

        assert row["maker_markout"] == expected


def test_steps_without_fills_have_zero_markout():
    result = run_simulation(
        SimulationConfig(steps=100, fill_probability=0)
    )

    for row in result.history:
        assert row["trade_direction"] == 0
        assert row["fill_price"] == 0
        assert row["maker_markout"] == 0

