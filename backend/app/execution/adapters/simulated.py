import uuid
from decimal import Decimal
from typing import Dict
from app.execution.broker import BrokerAdapter, OrderResult, Position, AccountInfo


class SimulatedBroker(BrokerAdapter):
    name = "simulated"

    def __init__(self, initial_capital: Decimal = Decimal("100000"), commission_rate: Decimal = Decimal("0.0003")):
        self._initial_capital = initial_capital
        self._cash = initial_capital
        self._commission_rate = commission_rate
        self._positions: Dict[str, Position] = {}
        self._order_counter = 0

    async def submit_order(self, symbol: str, direction: str, quantity: int, price: Decimal) -> OrderResult:
        qty = Decimal(str(quantity))
        price = Decimal(str(price))
        amount = qty * price
        commission = amount * self._commission_rate

        self._order_counter += 1
        order_id = f"sim_{self._order_counter}_{uuid.uuid4().hex[:6]}"

        if direction == "BUY":
            total_cost = amount + commission
            if total_cost > self._cash:
                return OrderResult(
                    success=False, order_id=order_id,
                    filled_quantity=0, filled_price=price,
                    message=f"资金不足: 需要{total_cost}, 可用{self._cash}"
                )
            self._cash -= total_cost
            if symbol in self._positions:
                pos = self._positions[symbol]
                total_qty = pos.quantity + int(qty)
                total_cost_basis = Decimal(str(pos.quantity)) * pos.avg_cost + amount + commission
                pos.quantity = total_qty
                pos.avg_cost = total_cost_basis / Decimal(str(total_qty))
            else:
                self._positions[symbol] = Position(
                    symbol=symbol, quantity=int(qty), avg_cost=(amount + commission) / qty
                )

        elif direction == "SELL":
            if symbol not in self._positions or self._positions[symbol].quantity < int(qty):
                return OrderResult(
                    success=False, order_id=order_id,
                    filled_quantity=0, filled_price=price,
                    message=f"持仓不足: {symbol}"
                )
            pos = self._positions[symbol]
            self._cash += amount - commission
            pos.quantity -= int(qty)
            if pos.quantity == 0:
                del self._positions[symbol]

        return OrderResult(
            success=True, order_id=order_id,
            filled_quantity=int(qty), filled_price=price,
            commission=commission
        )

    async def cancel_order(self, order_id: str) -> bool:
        return True  # Simulated broker executes immediately, nothing to cancel

    async def query_positions(self) -> Dict[str, Position]:
        return dict(self._positions)

    async def query_account(self) -> AccountInfo:
        return AccountInfo(account_id="sim_default", cash=self._cash, positions=dict(self._positions))
