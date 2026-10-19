import pytest

from quoteguard.metrics import (
    maximum_drawdown,
    sharpe_ratio,
    total_pnl,
)


def test_total_pnl():
    assert total_pnl([100, 103, 98, 110]) == 10


def test_maximum_drawdown():
    assert maximum_drawdown([100, 120, 90, 110]) == pytest.approx(0.25)


def test_no_drawdown_when_equity_only_rises():
    assert maximum_drawdown([100, 105, 110]) == 0


def test_sharpe_requires_two_returns():
    with pytest.raises(ValueError):
        sharpe_ratio([0.01])


def test_sharpe_is_zero_for_constant_returns():
    assert sharpe_ratio([0.01, 0.01, 0.01]) == 0

from quoteguard.metrics import (
    average_maker_markout,
    adverse_selection_rate,
)


def test_average_maker_markout():
    assert average_maker_markout([1.0, -1.0, 2.0]) == 2.0 / 3.0


def test_adverse_selection_rate():
    assert adverse_selection_rate([1.0, -1.0, -2.0, 3.0]) == 0.5


def test_average_maker_markout_rejects_empty_list():
    import pytest

    with pytest.raises(ValueError):
        average_maker_markout([])


def test_adverse_selection_rate_rejects_empty_list():
    import pytest

    with pytest.raises(ValueError):
        adverse_selection_rate([])

