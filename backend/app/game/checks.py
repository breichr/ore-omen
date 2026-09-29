"""Checks (docs/07-auftraege.md, "Proben"): W20 + Attribut + Skillpunkte ≥ Schwierigkeit."""

from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

from app.game import constants as c


def success_chance(attribute: int, skill: int, difficulty: int) -> Fraction:
    """Exact probability of success (shown at every option)."""
    need = difficulty - attribute - skill  # minimum die result
    hits = c.CHECK_DIE - max(1, need) + 1
    return Fraction(max(0, min(c.CHECK_DIE, hits)), c.CHECK_DIE)


def percent(chance: Fraction) -> int:
    """Whole percent for display; always a multiple of 5 with a d20."""
    return int(chance * 100)


@dataclass(frozen=True)
class CheckResult:
    roll: int
    total: int
    difficulty: int
    success: bool


def roll_check(rng: random.Random, attribute: int, skill: int, difficulty: int) -> CheckResult:
    """Roll with the instance's seeded RNG, so reloading never changes the result."""
    roll = rng.randint(1, c.CHECK_DIE)
    total = roll + attribute + skill
    return CheckResult(roll, total, difficulty, total >= difficulty)
