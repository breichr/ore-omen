"""Jobs (docs/07-auftraege.md, "Arbeiten")."""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal

from app.game import constants as c
from app.game.rounding import round_half_up


def job_yield(base: Mapping[str, int], level: int) -> dict[str, int]:
    """Ertrag × (1 + 0,1 × (Stufe − 1)); XP is not scaled."""
    factor = 1 + Decimal(str(c.JOB_YIELD_PER_LEVEL)) * (level - 1)
    return {k: round_half_up(v * factor) for k, v in base.items()}
