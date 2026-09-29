from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

CHAR_FK = "characters.id"


class Reputation(Base):
    __tablename__ = "reputation"

    character_id: Mapped[int] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), primary_key=True
    )
    faction: Mapped[str] = mapped_column(String(16), primary_key=True)
    value: Mapped[int] = mapped_column(Integer)


class Oath(Base):
    __tablename__ = "oaths"

    character_id: Mapped[int] = mapped_column(
        ForeignKey(CHAR_FK, ondelete="CASCADE"), primary_key=True
    )
    faction: Mapped[str] = mapped_column(String(16))
    sworn_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class QuestInstance(Base):
    __tablename__ = "quest_instances"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True)
    quest_id: Mapped[str] = mapped_column(String(64), index=True)
    seed: Mapped[int] = mapped_column(BigInteger)  # never sent to the client before resolution
    state: Mapped[str] = mapped_column(String(16))  # traveling | choice | done
    day: Mapped[date] = mapped_column(Date)  # game day of the start (dailies)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)  # outcome, applied changes
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finishes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True)
    item_id: Mapped[str] = mapped_column(String(64))
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CharacterFlag(Base):
    """Unlocks, statuses and other effects stored until their system exists."""

    __tablename__ = "character_flags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey(CHAR_FK, ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(16))  # unlock | status | combat | bounty | server_flag
    key: Mapped[str] = mapped_column(String(64))
    value: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str | None] = mapped_column(String(64))  # quest id
