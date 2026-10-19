import pytest

from quoteguard.strategy import StrategyConfig, make_quote


def test_quotes_are_symmetric_when_inventory_is_zero():
    quote = make_quote(100, 0, StrategyConfig())

    assert quote.bid == pytest.approx(99.95)
    assert quote.ask == pytest.approx(100.05)


def test_positive_inventory_shifts_quotes_down():
    config = StrategyConfig(inventory_skew=0.01)

    neutral = make_quote(100, 0, config)
    long = make_quote(100, 5, config)

    assert long.bid < neutral.bid
    assert long.ask < neutral.ask


def test_negative_inventory_shifts_quotes_up():
    config = StrategyConfig(inventory_skew=0.01)

    neutral = make_quote(100, 0, config)
    short = make_quote(100, -5, config)

    assert short.bid > neutral.bid
    assert short.ask > neutral.ask


def test_rejects_inventory_beyond_limit():
    config = StrategyConfig(max_inventory=10)

    with pytest.raises(ValueError):
        make_quote(100, 11, config)
