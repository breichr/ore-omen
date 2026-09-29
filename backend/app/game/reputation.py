"""Reputation rules (docs/02-fraktionen.md)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from app.game import constants as c
from app.game.character import RuleError
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


@dataclass(frozen=True)
class RepChange:
    values: dict[str, int]  # new values for all factions
    deltas: dict[str, int]  # actual change per faction (direct + side effects)


def apply(
    values: Mapping[str, int],
    direct: Mapping[str, int],
    corruption: float,
    oath: str | None,
) -> RepChange:
    """Apply direct reputation changes with side effects and caps (docs/02-fraktionen.md).

    Side effects follow the gain actually made (a capped gain causes none). Values
    above a cap are cut to it immediately.
    """
    new = {f: values.get(f, c.REPUTATION_START) for f in c.FACTIONS}
    for faction, delta in direct.items():
        if faction not in c.FACTIONS:
            raise RuleError("unknown_faction")
        limit = cap(faction, corruption, oath)
        before = new[faction]
        new[faction] = max(c.REPUTATION_MIN, min(limit, before + delta))
        gained = new[faction] - before
        for other, loss in side_effects(faction, gained).items():
            new[other] = max(c.REPUTATION_MIN, new[other] + loss)
    for faction in c.FACTIONS:
        new[faction] = min(new[faction], cap(faction, corruption, oath))
    deltas = {f: new[f] - values.get(f, 0) for f in c.FACTIONS if new[f] != values.get(f, 0)}
    return RepChange(new, deltas)


@dataclass(frozen=True)
class OathResult:
    oath: str
    values: dict[str, int]
    lost: int  # reputation lost at the abandoned faction


def swear(values: Mapping[str, int], oath: str | None, faction: str) -> OathResult:
    """Swear to the company or the ash gang (from "respected"); switching costs 50 %."""
    if faction not in c.OATH_FACTIONS:
        raise RuleError("no_oath_faction")
    if oath == faction:
        raise RuleError("already_sworn")
    if values.get(faction, 0) < c.OATH_MIN_REPUTATION:
        raise RuleError("reputation_too_low")
    new = dict(values)
    lost = 0
    if oath is not None:
        lost = round_half_up(Decimal(max(0, new.get(oath, 0))) * Decimal(str(c.OATH_SWITCH_LOSS)))
        new[oath] = new.get(oath, 0) - lost
    return OathResult(faction, new, lost)
