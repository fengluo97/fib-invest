from typing import List, Dict, Any
from app.risk.rule import RiskRule, RiskResult
from app.strategy.signal import Signal


class RiskEngine:
    def __init__(self, rules: List[RiskRule] | None = None):
        self._rules = rules or []

    def add_rule(self, rule: RiskRule) -> None:
        self._rules.append(rule)

    def evaluate(
        self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]
    ) -> List[RiskResult]:
        results = []
        for rule in self._rules:
            result = rule.evaluate(signal, portfolio, context)
            results.append(result)
        return results

    @property
    def rules(self) -> List[RiskRule]:
        return list(self._rules)
