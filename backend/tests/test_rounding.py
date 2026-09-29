from decimal import Decimal

import pytest

from app.game.rounding import round_half_up


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2.5, 3),
        (3.5, 4),
        (72.6, 73),  # Holzfällerplatz Produktion St. 3 (03-siedlung.md)
        (327.68, 328),  # Holzfällerplatz Kosten St. 5
        (1518.75, 1519),  # Bauzeit St. 5 = 25 min 19 s
        (10604.499, 10604),  # Lager St. 10
        (-1.5, -2),  # Rufnebenwirkung (08-technik.md, "Rundung")
        (-2.4, -2),
        (0, 0),
        (Decimal("0.5"), 1),
    ],
)
def test_round_half_up(value, expected):
    assert round_half_up(value) == expected


def test_differs_from_bankers_rounding():
    assert round(2.5) == 2
    assert round_half_up(2.5) == 3
