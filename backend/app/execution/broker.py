from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from datetime import datetime
from typing import Dict, List


@dataclass
class OrderResult:
    success: bool
    order_id: str
    filled_quantity: int
    filled_price: Decimal
    message: str = ""
    commission: Decimal = Decimal("0")


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_cost: Decimal
    market_value: Decimal = Decimal("0")

    @property
    def unrealized_pnl(self) -> Decimal:
        return self.market_value - Decimal(str(self.quantity)) * self.avg_cost


@dataclass
class AccountInfo:
    account_id: str
    cash: Decimal
    positions: Dict[str, Position] = field(default_factory=dict)

    @property
    def total_value(self) -> Decimal:
        pos_value = sum(p.market_value for p in self.positions.values())
        return self.cash + pos_value


class BrokerAdapter(ABC):
    name: str = ""

    @abstractmethod
    async def submit_order(self, symbol: str, direction: str, quantity: int, price: Decimal) -> OrderResult:
        """Submit an order for simulated or real execution."""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""

    @abstractmethod
    async def query_positions(self) -> Dict[str, Position]:
        """Get current positions."""

    @abstractmethod
    async def query_account(self) -> AccountInfo:
        """Get account summary."""
