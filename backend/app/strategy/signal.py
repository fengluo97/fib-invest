from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Signal:
    strategy_id: str
    symbol: str
    direction: str      # BUY | SELL | HOLD
    strength: float     # 0.0 ~ 1.0
    reason: str
    meta: dict = field(default_factory=dict)
