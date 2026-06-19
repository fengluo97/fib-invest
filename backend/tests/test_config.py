import os
from app.core.config import Settings


def test_settings_loads_from_env():
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
    os.environ["REDIS_URL"] = "redis://test:6379"
    try:
        settings = Settings()
        assert "test.db" in settings.database_url
        assert "test" in settings.redis_url
    finally:
        del os.environ["DATABASE_URL"]
        del os.environ["REDIS_URL"]


def test_settings_defaults():
    settings = Settings()
    assert settings.database_url == "sqlite+aiosqlite:///./fib_invest.db"
    assert settings.redis_url == "redis://localhost:6379"
