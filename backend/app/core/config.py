from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./fib_invest.db"
    redis_url: str = "redis://localhost:6379"
    config_dir: str = "./strategy_configs"
    akshare_cache_enabled: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
