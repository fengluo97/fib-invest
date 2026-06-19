from decimal import Decimal
from app.strategy.signal import Signal


class OrderBuilder:
    def __init__(self, default_quantity: int = 100, default_price: Decimal | None = None):
        self.default_quantity = default_quantity
        self.default_price = default_price

    def build(self, signal: Signal, price: Decimal | None = None) -> dict:
        qty = signal.meta.get("quantity", self.default_quantity)
        order_price = price or self.default_price or Decimal("0")
        return {
            "symbol": signal.symbol,
            "direction": signal.direction,
            "quantity": qty,
            "price": order_price,
            "strategy_id": signal.strategy_id,
            "reason": signal.reason,
        }
