from decimal import Decimal
from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class DailyLossRule(RiskRule):
    name = "daily_loss_limit"
    severity = "block"

    def __init__(self, daily_loss_limit: Decimal = Decimal("5000")):
        self.daily_loss_limit = daily_loss_limit

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        daily_pnl = portfolio.get("daily_pnl", Decimal("0"))
        if isinstance(daily_pnl, (int, float)):
            daily_pnl = Decimal(str(daily_pnl))
        if daily_pnl < -self.daily_loss_limit:
            return RiskResult(
                passed=False,
                message=f"日亏损({daily_pnl})超过限制({self.daily_loss_limit})，熔断所有策略"
            )
        return RiskResult(passed=True, message="OK")
