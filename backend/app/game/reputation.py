"""Reputation rules (docs/02-fraktionen.md)."""

from __future__ import annotations

from decimal import Decimal

from app.game import constants as c
from app.game.rounding import round_half_up


def tier(value: int) -> str:
    """Rufstufe for a value in −1000 … 1000."""
    code = c.REPUTATION_TIERS[0][1]
    for bound, name in c.REPUTATION_TIERS:
        if value >= bound:
            code = name
    return code


def side_effects(faction: str, gain: int) -> dict[str, int]:
    """Losses at other factions caused by a direct gain (Beziehungsmatrix).

    Only gains cause side effects; losses never do. Rounded ROUND_HALF_UP on the
    magnitude (docs/08-technik.md, "Rundung"). Factions with 0 % are omitted.
    """
    if gain <= 0:
        return {}
    result = {}
    for other, share in c.REPUTATION_SIDE_EFFECTS[faction].items():
        loss = round_half_up(Decimal(gain) * Decimal(str(share)))
        if loss:
            result[other] = -loss
    return result


def cap(faction: str, corruption: float, oath: str | None) -> int:
    """Highest value the faction's reputation may reach right now."""
    limit = c.REPUTATION_MAX
    if faction in c.OATH_FACTIONS and oath != faction:
        # No oath yet, or sworn to the other side
        limit = min(limit, c.OATH_CAP)
    if faction == "order" and corruption >= c.ORDER_CAP_CORRUPTION:
        limit = min(limit, c.ORDER_CAP_VALUE)
    if faction == "ash_gang":
        if corruption < c.ASH_GANG_TRUSTED_MIN_CORRUPTION:
            limit = min(limit, c.OATH_CAP)  # below "trusted"
        elif corruption < c.ASH_GANG_HONORED_MIN_CORRUPTION:
            limit = min(limit, c.REPUTATION_MAX - 1)  # below "honored"
    return limit
