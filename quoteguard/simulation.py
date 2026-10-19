from dataclasses import dataclass
import math
import random

from quoteguard.market import MarketMaker
from quoteguard.strategy import StrategyConfig, make_quote


@dataclass(frozen=True)
class SimulationConfig:
    initial_price: float = 100.0
    initial_cash: float = 10_000.0
    volatility: float = 0.05
    fill_probability: float = 0.7
    flow_strength: float = 0.6
    steps: int = 1000
    seed: int = 42
    max_inventory: int = 10
    inventory_skew: float = 0.01
    fill_sensitivity: float = 5.0

    def __post_init__(self) -> None:
        if self.initial_price <= 0:
            raise ValueError("Initial price must be positive.")
        if self.initial_cash < 0:
            raise ValueError("Initial cash cannot be negative.")
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
        if self.inventory_skew < 0:
            raise ValueError("Inventory skew cannot be negative.")
        if self.fill_sensitivity < 0:
            raise ValueError("Fill sensitivity cannot be negative.")


@dataclass(frozen=True)
class SimulationResult:
    final_price: float
    final_cash: float
    final_inventory: int
    final_equity: float
    trades: int
    history: tuple[dict[str, float], ...]


def quote_fill_probability(
    distance_from_mid: float,
    half_spread: float,
    base_probability: float,
    sensitivity: float,
) -> float:
    """Estimate fill probability from quote competitiveness.

    At the reference half-spread, probability equals the base probability.
    More competitive quotes receive higher probabilities, up to 1.
    Less competitive quotes receive lower probabilities.
    """
    exponent = -sensitivity * (distance_from_mid - half_spread)

    # Keep the calculation numerically stable for extreme quote distances.
    exponent = max(-50.0, min(50.0, exponent))

    probability = base_probability * math.exp(exponent)
    return min(1.0, max(0.0, probability))


def run_simulation(config: SimulationConfig) -> SimulationResult:
    rng = random.Random(config.seed)

    price = config.initial_price
    maker = MarketMaker(cash=config.initial_cash)
    trades = 0
    history: list[dict[str, float]] = []

    strategy_config = StrategyConfig(
        max_inventory=config.max_inventory,
        inventory_skew=config.inventory_skew,
    )

    for step in range(config.steps):
        # The signal represents directional order flow.
        signal = rng.choice((-1, 1))

        quote = make_quote(
            mid_price=price,
            inventory=maker.inventory,
            config=strategy_config,
        )

        # Calculate each side's competitiveness relative to the current mid.
        bid_distance = price - quote.bid
        ask_distance = quote.ask - price

        bid_fill_probability = quote_fill_probability(
            distance_from_mid=bid_distance,
            half_spread=strategy_config.half_spread,
            base_probability=config.fill_probability,
            sensitivity=config.fill_sensitivity,
        )

        ask_fill_probability = quote_fill_probability(
            distance_from_mid=ask_distance,
            half_spread=strategy_config.half_spread,
            base_probability=config.fill_probability,
            sensitivity=config.fill_sensitivity,
        )

        # Stronger positive signals produce more buyer-initiated orders.
        buy_probability = 0.5 + 0.5 * config.flow_strength * signal

        # Draw both random values every step to keep random-number usage
        # consistent across parameter comparisons.
        direction_draw = rng.random()
        fill_draw = rng.random()

        trade_direction = 0
        fill_price = 0.0
        maker_position_change = 0

        if direction_draw < buy_probability:
            # A buyer lifts our ask, so the market maker sells.
            if (
                maker.inventory > -config.max_inventory
                and fill_draw < ask_fill_probability
            ):
                trade_direction = 1
                fill_price = quote.ask
                maker.sell_to_buyer(fill_price)
                maker_position_change = -1
                trades += 1
        else:
            # A seller hits our bid, so the market maker buys.
            if (
                maker.inventory < config.max_inventory
                and fill_draw < bid_fill_probability
            ):
                trade_direction = -1
                fill_price = quote.bid
                maker.buy_from_seller(fill_price)
                maker_position_change = 1
                trades += 1

        # The signal also influences the next price movement.
        # This creates the adverse-selection effect being studied.
        noise = rng.gauss(0, config.volatility)

        price *= 1 + (
            signal * config.flow_strength * config.volatility + noise
        ) / 100

        price = max(price, 0.01)

        if trade_direction != 0:
            maker_markout = maker_position_change * (price - fill_price)
        else:
            maker_markout = 0.0

        history.append(
            {
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
            }
        )

    return SimulationResult(
        final_price=price,
        final_cash=maker.cash,
        final_inventory=maker.inventory,
        final_equity=maker.mark_to_market(price),
        trades=trades,
        history=tuple(history),
    )


if __name__ == "__main__":
    result = run_simulation(SimulationConfig())

    print(f"Final price: €{result.final_price:.4f}")
    print(f"Final cash: €{result.final_cash:.2f}")
    print(f"Final inventory: {result.final_inventory}")
    print(f"Final equity: €{result.final_equity:.2f}")
    print(f"Trades: {result.trades}")