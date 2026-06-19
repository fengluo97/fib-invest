import yaml
from pathlib import Path
from typing import Dict, Any
from app.strategy.base import Strategy
from app.strategy.registry import registry


def load_strategy_from_yaml(path: Path) -> Strategy:
    with open(path, "r", encoding="utf-8") as f:
        config: Dict[str, Any] = yaml.safe_load(f)

    strategy_type = config["strategy_type"]
    strategy_cls = registry.get(strategy_type)
    if strategy_cls is None:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    return strategy_cls(
        symbols=config.get("symbols", []),
        params=config.get("params", {}),
        mode=config.get("mode", "semi-auto"),
    )


def save_strategy_config(strategy: Strategy, path: Path) -> None:
    config = {
        "strategy_type": strategy.name,
        "symbols": strategy.symbols,
        "params": getattr(strategy, "_params", {}),
        "mode": strategy.mode,
        "risk_profile": strategy.risk_profile,
    }
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True)
