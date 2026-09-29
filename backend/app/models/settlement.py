from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

CHAR_FK = "characters.id"


class Building(Base):
    __tablename__ = "buildings"

    character_id: Mapped[int] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), primary_key=True
    )
    type: Mapped[str] = mapped_column(String(32), primary_key=True)
    level: Mapped[int] = mapped_column(Integer)
    damaged: Mapped[bool] = mapped_column(Boolean, default=False)


class BuildQueueItem(Base):
    __tablename__ = "build_queue"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(32))
    target_level: Mapped[int] = mapped_column(Integer)
    cost: Mapped[dict] = mapped_column(JSONB)  # what was paid, for the cancel refund
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finishes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    event_id: Mapped[int] = mapped_column(ForeignKey("scheduled_events.id"))


class Resource(Base):
    __tablename__ = "resources"

    character_id: Mapped[int] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    amount_milli: Mapped[int] = mapped_column(BigInteger)  # stock at updated_at
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CharacterSkill(Base):
    __tablename__ = "character_skills"

    character_id: Mapped[int] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), primary_key=True
    )
    skill: Mapped[str] = mapped_column(String(32), primary_key=True)
    points: Mapped[int] = mapped_column(Integer)


class Activity(Base):
    """A running or finished timer activity of a character (job, later travel)."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(16))  # job | travel
    ref: Mapped[str] = mapped_column(String(64))  # job code, region …
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finishes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(16))  # running | done | cancelled
    event_id: Mapped[int | None] = mapped_column(ForeignKey("scheduled_events.id"))


class ScheduledEvent(Base):
    __tablename__ = "scheduled_events"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    kind: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    character_id: Mapped[int | None] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True
    )
    # pending | done | failed | cancelled
    status: Mapped[str] = mapped_column(String(16), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(String(2000))
