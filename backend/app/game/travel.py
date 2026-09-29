"""Travel between regions (docs/01-welt.md, "Regionen")."""

from __future__ import annotations

from decimal import Decimal

from app.game import constants as c
from app.game.character import RuleError
from app.game.reputation import tier
from app.game.rounding import round_half_up


def base_minutes(origin: str, destination: str) -> int:
    for r in (origin, destination):
        if r not in c.REGIONS:
            raise RuleError("unknown_region")
    if origin == destination:
        raise RuleError("already_there")
    town = c.START_REGION
    total = c.TRAVEL_MINUTES_FROM_TOWN.get(origin, 0) + c.TRAVEL_MINUTES_FROM_TOWN.get(
        destination, 0
    )
    if town in (origin, destination):
        return total
    return min(total, c.TRAVEL_MINUTES_MAX)


def travel_seconds(
    origin: str, destination: str, map_room_level: int = 0, keepers_reputation: int = 0
) -> int:
    """Travel time with map room (−2 %/level) and keepers "trusted" (−15 %)."""
    if destination == "the_gorge" and keepers_reputation < c.GORGE_MIN_KEEPERS_REPUTATION:
        raise RuleError("gorge_closed")
    seconds = Decimal(base_minutes(origin, destination) * 60)
    seconds *= 1 - Decimal(str(c.MAP_ROOM_TRAVEL_REDUCTION_PER_LEVEL)) * map_room_level
    if tier(keepers_reputation) in ("trusted", "honored"):
        seconds *= 1 - Decimal(str(c.KEEPERS_TRUSTED_TRAVEL_REDUCTION))
    return round_half_up(seconds)
