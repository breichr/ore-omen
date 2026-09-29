import pytest

from app.game.character import RuleError
from app.game.settlement import plan_build

LUMBER = dict(
    base_cost={"wood": 50, "dollars": 20}, base_seconds=300, black_ore_per_level=0, excludes=()
)
MAIN = dict(
    base_cost={"wood": 100, "iron": 50, "dollars": 100},
    base_seconds=1200,
    black_ore_per_level=0,
    excludes=(),
)
CHAPEL = dict(
    base_cost={"wood": 120, "iron": 60, "dollars": 150},
    base_seconds=900,
    black_ore_per_level=0,
    excludes=("ore_shrine",),
)
SHRINE = dict(
    base_cost={"wood": 100, "iron": 80},
    base_seconds=720,
    black_ore_per_level=5,
    excludes=("chapel",),
)
RICH = {"wood": 10_000, "iron": 10_000, "black_ore": 1_000}


def plan(code, spec, levels=None, in_queue=(), resources=RICH, dollars=10_000):
    return plan_build(
        code, **spec, levels=levels or {}, in_queue=in_queue, resources=resources, dollars=dollars
    )


def err(*a, **kw):
    with pytest.raises(RuleError) as e:
        plan(*a, **kw)
    return e.value.code


def test_start_state_can_build_tent_only():
    start = {"wood": 200, "iron": 50}
    p = plan("main_house", MAIN, resources=start, dollars=150)
    assert (p.target_level, p.seconds) == (1, 1200)
    assert p.cost == {"wood": 100, "iron": 50, "dollars": 100}
    assert err("lumber_yard", LUMBER, resources=start, dollars=150) == "main_house_too_low"


def test_build_time_uses_main_house_level_at_start():
    p = plan("lumber_yard", LUMBER, levels={"main_house": 3, "lumber_yard": 2})
    assert p.target_level == 3
    assert p.seconds == 614  # 300 × 1,5² = 675 s × (1 − 0,03 × 3) = 614,25


def test_cost_of_next_level():
    p = plan("lumber_yard", LUMBER, levels={"main_house": 5, "lumber_yard": 2})
    assert p.cost == {"wood": 128, "dollars": 51}


def test_queue_rules():
    levels = {"main_house": 4, "lumber_yard": 1}
    assert err("lumber_yard", LUMBER, levels=levels, in_queue=["lumber_yard"]) == "already_building"
    assert err("lumber_yard", LUMBER, levels=levels, in_queue=["storehouse"]) == "queue_full"
    # from main house 5: two builds at the same time
    levels5 = {"main_house": 5, "lumber_yard": 1}
    assert plan("lumber_yard", LUMBER, levels=levels5, in_queue=["storehouse"]).target_level == 2
    assert err("lumber_yard", LUMBER, levels=levels5, in_queue=["a", "b"]) == "queue_full"


def test_max_levels():
    assert (
        err("lumber_yard", LUMBER, levels={"main_house": 2, "lumber_yard": 2})
        == "main_house_too_low"
    )
    assert err("main_house", MAIN, levels={"main_house": 10}) == "max_level"


def test_not_enough_resources_or_dollars():
    levels = {"main_house": 1}
    assert (
        err("lumber_yard", LUMBER, levels=levels, resources={"wood": 49}) == "not_enough_resources"
    )
    assert err("lumber_yard", LUMBER, levels=levels, dollars=19) == "not_enough_resources"


def test_chapel_and_ore_shrine_exclude_each_other():
    levels = {"main_house": 3, "chapel": 1}
    assert err("ore_shrine", SHRINE, levels=levels) == "excluded"
    assert err("chapel", CHAPEL, levels={"main_house": 3, "ore_shrine": 2}) == "excluded"
    # also while the other one is under construction
    assert err("ore_shrine", SHRINE, levels={"main_house": 5}, in_queue=["chapel"]) == "excluded"


def test_supernatural_needs_black_ore():
    p = plan("ore_shrine", SHRINE, levels={"main_house": 1})
    assert p.cost["black_ore"] == 5
    assert (
        err(
            "ore_shrine",
            SHRINE,
            levels={"main_house": 1},
            resources={"wood": 999, "iron": 999, "black_ore": 4},
        )
        == "not_enough_resources"
    )
