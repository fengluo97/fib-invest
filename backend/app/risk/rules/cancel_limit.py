from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class CancelLimitRule(RiskRule):
    name = "cancel_limit"
    severity = "block"

    def __init__(self, max_cancels: int = 5):
        self.max_cancels = max_cancels

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        strategy_cancels = context.get("strategy_cancels_today", {})
        cancels = strategy_cancels.get(signal.strategy_id, 0)
        if cancels >= self.max_cancels:
            return RiskResult(
                passed=False,
                message=f"策略 {signal.strategy_id} 当日撤单{cancels}次，超过限制{self.max_cancels}"
            )
        return RiskResult(passed=True, message="OK")
