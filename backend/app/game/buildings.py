"""Pure settlement formulas (docs/03-siedlung.md).

n = target level (1–10). Base values per building come from content/buildings.yaml;
these functions only take numbers.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal

from app.game import constants as c
from app.game.rounding import round_half_up


def _check_level(level: int) -> None:
    if not 1 <= level <= c.BUILDING_MAX_LEVEL:
        raise ValueError(f"level must be 1..{c.BUILDING_MAX_LEVEL}, got {level}")


def cost(base: Mapping[str, int], level: int, black_ore_per_level: int = 0) -> dict[str, int]:
    """Kosten(n) = Basiskosten × 1,6^(n−1) per resource; supernatural: + Schwarzerz 5 × n."""
    _check_level(level)
    factor = Decimal(str(c.COST_GROWTH)) ** (level - 1)
    result = {res: round_half_up(Decimal(amount) * factor) for res, amount in base.items()}
    if black_ore_per_level:
        result["black_ore"] = result.get("black_ore", 0) + black_ore_per_level * level
    return result


def build_time_seconds(base_seconds: int, level: int, main_house_level: int) -> int:
    """Bauzeit(n) = Basiszeit × 1,5^(n−1) × (1 − 0,03 × Haupthaus-Stufe), whole seconds."""
    _check_level(level)
    t = (
        Decimal(base_seconds)
        * Decimal(str(c.BUILD_TIME_GROWTH)) ** (level - 1)
        * (1 - Decimal(str(c.BUILD_TIME_REDUCTION_PER_MAIN_HOUSE_LEVEL)) * main_house_level)
    )
    return round_half_up(t)


def production_per_hour(base_rate: float, level: int) -> int:
    """Produktion(n) = Basisrate × n × 1,1^(n−1) per hour; 0 below level 1."""
    if level <= 0:
        return 0
    _check_level(level)
    rate = Decimal(str(base_rate)) * level * Decimal(str(c.PRODUCTION_GROWTH)) ** (level - 1)
    return round_half_up(rate)


def storage_capacity(storehouse_level: int) -> int:
    """Lager(n) = 1000 × 1,3^(n−1) per resource; 500 without a storehouse."""
    if storehouse_level <= 0:
        return c.STORAGE_WITHOUT_STOREHOUSE
    _check_level(storehouse_level)
    growth = Decimal(str(c.STORAGE_GROWTH)) ** (storehouse_level - 1)
    return round_half_up(c.STORAGE_BASE * growth)


def protected_share(storehouse_level: int) -> Decimal:
    """Geschützt(n) = 10 % + 4 % × n; 10 % without a storehouse."""
    if storehouse_level <= 0:
        return Decimal(str(c.PROTECTED_WITHOUT_STOREHOUSE))
    _check_level(storehouse_level)
    return Decimal(str(c.PROTECTED_BASE)) + Decimal(str(c.PROTECTED_PER_LEVEL)) * storehouse_level


def repair_cost(current_level_cost: Mapping[str, int]) -> dict[str, int]:
    """Reparatur = 25 % der Kosten der aktuellen Stufe."""
    share = Decimal(str(c.REPAIR_COST_SHARE))
    return {res: round_half_up(amount * share) for res, amount in current_level_cost.items()}


def cancel_refund(paid: Mapping[str, int]) -> dict[str, int]:
    """Abbruch eines laufenden Baus erstattet 50 % der Kosten."""
    share = Decimal(str(c.BUILD_CANCEL_REFUND))
    return {res: round_half_up(amount * share) for res, amount in paid.items()}


def queue_slots(main_house_level: int) -> int:
    if main_house_level >= c.BUILD_QUEUE_EXTENDED_MAIN_HOUSE_LEVEL:
        return c.BUILD_QUEUE_SLOTS_EXTENDED
    return c.BUILD_QUEUE_SLOTS


def max_level(building: str, main_house_level: int) -> int:
    """Max-Stufe aller anderen Gebäude = Haupthaus-Stufe."""
    if building == "main_house":
        return c.BUILDING_MAX_LEVEL
    return min(main_house_level, c.BUILDING_MAX_LEVEL)


def main_house_name(level: int) -> str:
    for lo, hi, code in c.MAIN_HOUSE_NAMES:
        if lo <= level <= hi:
            return code
    raise ValueError(f"no main house name for level {level}")
