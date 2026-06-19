from decimal import Decimal
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class PositionLimitRule(RiskRule):
    name = "position_limit"
    severity = "limit"

    def __init__(self, max_position_pct: Decimal = Decimal("0.2")):
        self.max_position_pct = max_position_pct

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        total_value = portfolio.get("total_value", Decimal("0"))
        positions = portfolio.get("positions", {})
        pos = positions.get(signal.symbol, {})

        # Calculate current position percentage from market_value or market_value_pct
        current_market_value = Decimal(str(pos.get("market_value", 0)))
        current_pct = Decimal(str(pos.get("market_value_pct", 0)))
        if current_pct == 0 and current_market_value > 0 and total_value > 0:
            current_pct = current_market_value / total_value

        order_qty = context.get("order_quantity", 100)
        order_price = context.get("order_price", Decimal("0"))
        order_value = Decimal(str(order_qty)) * Decimal(str(order_price))
        new_pct = current_pct + (order_value / total_value if total_value > 0 else Decimal("0"))

        if new_pct > self.max_position_pct:
            max_value = total_value * self.max_position_pct
            current_value = current_pct * total_value
            available = max_value - current_value
            # Only compute adjusted quantity if we have a valid price
            order_price_decimal = Decimal(str(order_price))
            if order_price_decimal > 0:
                adjusted = max(0, int(available / order_price_decimal // 100 * 100))
            else:
                adjusted = 0
            return RiskResult(
                passed=False,
                message=f"仓位超限: {new_pct:.1%} > {self.max_position_pct:.1%}",
                adjusted_quantity=adjusted
            )
        return RiskResult(passed=True, message="OK")
