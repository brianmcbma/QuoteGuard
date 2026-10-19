from dataclasses import dataclass


@dataclass(frozen=True)
class MarketState:
    mid_price: float

    def __post_init__(self) -> None:
        if self.mid_price <= 0:
            raise ValueError("Mid-price must be positive.")


@dataclass(frozen=True)
class Quote:
    bid: float
    ask: float

    def __post_init__(self) -> None:
        if self.bid <= 0 or self.ask <= 0:
            raise ValueError("Quote prices must be positive.")
        if self.bid >= self.ask:
            raise ValueError("Bid must be below ask.")


@dataclass
class MarketMaker:
    cash: float = 0.0
    inventory: int = 0

    def buy_from_seller(self, price: float, quantity: int = 1) -> None:
        self._validate_trade(price, quantity)
        self.cash -= price * quantity
        self.inventory += quantity

    def sell_to_buyer(self, price: float, quantity: int = 1) -> None:
        """Sell inventory; negative inventory represents a short position."""
        self._validate_trade(price, quantity)
        self.cash += price * quantity
        self.inventory -= quantity

    @staticmethod
    def _validate_trade(price: float, quantity: int) -> None:
        if price <= 0:
            raise ValueError("Trade price must be positive.")
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")

    def mark_to_market(self, mid_price: float) -> float:
        if mid_price <= 0:
            raise ValueError("Mid-price must be positive.")
        return self.cash + self.inventory * mid_price
