from typing import List, Optional
from collections import deque
import pandas as pd
from app.strategy.base import Strategy
from app.strategy.signal import Signal


class MACrossStrategy(Strategy):
    """Dual moving average crossover strategy with signal dedup.

    Uses fast/slow SMA crossover to generate BUY/SELL signals.
    A crossover is confirmed after a configurable number of consecutive bars
    where the fast MA stays on the new side of the slow MA, reducing false
    signals from whipsaws.
    """

    name = "ma_cross"
    frequency = "daily"

    def __init__(self, symbols: List[str], params: dict, mode: str = "semi-auto"):
        self.symbols = symbols
        self.mode = mode
        self.risk_profile = params.get("risk_profile", {})
        self._fast = params.get("fast", 5)
        self._slow = params.get("slow", 20)
        self._cooldown = params.get("signal_cooldown", 5)
        self._confirm_bars = params.get("confirm_bars", 3)
        self._prices: dict = {}
        self._last_signal_bar: dict = {}
        self._bars_above: dict = {}
        self._bars_below: dict = {}
        self._bar_count = 0

    async def on_start(self) -> None:
        self._prices = {sym: deque(maxlen=self._slow + self._confirm_bars) for sym in self.symbols}
        self._last_signal_bar = {}
        self._bars_above = {sym: 0 for sym in self.symbols}
        self._bars_below = {sym: 0 for sym in self.symbols}
        self._bar_count = 0

    async def on_bar(self, bar: pd.Series) -> Optional[Signal]:
        self._bar_count += 1
        symbol = self.symbols[0]  # Single symbol for now
        price = float(bar["close"])
        self._prices[symbol].append(price)

        if len(self._prices[symbol]) <= self._slow:
            return None

        prices = list(self._prices[symbol])
        fast_ma = sum(prices[-self._fast:]) / self._fast
        slow_ma = sum(prices[-self._slow:]) / self._slow

        # Track consecutive bars above/below for confirmation
        if fast_ma > slow_ma:
            self._bars_above[symbol] += 1
            self._bars_below[symbol] = 0
        elif fast_ma < slow_ma:
            self._bars_below[symbol] += 1
            self._bars_above[symbol] = 0
        else:
            # Exactly equal — reset both to avoid stale confirmations
            self._bars_above[symbol] = 0
            self._bars_below[symbol] = 0

        last_sig = self._last_signal_bar.get(symbol, -999)
        cooldown_ok = (self._bar_count - last_sig) >= self._cooldown

        # Confirmed golden cross: fast > slow for confirm_bars consecutive bars
        if self._bars_above[symbol] == self._confirm_bars and cooldown_ok:
            self._last_signal_bar[symbol] = self._bar_count
            return Signal(
                strategy_id=f"ma_cross_{id(self)}", symbol=symbol,
                direction="BUY", strength=0.7,
                reason=f"Golden cross: MA{self._fast}({fast_ma:.2f}) > MA{self._slow}({slow_ma:.2f})",
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )

        # Confirmed death cross: fast < slow for confirm_bars consecutive bars
        if self._bars_below[symbol] == self._confirm_bars and cooldown_ok:
            self._last_signal_bar[symbol] = self._bar_count
            return Signal(
                strategy_id=f"ma_cross_{id(self)}", symbol=symbol,
                direction="SELL", strength=0.7,
                reason=f"Death cross: MA{self._fast}({fast_ma:.2f}) < MA{self._slow}({slow_ma:.2f})",
                meta={"fast_ma": fast_ma, "slow_ma": slow_ma}
            )

        return None

    async def on_stop(self) -> None:
        self._prices.clear()
