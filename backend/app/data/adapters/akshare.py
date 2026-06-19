import os
import akshare as ak
import pandas as pd
from datetime import date
from typing import List, Optional
from app.data.provider import DataProvider, SymbolInfo

# Override system proxy so that requests made by AKShare can reach
# the internet directly. Windows registry proxy settings (e.g. from
# VPN or proxy tools) can break outbound HTTP when the proxy daemon
# is not running.
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["NO_PROXY"] = "*"


class AKShareDataProvider(DataProvider):
    name = "akshare"
    supports = ["daily"]

    async def get_bars(
        self, symbol: str, start: date, end: date, freq: str = "daily"
    ) -> Optional[pd.DataFrame]:
        """Get daily bars. Tries Eastmoney first, falls back to Sina if unreachable."""
        # Try 1: Eastmoney (stock_zh_a_hist)
        df = await self._try_eastmoney(symbol, start, end)
        if df is not None:
            return df

        # Try 2: Sina (stock_zh_a_daily) — different upstream, often works
        # when Eastmoney is blocked by corporate firewalls or proxies.
        df = await self._try_sina(symbol, start, end)
        return df

    async def _try_eastmoney(
        self, symbol: str, start: date, end: date
    ) -> Optional[pd.DataFrame]:
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol, period="daily",
                start_date=start.strftime("%Y%m%d"),
                end_date=end.strftime("%Y%m%d"),
                adjust="qfq"
            )
            if df is None or df.empty:
                return None
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "最高": "high",
                "最低": "low", "收盘": "close", "成交量": "volume",
                "成交额": "amount"
            })
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["adj_factor"] = 1.0
            df["symbol"] = symbol
            return df[["symbol", "date", "open", "high", "low", "close", "volume", "amount", "adj_factor"]]
        except Exception:
            return None

    async def _try_sina(
        self, symbol: str, start: date, end: date
    ) -> Optional[pd.DataFrame]:
        """Fallback: Sina Finance daily bars via stock_zh_a_daily."""
        try:
            # Determine market prefix: 6xxxxx → sh, others → sz
            code = symbol.zfill(6)
            sina_symbol = f"sh{code}" if code.startswith("6") else f"sz{code}"

            df = ak.stock_zh_a_daily(
                symbol=sina_symbol,
                start_date=start.strftime("%Y%m%d"),
                end_date=end.strftime("%Y%m%d"),
                adjust="qfq"
            )
            if df is None or df.empty:
                return None
            df = df.rename(columns={
                "date": "date", "open": "open", "high": "high",
                "low": "low", "close": "close", "volume": "volume",
                "amount": "amount"
            })
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["adj_factor"] = 1.0
            df["symbol"] = symbol
            return df[["symbol", "date", "open", "high", "low", "close", "volume", "amount", "adj_factor"]]
        except Exception:
            return None

    async def get_tick(self, symbol: str, trade_date: date) -> Optional[pd.DataFrame]:
        return None  # Not supported in free tier

    async def list_symbols(self, market: Optional[str] = None) -> List[SymbolInfo]:
        try:
            df = ak.stock_info_a_code_name()
            symbols = []
            for _, row in df.iterrows():
                code = str(row["code"]).zfill(6)
                mkt = "sh" if code.startswith("6") else "sz"
                if market and mkt != market:
                    continue
                symbols.append(SymbolInfo(code=code, name=row["name"], market=mkt, list_date=date(2000, 1, 1)))
            return symbols
        except Exception:
            return []

    async def health_check(self) -> bool:
        try:
            df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260101", end_date="20260601")
            if df is not None and not df.empty:
                return True
            # Fallback: try Sina if Eastmoney is unreachable
            df = ak.stock_zh_a_daily(symbol="sz000001", start_date="20260101", end_date="20260601", adjust="qfq")
            return df is not None and not df.empty
        except Exception:
            return False
