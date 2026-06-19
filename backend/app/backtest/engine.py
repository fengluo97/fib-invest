import pandas as pd
from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional
from app.strategy.base import Strategy
from app.backtest.broker_sim import BacktestBroker
from app.backtest.metrics import compute_metrics


class BacktestEngine:
    def __init__(self, data_service, initial_capital: float = 100000):
        self.data_service = data_service
        self.initial_capital = initial_capital
        self._bars_cache: Dict[str, pd.DataFrame] = {}

    async def run(
        self,
        strategy: Strategy,
        symbols: List[str],
        start: date,
        end: date,
        commission_rate: float = 0.0003,
        slippage: float = 0.001,
        warmup_bars: int = 30,
    ) -> Dict:
        # Load all bars
        all_bars = {}
        for symbol in symbols:
            df = await self.data_service.get_bars(symbol, start, end)
            if df is None or df.empty:
                continue
            all_bars[symbol] = df.sort_values("date").reset_index(drop=True)

        if not all_bars:
            return {"equity_curve": pd.DataFrame(), "trades": pd.DataFrame(), "metrics": {}}

        broker = BacktestBroker(
            initial_capital=self.initial_capital,
            commission_rate=commission_rate,
            slippage=slippage,
        )

        await strategy.on_start()

        # Build unified timeline from all symbols
        first_symbol = list(all_bars.keys())[0]
        timeline = all_bars[first_symbol]

        equity_records = []
        trade_records = []

        for idx, row in timeline.iterrows():
            bar = row
            current_date = bar["date"]
            if hasattr(current_date, "to_pydate"):
                current_date = current_date.to_pydate()

            # Feed bar to strategy
            signal = await strategy.on_bar(bar)

            # Process signal
            if signal is not None and idx >= warmup_bars:
                qty = self._calculate_position_size(broker, signal, float(bar["close"]))
                if qty > 0:
                    trade = broker.execute(
                        trade_date=current_date,
                        symbol=signal.symbol,
                        direction=signal.direction,
                        quantity=qty,
                        price=float(bar["close"]),
                    )
                    if trade:
                        trade_records.append({
                            "date": trade.date, "symbol": trade.symbol,
                            "direction": trade.direction, "quantity": trade.quantity,
                            "price": float(trade.price), "commission": float(trade.commission),
                            "pnl": float(trade.pnl),
                        })

            # Record equity
            prices = {sym: float(row["close"]) for sym in symbols}
            equity = broker.get_equity(prices)
            equity_records.append({"date": current_date, "equity": equity, "benchmark": equity})

        await strategy.on_stop()

        # Calculate PnL for sell trades
        trades_df = pd.DataFrame(trade_records)
        equity_df = pd.DataFrame(equity_records)
        metrics = compute_metrics(equity_df, trades_df, initial_capital=self.initial_capital)

        return {"equity_curve": equity_df, "trades": trades_df, "metrics": metrics}

    def _calculate_position_size(self, broker: BacktestBroker, signal, price: float) -> int:
        if signal.direction == "BUY":
            max_value = broker.cash * Decimal("0.95")  # Use 95% of cash max
            qty = int(float(max_value) / price / 100) * 100  # Round to lots of 100
            return max(0, qty)
        elif signal.direction == "SELL":
            pos = broker.positions.get(signal.symbol, {})
            return pos.get("quantity", 0)
        return 0
