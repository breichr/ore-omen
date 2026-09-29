import random
from fractions import Fraction

import pytest

from app.game.checks import percent, roll_check, success_chance
from app.game.reputation import cap, side_effects, tier


def test_example_from_doc():
    # 02-fraktionen.md: +40 Aschenbande → −20 Kompanie, −20 Orden, −4 Hüter
    assert side_effects("ash_gang", 40) == {"company": -20, "order": -20, "keepers": -4}


def test_rounding_half_up_on_magnitude():
    # 02-fraktionen.md: +15 Aschenbande → −8, −8, −2 (−1,5 → −2)
    assert side_effects("ash_gang", 15) == {"company": -8, "order": -8, "keepers": -2}


def test_zero_shares_and_losses_have_no_side_effects():
    assert side_effects("order", 40) == {"company": -10, "ash_gang": -20}
    assert side_effects("keepers", 20) == {"company": -5, "ash_gang": -2}
    assert side_effects("company", -40) == {}


@pytest.mark.parametrize(
    ("value", "code"),
    [
        (-1000, "hated"),
        (-600, "hated"),
        (-599, "hostile"),
        (-199, "neutral"),
        (199, "neutral"),
        (200, "known"),
        (500, "respected"),
        (799, "respected"),
        (800, "trusted"),
        (1000, "honored"),
    ],
)
def test_tiers(value, code):
    assert tier(value) == code


def test_oath_caps():
    assert cap("company", 0, None) == 799
    assert cap("company", 0, "company") == 1000
    assert cap("company", 0, "ash_gang") == 799
    assert cap("order", 0, "company") == 1000
    assert cap("keepers", 0, None) == 1000


def test_corruption_caps():
    assert cap("order", 49.9, None) == 1000
    assert cap("order", 50, None) == 199
    assert cap("ash_gang", 24, "ash_gang") == 799  # trusted only from 25
    assert cap("ash_gang", 25, "ash_gang") == 999  # honored only from 50
    assert cap("ash_gang", 50, "ash_gang") == 1000


def test_success_chance():
    # Attribut 5, Skill 0: leicht 15 → W20 ≥ 10 → 55 %; mittel 22 → ≥ 17 → 20 %
    assert percent(success_chance(5, 0, 15)) == 55
    assert percent(success_chance(5, 0, 22)) == 20
    assert success_chance(5, 0, 28) == 0  # schwer: needs 23
    assert success_chance(10, 5, 15) == 1  # needs 0 → always
    assert success_chance(10, 4, 15) == 1  # needs 1
    assert success_chance(5, 0, 25) == Fraction(1, 20)  # needs 20


def test_roll_is_reproducible_with_seed():
    a = [roll_check(random.Random(42), 5, 1, 15) for _ in range(3)]
    assert len({r.roll for r in a}) == 1  # same seed → same roll
    r = a[0]
    assert r.total == r.roll + 6 and r.success == (r.total >= 15)
