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
    if df is None:
        return {"bars": []}
    return {"bars": df.to_dict(orient="records")}
