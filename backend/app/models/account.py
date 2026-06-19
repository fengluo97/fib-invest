from decimal import Decimal
from sqlalchemy import String, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(10), default="CNY")


class Position(Base):
    __tablename__ = "positions"

    account_id: Mapped[str] = mapped_column(String(50), ForeignKey("accounts.id"), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_cost: Mapped[Decimal] = mapped_column(Numeric(10, 4), default=Decimal("0"))
