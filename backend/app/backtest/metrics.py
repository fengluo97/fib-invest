import numpy as np
import pandas as pd
from typing import Dict, List


def max_drawdown(equity: List[float]) -> float:
    peak = np.maximum.accumulate(equity)
    drawdown = (np.array(equity) - peak) / peak
    return float(abs(min(drawdown)))


def annualized_return(equity: List[float], trading_days: int = 252) -> float:
    total = equity[-1] / equity[0] - 1
    years = len(equity) / trading_days
    if years == 0:
        return 0.0
    return float((1 + total) ** (1 / years) - 1)


def sharpe_ratio(equity: List[float], risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
    returns = np.diff(equity) / np.array(equity[:-1])
    if len(returns) < 2 or returns.std() == 0:
        return 0.0
    excess = returns.mean() * trading_days - risk_free_rate
    vol = returns.std() * np.sqrt(trading_days)
    return float(excess / vol) if vol > 0 else 0.0


def sortino_ratio(equity: List[float], risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
    returns = np.diff(equity) / np.array(equity[:-1])
    downside = returns[returns < 0]
    if len(downside) < 2 or downside.std() == 0:
        return 0.0
    excess = returns.mean() * trading_days - risk_free_rate
    downside_vol = downside.std() * np.sqrt(trading_days)
    return float(excess / downside_vol) if downside_vol > 0 else 0.0


def calmar_ratio(equity: List[float], trading_days: int = 252) -> float:
    ann = annualized_return(equity, trading_days)
    mdd = max_drawdown(equity)
    return float(ann / mdd) if mdd > 0 else 0.0


def compute_metrics(equity_curve: pd.DataFrame, trades: pd.DataFrame, initial_capital: float = 100000) -> Dict:
    equity = equity_curve["equity"].tolist()
    total_return = (equity[-1] / equity[0] - 1) if equity else 0

    # Trade statistics
    sell_trades = trades[trades["direction"] == "SELL"] if not trades.empty else pd.DataFrame()
    winning_trades = sell_trades[sell_trades["pnl"] > 0] if not sell_trades.empty else pd.DataFrame()

    win_rate = len(winning_trades) / len(sell_trades) if len(sell_trades) > 0 else 0
    total_pnl = trades["pnl"].sum() if not trades.empty else 0

    return {
        "total_return": round(total_return * 100, 2),
        "annualized_return": round(annualized_return(equity) * 100, 2),
        "max_drawdown": round(max_drawdown(equity) * 100, 2),
        "sharpe_ratio": round(sharpe_ratio(equity), 3),
        "sortino_ratio": round(sortino_ratio(equity), 3),
        "calmar_ratio": round(calmar_ratio(equity), 3),
        "annual_volatility": round(float(np.std(np.diff(equity) / np.array(equity[:-1])) * np.sqrt(252)) * 100, 2) if len(equity) > 2 else 0,
        "win_rate": round(win_rate * 100, 2),
        "total_trades": len(trades),
        "total_pnl": round(float(total_pnl), 2),
        "final_equity": round(equity[-1], 2) if equity else initial_capital,
    }
