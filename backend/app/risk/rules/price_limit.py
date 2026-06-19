from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class PriceLimitRule(RiskRule):
    name = "price_limit"
    severity = "block"

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        is_limit_up = context.get("is_limit_up", False)
        is_limit_down = context.get("is_limit_down", False)

        if signal.direction == "BUY" and is_limit_up:
            return RiskResult(passed=False, message=f"{signal.symbol}涨停，不可买入")
        if signal.direction == "SELL" and is_limit_down:
            return RiskResult(passed=False, message=f"{signal.symbol}跌停，不可卖出")

        return RiskResult(passed=True, message="OK")
