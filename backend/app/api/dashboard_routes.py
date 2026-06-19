from fastapi import APIRouter
from decimal import Decimal

router = APIRouter()


@router.get("/summary")
async def dashboard_summary():
    return {
        "account": {"total_value": 100000, "cash": 100000, "currency": "CNY"},
        "positions": [],
        "daily_pnl": 0,
        "strategies_running": 0,
    }
