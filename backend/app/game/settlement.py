"""Pure build rules (docs/03-siedlung.md, "Bauwarteschlange" and "Regeln")."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from dataclasses import dataclass

from app.game import buildings as f
from app.game import constants as c
from app.game.character import RuleError


@dataclass(frozen=True)
class BuildPlan:
    target_level: int
    cost: dict[str, int]  # resources and "dollars"
    seconds: int


def plan_build(
    code: str,
    *,
    base_cost: Mapping[str, int],
    base_seconds: int,
    black_ore_per_level: int,
    excludes: Collection[str],
    levels: Mapping[str, int],
    in_queue: Collection[str],
    resources: Mapping[str, int],
    dollars: int,
) -> BuildPlan:
    """Check every rule for starting the next level of `code` and return the plan.

    `levels`: current level per building (missing = 0); `in_queue`: codes under
    construction; `resources`: whole units available now.
    """
    main_house = levels.get("main_house", 0)
    current = levels.get(code, 0)
    target = current + 1
    if code in in_queue:
        raise RuleError("already_building")
    if len(in_queue) >= f.queue_slots(main_house):
        raise RuleError("queue_full")
    if current >= c.BUILDING_MAX_LEVEL:
        raise RuleError("max_level")
    if target > f.max_level(code, main_house):
        raise RuleError("main_house_too_low")
    for other in excludes:
        if levels.get(other, 0) > 0 or other in in_queue:
            raise RuleError("excluded")
    cost = f.cost(base_cost, target, black_ore_per_level)
    for res, amount in cost.items():
        have = dollars if res == "dollars" else resources.get(res, 0)
        if have < amount:
            raise RuleError("not_enough_resources")
    return BuildPlan(target, cost, f.build_time_seconds(base_seconds, target, main_house))
