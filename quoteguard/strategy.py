from dataclasses import dataclass

from quoteguard.market import Quote


@dataclass(frozen=True)
class StrategyConfig:
    half_spread: float = 0.05
    inventory_skew: float = 0.01
    max_inventory: int = 10

    def __post_init__(self) -> None:
        if self.half_spread <= 0:
            raise ValueError("Half-spread must be positive.")
        if self.inventory_skew < 0:
            raise ValueError("Inventory skew cannot be negative.")
        if self.max_inventory < 1:
            raise ValueError("Maximum inventory must be positive.")


def make_quote(
    mid_price: float,
    inventory: int,
    config: StrategyConfig,
) -> Quote:
    if mid_price <= 0:
        raise ValueError("Mid-price must be positive.")

    if abs(inventory) > config.max_inventory:
        raise ValueError("Inventory exceeds the configured limit.")

    # Positive inventory shifts both quotes lower, encouraging selling.
    reservation_price = mid_price - inventory * config.inventory_skew

    bid = reservation_price - config.half_spread
    ask = reservation_price + config.half_spread

    return Quote(bid=bid, ask=ask)
