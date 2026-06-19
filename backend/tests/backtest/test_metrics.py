import pandas as pd
import numpy as np
from datetime import date, timedelta
from app.backtest.metrics import compute_metrics, annualized_return, max_drawdown, sharpe_ratio


def make_equity_curve(values):
    dates = [date(2026, 1, 1) + timedelta(days=i) for i in range(len(values))]
    return pd.DataFrame({"date": dates, "equity": values, "benchmark": values})


def test_max_drawdown():
    equity = [100, 110, 90, 95, 85, 100]
    mdd = max_drawdown(equity)
    assert abs(mdd - 0.2272) < 0.01  # Peak 110 to trough 85


def test_annualized_return():
    values = [100, 110]
    ann_ret = annualized_return(values, trading_days=1)
    assert ann_ret > 0  # Positive return


def test_sharpe_ratio():
    equity = [100, 101, 102, 103, 102, 104, 105, 106, 107, 108]
    sr = sharpe_ratio(equity, risk_free_rate=0.02)
    assert sr > 0


def test_compute_metrics():
    equity = make_equity_curve([100000, 101000, 102000, 103000, 104000, 105000])
    trades = pd.DataFrame({
        "date": [date(2026, 1, 2), date(2026, 1, 4)],
        "symbol": ["000001.sz", "000001.sz"],
        "direction": ["BUY", "SELL"],
        "quantity": [1000, 1000],
        "price": [10.0, 10.5],
        "pnl": [0, 500],
        "commission": [3, 3],
    })
    metrics = compute_metrics(equity, trades, initial_capital=100000)
    assert "total_return" in metrics
    assert "max_drawdown" in metrics
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
    assert metrics["total_trades"] == 2
