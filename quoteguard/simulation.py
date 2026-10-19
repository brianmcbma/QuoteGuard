from dataclasses import dataclass
import random

from quoteguard.market import MarketMaker
from quoteguard.strategy import StrategyConfig, make_quote


@dataclass(frozen=True)
class SimulationConfig:
    initial_price: float = 100.0
    volatility: float = 0.05
    fill_probability: float = 0.7
    flow_strength: float = 0.6
    steps: int = 1000
    seed: int = 42
    max_inventory: int = 10

    def __post_init__(self) -> None:
        if self.initial_price <= 0:
            raise ValueError("Initial price must be positive.")
        if self.volatility < 0:
            raise ValueError("Volatility cannot be negative.")
        if not 0 <= self.fill_probability <= 1:
            raise ValueError("Fill probability must be between 0 and 1.")
        if not 0 <= self.flow_strength <= 1:
            raise ValueError("Flow strength must be between 0 and 1.")
        if self.steps <= 0:
            raise ValueError("Steps must be positive.")
        if self.max_inventory < 1:
            raise ValueError("Maximum inventory must be positive.")


@dataclass(frozen=True)
class SimulationResult:
    final_price: float
    final_cash: float
    final_inventory: int
    final_equity: float
    trades: int
    history: tuple[dict[str, float], ...]


def run_simulation(config: SimulationConfig) -> SimulationResult:
    rng = random.Random(config.seed)
    price = config.initial_price
    maker = MarketMaker()
    trades = 0
    history = []

    strategy_config = StrategyConfig(
        max_inventory=config.max_inventory
    )

    for step in range(config.steps):
        # Hidden directional pressure in the simulated market.
        signal = rng.choice((-1, 1))

        quote = make_quote(
            mid_price=price,
            inventory=maker.inventory,
            config=strategy_config,
        )

        trade_direction = 0
        fill_price = 0.0
        maker_position_change = 0

        buy_probability = (
            0.5 + 0.5 * config.flow_strength * signal
        )

        if rng.random() < config.fill_probability:
            if rng.random() < buy_probability:
                # A buyer lifts our ask: we sell.
                if maker.inventory > -config.max_inventory:
                    trade_direction = 1
                    fill_price = quote.ask
                    maker.sell_to_buyer(fill_price)
                    maker_position_change = -1
                    trades += 1
            else:
                # A seller hits our bid: we buy.
                if maker.inventory < config.max_inventory:
                    trade_direction = -1
                    fill_price = quote.bid
                    maker.buy_from_seller(fill_price)
                    maker_position_change = 1
                    trades += 1

        # The hidden signal affects the subsequent market move.
        noise = rng.gauss(0, config.volatility)
        price *= (
            1
            + (
                signal * config.flow_strength * config.volatility
                + noise
            ) / 100
        )
        price = max(price, 0.01)

        # Immediate markout: the fill's value relative to the next mid.
        if trade_direction != 0:
            maker_markout = (
                maker_position_change * (price - fill_price)
            )
        else:
            maker_markout = 0.0

        history.append({
            "step": float(step),
            "mid_price": price,
            "bid": quote.bid,
            "ask": quote.ask,
            "cash": maker.cash,
            "inventory": float(maker.inventory),
            "equity": maker.mark_to_market(price),
            "trade_direction": float(trade_direction),
            "fill_price": fill_price,
            "next_mid_price": price,
            "maker_markout": maker_markout,
        })

    return SimulationResult(
        final_price=price,
        final_cash=maker.cash,
        final_inventory=maker.inventory,
        final_equity=maker.mark_to_market(price),
        trades=trades,
        history=tuple(history),
    )
