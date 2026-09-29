from app.game.jobs import job_yield
from app.game.storage import add_capped, current_milli, overflow, produced_milli, whole

HOUR = 3600 * 1000


def test_production_over_time():
    assert produced_milli(20, HOUR) == 20_000
    assert produced_milli(20, HOUR // 2) == 10_000
    # 73/h over 1 s = 20.27 milli: fractions are kept, not lost to rounding
    assert produced_milli(73, 1000) == 20


def test_current_is_capped_by_storage():
    assert current_milli(0, 20, 500, HOUR) == 20_000
    assert current_milli(490_000, 20, 500, HOUR) == 500_000  # stops when full
    # already above capacity (e.g. start stock): stays, does not grow
    assert current_milli(600_000, 20, 500, HOUR) == 600_000


def test_add_capped_loses_overflow():
    r = add_capped({"wood": 480_000}, {"wood": 25, "iron": 10}, 500)
    assert r.amounts_milli == {"wood": 500_000, "iron": 10_000}
    assert r.lost == {"wood": 5}
    assert overflow({"wood": 0}, {"wood": 25}, 500) == {}


def test_whole_rounds_down():
    assert whole(1_999) == 1


def test_job_yield_grows_10_percent_per_level():
    assert job_yield({"wood": 25}, 1) == {"wood": 25}
    assert job_yield({"wood": 25}, 2) == {"wood": 28}  # 27,5 → 28
    assert job_yield({"iron": 40, "dollars": 30}, 11) == {"iron": 80, "dollars": 60}
