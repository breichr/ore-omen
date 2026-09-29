"""Pure quest rules (docs/07-auftraege.md): availability, options, checks, outcomes.

Quests are plain dicts as loaded from content/quests/*.json (schema.json).
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from fractions import Fraction

from app.game import constants as c
from app.game.character import RuleError
from app.game.checks import CheckResult, roll_check, success_chance


def difficulty(value: int | str) -> int:
    if isinstance(value, int):
        return value
    if value not in c.CHECK_DIFFICULTIES:
        raise RuleError("unknown_difficulty")
    return c.CHECK_DIFFICULTIES[value]


@dataclass(frozen=True)
class Context:
    """What an option may require of the character."""

    character_class: str
    corruption: float
    items: Collection[str]
    reputation: Mapping[str, int]
    dollars: int
    attributes: Mapping[str, int]
    skills: Mapping[str, int] = field(default_factory=dict)


def blocked(option: Mapping, ctx: Context) -> str | None:
    """Why an option cannot be chosen (rule code), or None."""
    req = option.get("requires") or {}
    if "class" in req and ctx.character_class != req["class"]:
        return "requires_class"
    if "min_corruption" in req and ctx.corruption < req["min_corruption"]:
        return "requires_corruption"
    if "max_corruption" in req and ctx.corruption > req["max_corruption"]:
        return "requires_corruption"
    if "item" in req and req["item"] not in ctx.items:
        return "requires_item"
    for faction, minimum in (req.get("reputation") or {}).items():
        if ctx.reputation.get(faction, 0) < minimum:
            return "requires_reputation"
    if ctx.dollars < req.get("dollars", 0):
        return "requires_dollars"
    return None


def chance(option: Mapping, ctx: Context) -> Fraction | None:
    """Success chance shown at the option; None if there is no check."""
    check = option.get("check")
    if not check:
        return None
    skill = ctx.skills.get(check.get("skill", ""), 0)
    return success_chance(
        ctx.attributes[check["attribute"]], skill, difficulty(check["difficulty"])
    )


@dataclass(frozen=True)
class Outcome:
    text: str
    effects: dict
    success: bool | None  # None: no check
    check: CheckResult | None = None


def option_rng(seed: int, index: int) -> random.Random:
    """Each option of an instance has its own fixed roll: reloading changes nothing."""
    return random.Random(f"{seed}:{index}")


def resolve(option: Mapping, index: int, seed: int, ctx: Context) -> Outcome:
    reason = blocked(option, ctx)
    if reason:
        raise RuleError(reason)
    if "combat" in option:
        # The duel engine comes with M3; until then every fight is lost (docs/07-auftraege.md)
        branch = option["failure"]
        effects = {**(branch.get("effects") or {}), "combat": option["combat"]}
        return Outcome(branch.get("text", ""), effects, False)
    check = option.get("check")
    if not check:
        return Outcome(option.get("text", ""), dict(option.get("effects") or {}), None)
    skill = ctx.skills.get(check.get("skill", ""), 0)
    result = roll_check(
        option_rng(seed, index),
        ctx.attributes[check["attribute"]],
        skill,
        difficulty(check["difficulty"]),
    )
    branch = option["success"] if result.success else option["failure"]
    return Outcome(
        branch.get("text", ""), dict(branch.get("effects") or {}), result.success, result
    )


def daily_offer(
    pool: Sequence[str], character_id: int, day: date, faction: str, count: int = 0
) -> list[str]:
    """The dailies a faction offers a character on a game day (stable for the day)."""
    count = count or c.DAILY_JOBS_PER_FACTION
    key = f"{character_id}:{day.isoformat()}:{faction}".encode()
    rng = random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))
    ordered = sorted(pool)
    return sorted(rng.sample(ordered, min(count, len(ordered))))
