from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Character(Base):
    __tablename__ = "characters"
    __table_args__ = (
        CheckConstraint("corruption_tenths BETWEEN 0 AND 1000", name="corruption_range"),
        CheckConstraint("dollars >= 0", name="dollars_non_negative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # One character per account
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name: Mapped[str] = mapped_column(String(20))
    name_key: Mapped[str] = mapped_column(String(40), unique=True)  # casefolded, for uniqueness
    character_class: Mapped[str] = mapped_column("class", String(20))
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    strength: Mapped[int] = mapped_column(Integer)
    dexterity: Mapped[int] = mapped_column(Integer)
    intellect: Mapped[int] = mapped_column(Integer)
    charisma: Mapped[int] = mapped_column(Integer)
    unspent_attribute_points: Mapped[int] = mapped_column(Integer, default=0)
    unspent_skill_points: Mapped[int] = mapped_column(Integer, default=0)
    dollars: Mapped[int] = mapped_column(BigInteger, default=0)
    bank_dollars: Mapped[int] = mapped_column(BigInteger, default=0)
    corruption_tenths: Mapped[int] = mapped_column(Integer, default=0)
    region: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="idle")
    status_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
