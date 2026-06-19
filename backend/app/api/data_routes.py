from fastapi import APIRouter, Query
from datetime import date
from app.data.adapters.akshare import AKShareDataProvider

router = APIRouter()
_provider = AKShareDataProvider()


@router.get("/symbols")
async def list_symbols(market: str = Query(None)):
    symbols = await _provider.list_symbols(market=market)
    return {"symbols": [{"code": s.code, "name": s.name, "market": s.market} for s in symbols]}


@router.get("/bars/{symbol}")
async def get_bars(symbol: str, start: date, end: date):
    df = await _provider.get_bars(symbol, start, end)
    if df is None or df.empty:
        return {"bars": []}
    # Convert date column to string for JSON serialization
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)
    return {"bars": df.to_dict(orient="records")}
