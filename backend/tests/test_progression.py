import pytest

from app.game.character import RuleError
from app.game.progression import (
    gain_xp,
    level_for_xp,
    spend_points,
    total_xp_for_level,
    xp_to_next,
)


def test_xp_table_from_doc():
    # 01-welt.md: 100, 283, 520, 800, 1.118 … 2.700
    assert [xp_to_next(n) for n in (1, 2, 3, 4, 5, 9)] == [100, 283, 520, 800, 1118, 2700]


def test_level_10_total_xp():
    assert total_xp_for_level(10) == 11106  # 01-welt.md


def test_level_for_xp_boundaries():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(382) == 2
    assert level_for_xp(383) == 3


def test_gain_xp_grants_points_per_level():
    up = gain_xp(level=1, xp=90, gained=300)  # 390 → level 3
    assert (up.level, up.xp, up.levels_gained) == (3, 390, 2)
    assert (up.attribute_points, up.skill_points) == (4, 6)
    same = gain_xp(level=3, xp=390, gained=10)
    assert same.levels_gained == 0 and same.attribute_points == 0


ATTRS = {"strength": 5, "dexterity": 7, "intellect": 5, "charisma": 7}


def test_spend_points():
    r = spend_points(2, ATTRS, {"aim": 1}, 2, 8, {"strength": 2}, {"aim": 3, "trade": 1})
    assert r.attributes["strength"] == 7
    assert r.skills == {"aim": 4, "trade": 1}
    assert (r.unspent_attribute_points, r.unspent_skill_points) == (0, 4)


@pytest.mark.parametrize(
    ("add_a", "add_s", "code"),
    [
        ({"strength": 3}, {}, "not_enough_attribute_points"),
        ({}, {"aim": 9}, "not_enough_skill_points"),
        ({}, {"aim": 4}, "skill_cap"),  # level 1 → max 3
        ({}, {}, "nothing_to_spend"),
        ({"luck": 1}, {}, "unknown_attribute"),
        ({}, {"lockpicking": 1}, "unknown_skill"),
        ({"strength": -1}, {}, "negative_points"),
    ],
)
def test_spend_points_errors(add_a, add_s, code):
    with pytest.raises(RuleError) as e:
        spend_points(1, ATTRS, {}, 2, 5, add_a, add_s)
    assert e.value.code == code
