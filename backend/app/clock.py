"""Single source of "now" outside app/game/. Tests override it via FastAPI deps."""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)
