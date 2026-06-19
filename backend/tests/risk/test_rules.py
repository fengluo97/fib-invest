import pytest
from decimal import Decimal
from app.risk.rule import RiskRule, RiskResult
from app.risk.engine import RiskEngine
from app.strategy.signal import Signal


class AlwaysPassRule(RiskRule):
    name = "always_pass"
    severity = "warn"

    def evaluate(self, signal, portfolio, context) -> RiskResult:
        return RiskResult(passed=True, message="OK")


class AlwaysBlockRule(RiskRule):
    name = "always_block"
    severity = "block"

    def evaluate(self, signal, portfolio, context) -> RiskResult:
        return RiskResult(passed=False, message="Blocked")


def test_risk_result_defaults():
    result = RiskResult(passed=True, message="OK")
    assert result.passed is True
    assert result.adjusted_quantity is None


def test_risk_engine_all_pass():
    engine = RiskEngine([AlwaysPassRule(), AlwaysPassRule()])
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    results = engine.evaluate(signal, portfolio={}, context={})
    assert all(r.passed for r in results)


def test_risk_engine_one_block():
    engine = RiskEngine([AlwaysPassRule(), AlwaysBlockRule()])
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    results = engine.evaluate(signal, portfolio={}, context={})
    assert any(not r.passed for r in results)
