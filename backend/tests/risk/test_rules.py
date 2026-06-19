import pytest
from decimal import Decimal
from app.risk.rule import RiskRule, RiskResult
from app.risk.engine import RiskEngine
from app.risk.rules.daily_loss import DailyLossRule
from app.risk.rules.position_limit import PositionLimitRule
from app.risk.rules.price_limit import PriceLimitRule
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


def test_daily_loss_rule_blocks_when_exceeded():
    rule = DailyLossRule(daily_loss_limit=Decimal("1000"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {"daily_pnl": Decimal("-1500")}
    result = rule.evaluate(signal, portfolio, {})
    assert not result.passed
    assert "亏损" in result.message


def test_daily_loss_rule_passes_when_ok():
    rule = DailyLossRule(daily_loss_limit=Decimal("1000"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {"daily_pnl": Decimal("500")}
    result = rule.evaluate(signal, portfolio, {})
    assert result.passed


def test_position_limit_rule_reduces_quantity():
    rule = PositionLimitRule(max_position_pct=Decimal("0.2"))
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    portfolio = {
        "total_value": Decimal("100000"),
        "positions": {"000001.sz": {"market_value": Decimal("25000")}}
    }
    result = rule.evaluate(signal, portfolio, {"order_quantity": 500})
    assert not result.passed
    assert result.adjusted_quantity is not None
    assert result.adjusted_quantity < 500


def test_price_limit_rule_blocks_limit_up_buy():
    rule = PriceLimitRule()
    signal = Signal(strategy_id="t1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    context = {"prev_close": Decimal("10.00"), "is_limit_up": True}
    result = rule.evaluate(signal, {}, context)
    assert not result.passed
