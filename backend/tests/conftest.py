from __future__ import annotations

import os
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

TEST_DB_URL = os.environ.get(
    "OO_TEST_DATABASE_URL", "postgresql+psycopg://ore:ore@localhost:5432/ore_omen_test"
)


class FakeClock:
    def __init__(self) -> None:
        self.now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture(scope="session")
def engine():
    from alembic.config import Config

    from alembic import command

    eng = create_engine(TEST_DB_URL)
    with eng.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    cfg.attributes["configure_logger"] = False
    command.upgrade(cfg, "head")
    yield eng
    eng.dispose()


@pytest.fixture
def db_sessionmaker(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE users, sessions, characters, buildings, build_queue, resources, "
                "character_skills, activities, scheduled_events, reputation, oaths, "
                "quest_instances, items, character_flags RESTART IDENTITY CASCADE"
            )
        )
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def client(db_sessionmaker, clock):
    from fastapi.testclient import TestClient

    from app.api.deps import get_now
    from app.db import get_db
    from app.main import create_app
    from app.services.ratelimit import limiter

    limiter.reset()
    app = create_app()

    def _db():
        s = db_sessionmaker()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_now] = clock
    # https so the Secure session cookie is sent back
    with TestClient(app, base_url="https://testserver") as c:
        yield c


def register(client, username="rosa", password="geheim123"):
    return client.post("/auth/register", json={"username": username, "password": password})
