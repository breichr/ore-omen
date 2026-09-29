"""Lazy resource calculation (docs/08-technik.md, "Zeit und Timer").

Amounts are in thousandths (milli). Production is never ticked: the stored
amount plus rate × Δt, capped by storage.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from app.game import constants as c

S = c.RESOURCE_SCALE
MS_PER_HOUR = 3600 * 1000


def produced_milli(rate_per_hour: int, elapsed_ms: int) -> int:
    """Production in milli-units over `elapsed_ms` (rounded down)."""
    if elapsed_ms <= 0 or rate_per_hour <= 0:
        return 0
    return rate_per_hour * S * elapsed_ms // MS_PER_HOUR


def current_milli(amount_milli: int, rate_per_hour: int, capacity: int, elapsed_ms: int) -> int:
    """lager = min(kapazität, stand + rate × Δt). Never lowers an amount already above cap."""
    cap = capacity * S
    if amount_milli >= cap:
        return amount_milli
    return min(cap, amount_milli + produced_milli(rate_per_hour, elapsed_ms))


@dataclass(frozen=True)
class Added:
    amounts_milli: dict[str, int]
    lost: dict[str, int]  # whole units that did not fit


def add_capped(amounts_milli: Mapping[str, int], add: Mapping[str, int], capacity: int) -> Added:
    """Add whole units, capped by storage; the rest is lost (docs/03-siedlung.md)."""
    cap = capacity * S
    result = dict(amounts_milli)
    lost: dict[str, int] = {}
    for res, units in add.items():
        have = result.get(res, 0)
        room = max(0, cap - have)
        added = min(units * S, room)
        result[res] = have + added
        overflow = units - added // S
        if overflow > 0:
            lost[res] = overflow
    return Added(result, lost)


def overflow(amounts_milli: Mapping[str, int], add: Mapping[str, int], capacity: int) -> dict:
    """What `add` would lose right now (for UI warnings)."""
    return add_capped(amounts_milli, add, capacity).lost


def whole(amount_milli: int) -> int:
    return amount_milli // S
