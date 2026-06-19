from decimal import Decimal
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import date


@dataclass
class BacktestTrade:
    date: date
    symbol: str
    direction: str
    quantity: int
    price: Decimal
    pnl: Decimal = Decimal("0")
    commission: Decimal = Decimal("0")


class BacktestBroker:
    def __init__(self, initial_capital: float = 100000, commission_rate: float = 0.0003, slippage: float = 0.0):
        self.initial_capital = Decimal(str(initial_capital))
        self.cash = Decimal(str(initial_capital))
        self.commission_rate = Decimal(str(commission_rate))
        self.slippage = Decimal(str(slippage))
        self.positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_cost}
        self.trades: List[BacktestTrade] = []
        self._equity: List[float] = []

    def execute(self, trade_date: date, symbol: str, direction: str, quantity: int, price: float) -> BacktestTrade | None:
        qty = Decimal(str(quantity))
        p = Decimal(str(price))

        # Apply slippage
        if direction == "BUY":
            p = p * (Decimal("1") + self.slippage)
        else:
            p = p * (Decimal("1") - self.slippage)

        amount = qty * p
        commission = amount * self.commission_rate
        pnl = Decimal("0")

        if direction == "BUY":
            total_cost = amount + commission
            if total_cost > self.cash:
                return None  # Insufficient cash
            self.cash -= total_cost
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_qty = pos["quantity"] + int(qty)
                pos["avg_cost"] = (Decimal(str(pos["quantity"])) * pos["avg_cost"] + amount + commission) / Decimal(str(total_qty))
                pos["quantity"] = total_qty
            else:
                self.positions[symbol] = {"quantity": int(qty), "avg_cost": (amount + commission) / qty}
        else:  # SELL
            if symbol not in self.positions or self.positions[symbol]["quantity"] < int(qty):
                return None
            pos = self.positions[symbol]
            self.cash += amount - commission
            pnl = (p - pos["avg_cost"]) * qty
            pos["quantity"] -= int(qty)
            if pos["quantity"] == 0:
                del self.positions[symbol]

        trade = BacktestTrade(
            date=trade_date, symbol=symbol, direction=direction,
            quantity=int(qty), price=p, pnl=pnl, commission=commission
        )
        self.trades.append(trade)
        return trade

    def get_equity(self, prices: Dict[str, float]) -> float:
        pos_value = Decimal("0")
        for sym, pos in self.positions.items():
            if sym in prices:
                pos_value += Decimal(str(pos["quantity"])) * Decimal(str(prices[sym]))
        return float(self.cash + pos_value)

    def reset(self):
        self.cash = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self._equity.clear()
