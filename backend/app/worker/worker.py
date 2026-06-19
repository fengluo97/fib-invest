from app.core.config import settings
from app.worker.tasks import sync_daily_data, run_strategy_cycle


class WorkerSettings:
    redis_settings = settings.redis_url
    functions = [sync_daily_data, run_strategy_cycle]
    max_jobs = 10
    poll_delay = 1.0
