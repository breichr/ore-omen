"""Rounding rule for all game numbers (docs/08-technik.md, "Rundung").

ROUND_HALF_UP via decimal, applied to the absolute value: 2.5 → 3, −1.5 → −2.
Never use Python's round(), which rounds half to even.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def round_half_up(value: float | int | Decimal) -> int:
    # str() avoids binary artefacts such as 2.675 being stored as 2.67499…
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    return int(d.quantize(Decimal(1), rounding=ROUND_HALF_UP))
