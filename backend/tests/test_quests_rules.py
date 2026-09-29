from datetime import date
from fractions import Fraction

import pytest

from app.game.character import RuleError
from app.game.quests import Context, blocked, chance, daily_offer, difficulty, resolve

CTX = Context(
    character_class="preacher",
    corruption=0,
    items={"strange_coat"},
    reputation={"order": 250},
    dollars=10,
    attributes={"strength": 5, "dexterity": 5, "intellect": 5, "charisma": 7},
    skills={"persuasion": 1},
)

CHECKED = {
    "label": "Nachhaken",
    "check": {"attribute": "charisma", "skill": "persuasion", "difficulty": "easy"},
    "success": {"text": "ja", "effects": {"xp": 20}},
    "failure": {"text": "nein", "effects": {"xp": 10}},
}


def test_difficulty_names():
    assert [difficulty(x) for x in ("easy", "medium", "hard", "deadly", 18)] == [15, 22, 28, 35, 18]


def test_chance_uses_attribute_and_skill():
    # 7 + 1: needs 7 on the d20 → 14/20 = 70 %
    assert chance(CHECKED, CTX) == Fraction(14, 20)
    assert chance({"label": "x"}, CTX) is None


def test_resolve_is_reproducible():
    results = {resolve(CHECKED, 0, seed=123, ctx=CTX).check.roll for _ in range(5)}
    assert len(results) == 1


def test_resolve_picks_branch():
    seen = {resolve(CHECKED, 0, seed=s, ctx=CTX).success for s in range(40)}
    assert seen == {True, False}
    o = next(
        resolve(CHECKED, 0, seed=s, ctx=CTX)
        for s in range(40)
        if resolve(CHECKED, 0, seed=s, ctx=CTX).success is False
    )
    assert (o.text, o.effects) == ("nein", {"xp": 10})


def test_option_without_check():
    o = resolve({"label": "x", "text": "t", "effects": {"dollars": -5}}, 1, 7, CTX)
    assert (o.text, o.effects, o.success) == ("t", {"dollars": -5}, None)


@pytest.mark.parametrize(
    ("req", "code"),
    [
        ({"class": "gunslinger"}, "requires_class"),
        ({"min_corruption": 25}, "requires_corruption"),
        ({"item": "bell_shard"}, "requires_item"),
        ({"reputation": {"order": 500}}, "requires_reputation"),
        ({"dollars": 11}, "requires_dollars"),
    ],
)
def test_requires(req, code):
    opt = {"label": "x", "requires": req}
    assert blocked(opt, CTX) == code
    with pytest.raises(RuleError):
        resolve(opt, 0, 1, CTX)


def test_requires_met():
    assert blocked({"label": "x", "requires": {"item": "strange_coat", "dollars": 5}}, CTX) is None


def test_daily_offer_is_stable_per_day_and_varies():
    pool = [f"q{i}" for i in range(6)]
    a = daily_offer(pool, 1, date(2026, 1, 1), "order")
    assert a == daily_offer(pool, 1, date(2026, 1, 1), "order")
    assert len(a) == 3
    days = {tuple(daily_offer(pool, 1, date(2026, 1, d), "order")) for d in range(1, 15)}
    assert len(days) > 1
    assert daily_offer(["a", "b"], 1, date(2026, 1, 1), "order") == ["a", "b"]
