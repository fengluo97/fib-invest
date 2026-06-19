from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
import pandas as pd


@dataclass
class SymbolInfo:
    code: str
    name: str
    market: str
    list_date: date


class DataProvider(ABC):
    """Abstract data provider — all market data adapters implement this interface."""

    name: str
    supports: List[str]

    @abstractmethod
    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        """Return OHLCV DataFrame with columns: date, open, high, low, close, volume, amount, adj_factor."""

    @abstractmethod
    async def get_tick(self, symbol: str, trade_date: date) -> Optional[pd.DataFrame]:
        """Return tick data for a given date."""

    @abstractmethod
    async def list_symbols(self, market: Optional[str] = None) -> List[SymbolInfo]:
        """List available symbols."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the data provider is operational."""
