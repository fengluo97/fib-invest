import pytest
import pandas as pd
from datetime import date, timedelta
from app.strategy.builtins.ma_cross import MACrossStrategy


def make_bars(prices, start_date=date(2026, 1, 5)):
    """Build a list of bar Series from a price list."""
    bars = []
    d = start_date
    for p in prices:
        bar = pd.Series({
            "date": d, "open": p, "high": p, "low": p,
            "close": p, "volume": 10000
        })
        bars.append(bar)
        d += timedelta(days=1)
    return bars


async def test_ma_cross_no_signal_during_warmup():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 5, "slow": 20}
    )
    await s.on_start()
    bars = make_bars([10.0] * 15)
    for bar in bars:
        result = await s.on_bar(bar)
        assert result is None  # Not enough data for 20-period MA


async def test_ma_cross_buy_signal():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 3, "slow": 5}
    )
    await s.on_start()
    # First 4 bars: price drops (slow MA above fast MA)
    bars = make_bars([12, 11, 10, 9, 8])
    for bar in bars:
        result = await s.on_bar(bar)
    assert result is None  # No cross yet

    # Now price rises sharply — fast MA crosses above slow MA
    more_bars = make_bars([10, 11, 12, 13], start_date=date(2026, 1, 10))
    signal = None
    for bar in more_bars:
        signal = await s.on_bar(bar)
    assert signal is not None
    assert signal.direction == "BUY"
    assert signal.symbol == "000001.sz"


async def test_ma_cross_signal_dedup():
    s = MACrossStrategy(
        symbols=["000001.sz"],
        params={"fast": 3, "slow": 5, "signal_cooldown": 5}
    )
    await s.on_start()
    bars = make_bars([12, 11, 10, 9, 8, 10, 11, 12, 13, 14, 15, 16])
    signals = []
    for bar in bars:
        sig = await s.on_bar(bar)
        if sig:
            signals.append(sig)
    # Only first crossover generates a signal (cooldown prevents spam)
    assert len(signals) == 1
