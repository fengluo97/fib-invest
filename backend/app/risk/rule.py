from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from app.strategy.signal import Signal


@dataclass
class RiskResult:
    passed: bool
    message: str
    adjusted_quantity: Optional[int] = None


class RiskRule(ABC):
    name: str = ""
    severity: str = "block"  # block | warn | limit

    @abstractmethod
    def evaluate(
        self, signal: Signal, portfolio: Dict[str, Any], context: Dict[str, Any]
    ) -> RiskResult:
        """Evaluate signal against this rule. Return RiskResult with passed=False to block."""
