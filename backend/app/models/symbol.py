from datetime import date
from typing import Any
from sqlalchemy import String, Date, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
import enum


class Market(str, enum.Enum):
    SH = "sh"
    SZ = "sz"


class Symbol(Base):
    __tablename__ = "symbols"

    code: Mapped[str] = mapped_column(String(10))
    name: Mapped[str] = mapped_column(String(50))
    market: Mapped[Market] = mapped_column(SAEnum(Market))
    list_date: Mapped[date] = mapped_column(Date)
    full_symbol: Mapped[str] = mapped_column(String(20), primary_key=True)

    def __init__(self, **kw: Any) -> None:
        if "code" in kw and "market" in kw and "full_symbol" not in kw:
            m = kw["market"]
            kw["full_symbol"] = f"{kw['code']}.{m.value if isinstance(m, Market) else m}"
        super().__init__(**kw)
