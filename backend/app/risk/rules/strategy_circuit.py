from typing import Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class StrategyCircuitBreaker(RiskRule):
    name = "strategy_circuit_breaker"
    severity = "block"

    def __init__(self, max_consecutive_losses: int = 5):
        self.max_consecutive_losses = max_consecutive_losses

    def evaluate(self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]) -> RiskResult:
        consecutive_losses = context.get("strategy_pnl", {}).get(signal.strategy_id, {}).get("consecutive_losses", 0)
        if consecutive_losses >= self.max_consecutive_losses:
            return RiskResult(
                passed=False,
                message=f"策略{signal.strategy_id}连续亏损{consecutive_losses}次，触发熔断"
            )
        return RiskResult(passed=True, message="OK")
