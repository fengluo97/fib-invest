from decimal import Decimal
from typing import Optional, Dict, Any
from app.strategy.signal import Signal
from app.risk.engine import RiskEngine
from app.execution.broker import BrokerAdapter, OrderResult
from app.execution.order_builder import OrderBuilder


class ExecutionPipeline:
    def __init__(self, risk_engine: RiskEngine, broker: BrokerAdapter, order_builder: OrderBuilder):
        self.risk_engine = risk_engine
        self.broker = broker
        self.order_builder = order_builder

    async def process_signal(
        self,
        signal: Signal,
        strategy_config: Dict[str, Any],
        portfolio: Dict[str, Any] | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Optional[OrderResult]:
        if portfolio is None:
            portfolio = {}
        if context is None:
            context = {}

        mode = strategy_config.get("mode", "semi-auto")

        # Step 1: Risk check (mandatory for all modes)
        results = self.risk_engine.evaluate(signal, portfolio, context)
        blockers = [r for r in results if not r.passed and r.severity == "block"]
        if blockers:
            return None  # Blocked

        # Check for quantity adjustment
        limiters = [r for r in results if not r.passed and r.severity == "limit"]
        if limiters:
            context["order_quantity"] = limiters[0].adjusted_quantity or context.get("order_quantity", 100)

        # Step 2: Build order
        price = context.get("current_price", Decimal("0"))
        order_data = self.order_builder.build(signal, price=price)
        order_data["quantity"] = context.get("order_quantity", order_data["quantity"])

        # Step 3: Submit or hold based on mode
        if mode == "auto":
            return await self.broker.submit_order(
                symbol=order_data["symbol"], direction=order_data["direction"],
                quantity=order_data["quantity"], price=order_data["price"]
            )
        else:
            # semi-auto: store order for manual review
            return None  # Order saved to DB by the caller
