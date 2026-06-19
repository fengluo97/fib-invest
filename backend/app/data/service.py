import pandas as pd
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.data.provider import DataProvider
from app.models.symbol import Symbol
from app.models.bar import DailyBar


class DataService:
    def __init__(self, provider: DataProvider):
        self.provider = provider
        self._session_factory = async_session

    async def sync_symbols(self, market: Optional[str] = None) -> int:
        symbols = await self.provider.list_symbols(market=market)
        async with self._session_factory() as session:
            count = 0
            for info in symbols:
                full_sym = f"{info.code}.{info.market}"
                existing = await session.get(Symbol, full_sym)
                if existing:
                    existing.name = info.name
                else:
                    session.add(Symbol(code=info.code, name=info.name, market=info.market, list_date=info.list_date))
                    count += 1
            await session.commit()
        return count

    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        async with self._session_factory() as session:
            stmt = (
                select(DailyBar)
                .where(DailyBar.symbol == symbol)
                .where(DailyBar.date >= start)
                .where(DailyBar.date <= end)
                .order_by(DailyBar.date)
            )
            result = await session.execute(stmt)
            bars = result.scalars().all()

            if bars:
                data = [
                    {"date": b.date, "open": float(b.open), "high": float(b.high),
                     "low": float(b.low), "close": float(b.close), "volume": b.volume,
                     "amount": float(b.amount), "adj_factor": float(b.adj_factor)}
                    for b in bars
                ]
                return pd.DataFrame(data)

        # Fallback to provider if not in DB
        df = await self.provider.get_bars(symbol, start, end, freq)
        if df is not None and not df.empty:
            async with self._session_factory() as save_session:
                await self._save_bars(save_session, df)
        return df

    async def sync_daily_bars(self, symbols: List[str], start: date, end: date) -> int:
        total = 0
        for symbol in symbols:
            df = await self.provider.get_bars(symbol, start, end)
            if df is not None and not df.empty:
                async with self._session_factory() as session:
                    await self._save_bars(session, df)
                    total += len(df)
        return total

    async def _save_bars(self, session: AsyncSession, df: pd.DataFrame):
        for _, row in df.iterrows():
            bar = DailyBar(
                symbol=str(row["symbol"]),
                date=row["date"].to_pydate() if hasattr(row["date"], "to_pydate") else row["date"],
                open=row["open"], high=row["high"], low=row["low"],
                close=row["close"], volume=int(row["volume"]),
                amount=row["amount"], adj_factor=row.get("adj_factor", 1.0)
            )
            session.add(bar)
        await session.commit()
