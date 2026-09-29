"""Formulas from docs/03-siedlung.md, checked against the reference table there."""

from decimal import Decimal

import pytest

from app.game.buildings import (
    build_time_seconds,
    cancel_refund,
    cost,
    main_house_name,
    max_level,
    production_per_hour,
    protected_share,
    queue_slots,
    repair_cost,
    storage_capacity,
)

# Holzfällerplatz: Basis 50 Holz, 20 $, 5 min, 20 Holz/h, ohne Haupthaus-Bonus
LUMBER_BASE = {"wood": 50, "dollars": 20}
LUMBER_TIME = 5 * 60
LUMBER_RATE = 20

REFERENCE = [
    # level, wood, build time (s), production/h
    (1, 50, 5 * 60, 20),
    (3, 128, 11 * 60 + 15, 73),
    (5, 328, 25 * 60 + 19, 146),
    (7, 839, 56 * 60 + 57, 248),
    (10, 3436, None, 472),  # doc: "3 h 12 min", see test below
]


@pytest.mark.parametrize(("level", "wood", "seconds", "production"), REFERENCE)
def test_lumber_yard_reference_table(level, wood, seconds, production):
    assert cost(LUMBER_BASE, level)["wood"] == wood
    if seconds is not None:
        assert build_time_seconds(LUMBER_TIME, level, main_house_level=0) == seconds
    assert production_per_hour(LUMBER_RATE, level) == production


def test_lumber_yard_level_10_time_is_3h_12min():
    s = build_time_seconds(LUMBER_TIME, 10, main_house_level=0)
    assert s == 11533  # 300 × 1,5^9 = 11533,4 → 3 h 12 min 13 s
    assert divmod(s // 60, 60) == (3, 12)


def test_cost_rounds_every_resource():
    assert cost(LUMBER_BASE, 3) == {"wood": 128, "dollars": 51}  # 20 × 2,56 = 51,2


def test_supernatural_black_ore_is_linear():
    base = {"wood": 100, "iron": 80}
    assert cost(base, 1, black_ore_per_level=5)["black_ore"] == 5
    assert cost(base, 4, black_ore_per_level=5)["black_ore"] == 20


def test_main_house_reduces_build_time_3_percent_per_level():
    assert build_time_seconds(LUMBER_TIME, 1, main_house_level=1) == 291  # 300 × 0,97
    assert build_time_seconds(LUMBER_TIME, 1, main_house_level=10) == 210


def test_storage_reference():
    assert storage_capacity(10) == 10604  # 03-siedlung.md
    assert storage_capacity(1) == 1000
    assert storage_capacity(0) == 500  # ohne Lagerschuppen


def test_protected_share():
    assert protected_share(0) == Decimal("0.10")
    assert protected_share(1) == Decimal("0.14")
    assert protected_share(10) == Decimal("0.50")


def test_production_zero_below_level_1_and_fractional_base():
    assert production_per_hour(20, 0) == 0
    # Schürfstelle Schwarzerz 0,5/h ab Stufe 5: 0,5 × 5 × 1,1^4 = 3,66
    assert production_per_hour(0.5, 5) == 4


def test_repair_and_refund():
    assert repair_cost({"wood": 128, "dollars": 51}) == {"wood": 32, "dollars": 13}
    assert cancel_refund({"wood": 50, "dollars": 21}) == {"wood": 25, "dollars": 11}


def test_queue_slots():
    assert queue_slots(0) == 1
    assert queue_slots(4) == 1
    assert queue_slots(5) == 2


def test_max_level_follows_main_house():
    assert max_level("lumber_yard", 0) == 0
    assert max_level("lumber_yard", 3) == 3
    assert max_level("main_house", 0) == 10


def test_main_house_names():
    names = [main_house_name(n) for n in range(1, 11)]
    assert names == [
        "tent",
        "hut",
        "hut",
        "log_house",
        "log_house",
        "log_house",
        "ranch_house",
        "ranch_house",
        "ranch_house",
        "manor",
    ]


@pytest.mark.parametrize("bad", [0, 11])
def test_level_bounds(bad):
    with pytest.raises(ValueError):
        cost(LUMBER_BASE, bad)
