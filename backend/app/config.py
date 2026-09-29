from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings from environment variables (prefix OO_)."""

    model_config = SettingsConfigDict(env_prefix="OO_", env_file=".env", extra="ignore")

    env: str = "development"
    database_url: str = "postgresql+psycopg://ore:ore@localhost:5432/ore_omen"

    session_cookie_name: str = "oo_session"
    session_days: int = 30
    session_touch_minutes: int = 5  # write last_seen/expires at most this often
    cookie_secure: bool = True

    # Rate limits: requests per window per client IP
    rate_limit_login: int = 10
    rate_limit_register: int = 5
    rate_limit_recover: int = 5
    rate_limit_write: int = 60
    rate_limit_window_seconds: int = 60

    worker_poll_seconds: float = 5.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
