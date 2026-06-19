from datetime import date
from decimal import Decimal
from sqlalchemy import String, Date, Numeric, BigInteger, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class DailyBar(Base):
    __tablename__ = "daily_bars"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    high: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    low: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    volume: Mapped[int] = mapped_column(BigInteger)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    adj_factor: Mapped[Decimal] = mapped_column(Numeric(10, 6), default=Decimal("1.0"))
