import pytest
from decimal import Decimal
from app.strategy.signal import Signal
from app.risk.engine import RiskEngine
from app.risk.rules.daily_loss import DailyLossRule
from app.execution.adapters.simulated import SimulatedBroker
from app.execution.order_builder import OrderBuilder
from app.execution.pipeline import ExecutionPipeline


@pytest.fixture
def pipeline():
    risk_engine = RiskEngine([DailyLossRule(daily_loss_limit=Decimal("5000"))])
    broker = SimulatedBroker(initial_capital=Decimal("100000"))
    builder = OrderBuilder(default_quantity=100)
    return ExecutionPipeline(risk_engine=risk_engine, broker=broker, order_builder=builder)


async def test_pipeline_auto_mode_executes_order(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("0")})
    assert result is not None
    assert result.success


async def test_pipeline_semi_auto_does_not_execute(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "semi-auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("0")})
    assert result is None  # semi-auto: order stored but not submitted yet


async def test_pipeline_risk_blocks_signal(pipeline):
    signal = Signal(strategy_id="ma_cross_1", symbol="000001.sz", direction="BUY", strength=0.8, reason="test")
    strategy_config = {"mode": "auto"}

    result = await pipeline.process_signal(signal, strategy_config, portfolio={"daily_pnl": Decimal("-10000")})
    assert result is None  # Risk blocked it
