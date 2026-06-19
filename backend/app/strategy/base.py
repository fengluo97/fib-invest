from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd
from app.strategy.signal import Signal


class Strategy(ABC):
    name: str = ""
    frequency: str = "daily"
    symbols: List[str] = []
    mode: str = "semi-auto"
    risk_profile: dict = {}

    @abstractmethod
    async def on_start(self) -> None:
        """Initialize strategy, load models, warm up indicators."""

    @abstractmethod
    async def on_bar(self, bar: pd.Series) -> Optional[Signal]:
        """Process one bar and optionally return a signal."""

    @abstractmethod
    async def on_stop(self) -> None:
        """Cleanup resources."""

    def __repr__(self) -> str:
        return f"{self.name}(symbols={self.symbols}, mode={self.mode})"
