import logging
from datetime import date, timedelta
from app.data.adapters.akshare import AKShareDataProvider
from app.data.service import DataService

logger = logging.getLogger(__name__)

_provider = AKShareDataProvider()
_data_service = DataService(_provider)


async def sync_daily_data(ctx, symbols: list[str] | None = None):
    """Daily task: sync bar data for tracked symbols after market close."""
    if symbols is None:
        symbols = ["000001"]
    end = date.today()
    start = end - timedelta(days=30)
    count = await _data_service.sync_daily_bars(symbols, start, end)
    logger.info(f"Synced {count} daily bars for {len(symbols)} symbols")
    return {"synced_bars": count}


async def run_strategy_cycle(ctx, strategy_id: str):
    """Execute one cycle of a strategy (used for async AI/ML strategies)."""
    logger.info(f"Running strategy cycle for {strategy_id}")
    # Stub: load strategy config, run one bar cycle
    return {"strategy_id": strategy_id, "status": "completed"}
