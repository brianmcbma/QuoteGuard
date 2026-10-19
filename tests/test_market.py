import pytest

from quoteguard.market import MarketMaker, MarketState, Quote


def test_market_state_rejects_nonpositive_price():
    with pytest.raises(ValueError):
        MarketState(0)


def test_quote_requires_bid_below_ask():
    with pytest.raises(ValueError):
        Quote(bid=100, ask=99)


def test_buying_inventory_updates_cash_and_position():
    maker = MarketMaker()
    maker.buy_from_seller(price=99, quantity=2)

    assert maker.cash == -198
    assert maker.inventory == 2


def test_selling_inventory_updates_cash_and_position():
    maker = MarketMaker(inventory=2)
    maker.sell_to_buyer(price=101, quantity=1)

    assert maker.cash == 101
    assert maker.inventory == 1


def test_mark_to_market():
    maker = MarketMaker()
    maker.buy_from_seller(price=99)

    assert maker.mark_to_market(mid_price=100) == 1


def test_selling_can_create_short_position():
    maker = MarketMaker()
    maker.sell_to_buyer(price=101, quantity=2)

    assert maker.cash == 202
    assert maker.inventory == -2
    assert maker.mark_to_market(mid_price=100) == 2


def test_invalid_trade_is_rejected():
    maker = MarketMaker()

    with pytest.raises(ValueError):
        maker.buy_from_seller(price=100, quantity=0)
