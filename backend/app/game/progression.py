"""Experience and levels (docs/01-welt.md, "Erfahrung und Stufen")."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from app.game import constants as c
from app.game.character import RuleError, attribute_of_skill, skill_cap
from app.game.rounding import round_half_up


def xp_to_next(level: int) -> int:
    """XP needed for the step from `level` to `level + 1` = 100 × n^1.5."""
    if level < 1:
        raise ValueError("level must be >= 1")
    return round_half_up(c.XP_BASE * Decimal(level) ** Decimal(str(c.XP_EXPONENT)))


def total_xp_for_level(level: int) -> int:
    """Cumulative XP at which `level` is reached (level 1 = 0)."""
    return sum(xp_to_next(n) for n in range(1, level))


def level_for_xp(total_xp: int) -> int:
    level = 1
    while total_xp >= total_xp_for_level(level + 1):
        level += 1
    return level


@dataclass(frozen=True)
class LevelUp:
    level: int
    xp: int
    levels_gained: int
    attribute_points: int
    skill_points: int


def gain_xp(level: int, xp: int, gained: int) -> LevelUp:
    """Add XP (cumulative) and return the new level and the points it grants."""
    if gained < 0:
        raise ValueError("gained must be >= 0")
    new_xp = xp + gained
    new_level = max(level, level_for_xp(new_xp))
    n = new_level - level
    return LevelUp(
        level=new_level,
        xp=new_xp,
        levels_gained=n,
        attribute_points=n * c.ATTRIBUTE_POINTS_PER_LEVEL,
        skill_points=n * c.SKILL_POINTS_PER_LEVEL,
    )


@dataclass(frozen=True)
class Spent:
    attributes: dict[str, int]
    skills: dict[str, int]
    unspent_attribute_points: int
    unspent_skill_points: int


def spend_points(
    level: int,
    attributes: Mapping[str, int],
    skills: Mapping[str, int],
    unspent_attribute_points: int,
    unspent_skill_points: int,
    add_attributes: Mapping[str, int],
    add_skills: Mapping[str, int],
) -> Spent:
    """Distribute free points. Skills are capped at level + 2."""
    if set(add_attributes) - set(c.ATTRIBUTES):
        raise RuleError("unknown_attribute")
    if set(add_skills) - set(c.SKILLS):
        raise RuleError("unknown_skill")
    if any(v < 0 for v in (*add_attributes.values(), *add_skills.values())):
        raise RuleError("negative_points")
    a_sum, s_sum = sum(add_attributes.values()), sum(add_skills.values())
    if a_sum == 0 and s_sum == 0:
        raise RuleError("nothing_to_spend")
    if a_sum > unspent_attribute_points:
        raise RuleError("not_enough_attribute_points")
    if s_sum > unspent_skill_points:
        raise RuleError("not_enough_skill_points")
    new_skills = {s: skills.get(s, 0) + add_skills.get(s, 0) for s in c.SKILLS}
    for s in add_skills:
        attribute_of_skill(s)
        if new_skills[s] > skill_cap(level):
            raise RuleError("skill_cap")
    return Spent(
        attributes={a: attributes[a] + add_attributes.get(a, 0) for a in c.ATTRIBUTES},
        skills={s: v for s, v in new_skills.items() if v},
        unspent_attribute_points=unspent_attribute_points - a_sum,
        unspent_skill_points=unspent_skill_points - s_sum,
    )
