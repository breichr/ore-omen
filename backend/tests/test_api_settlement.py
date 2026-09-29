"""M1 integration: building, production, storage, catch-up, worker, jobs, points."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import text

from app.worker.__main__ import tick
from tests.conftest import register

ROSA = {"name": "Rosa", "class": "prospector", "allocation": {"strength": 4}}


@pytest.fixture
def player(client):
    register(client)
    assert client.post("/characters", json=ROSA).status_code == 201
    return client


def set_stock(db_sessionmaker, clock, dollars=None, **resources):
    with db_sessionmaker() as db:
        for name, amount in resources.items():
            db.execute(
                text("UPDATE resources SET amount_milli = :a, updated_at = :t WHERE name = :n"),
                {"a": amount * 1000, "t": clock.now, "n": name},
            )
        if dollars is not None:
            db.execute(text("UPDATE characters SET dollars = :d"), {"d": dollars})
        db.commit()


def settlement(client):
    r = client.get("/settlement")
    assert r.status_code == 200, r.text
    return r.json()


def stock(view):
    return {r["name"]: r["amount_milli"] // 1000 for r in view["resources"]}


def building(view, code):
    return next(b for b in view["buildings"] if b["code"] == code)


def build(client, code):
    return client.post("/settlement/build", json={"type": code})


def finish(client, clock, seconds):
    clock.now += timedelta(seconds=seconds)
    return settlement(client)


def test_start_state(player):
    v = settlement(player)
    assert stock(v)["wood"] == 200 and stock(v)["iron"] == 50
    assert v["dollars"] == 150
    assert v["capacity"] == 500 and v["protected_share"] == pytest.approx(0.10)
    assert all(b["level"] == 0 for b in v["buildings"])
    assert building(v, "main_house")["can_build"]
    assert building(v, "lumber_yard")["reason"] == "main_house_too_low"
    assert building(v, "main_house")["next"] == {
        "level": 1,
        "cost": {"wood": 100, "iron": 50, "dollars": 100},
        "seconds": 1200,
    }


def test_build_tent_pays_and_completes_on_time(player, clock):
    r = build(player, "main_house")
    assert r.status_code == 200, r.text
    v = r.json()
    assert stock(v)["wood"] == 100 and stock(v)["iron"] == 0 and v["dollars"] == 50
    assert [(q["type"], q["target_level"]) for q in v["queue"]] == [("main_house", 1)]
    assert build(player, "storehouse").json()["detail"]["code"] == "queue_full"

    assert building(finish(player, clock, 1199), "main_house")["level"] == 0
    v = finish(player, clock, 1)
    assert building(v, "main_house")["level"] == 1
    assert building(v, "main_house")["variant"] == "tent"
    assert v["queue"] == []


def test_lumber_yard_to_level_3_matches_reference(player, clock, db_sessionmaker):
    """Acceptance M1: production exact, build time = formula incl. main house bonus."""
    for _ in range(3):
        set_stock(db_sessionmaker, clock, dollars=10_000, wood=500, iron=500)
        build(player, "main_house")
        finish(player, clock, 3 * 3600)
    assert building(settlement(player), "main_house")["level"] == 3

    # 300 × 1,5^(n−1) × (1 − 0,03 × 3): the reference table is without main house bonus
    expected_seconds = {1: 273, 2: 410, 3: 614}  # 273 · 409,5 → 410 · 614,25 → 614
    for level in (1, 2, 3):
        set_stock(db_sessionmaker, clock, wood=500)
        q = build(player, "lumber_yard").json()["queue"][0]
        assert q["target_level"] == level
        took = datetime.fromisoformat(q["finishes_at"]) - datetime.fromisoformat(q["started_at"])
        assert took.total_seconds() == expected_seconds[level]
        finish(player, clock, expected_seconds[level])

    set_stock(db_sessionmaker, clock, wood=0)
    v = settlement(player)
    assert building(v, "lumber_yard")["level"] == 3
    assert building(v, "lumber_yard")["produces"] == {"wood": 73}  # 03-siedlung.md
    assert stock(finish(player, clock, 3600))["wood"] == 73


def test_production_starts_at_completion_not_at_read(player, clock, db_sessionmaker):
    set_stock(db_sessionmaker, clock, dollars=1000, wood=400, iron=400)
    build(player, "main_house")
    finish(player, clock, 1200)
    set_stock(db_sessionmaker, clock, wood=100)
    build(player, "lumber_yard")  # 291 s with main house 1
    # Nobody looks for over an hour; the catch-up applies the level at its due time
    v = finish(player, clock, 291 + 3600)
    assert stock(v)["wood"] == 100 - 50 + 20


def test_storage_fills_up_and_stops(player, clock, db_sessionmaker):
    set_stock(db_sessionmaker, clock, dollars=1000, wood=400, iron=400)
    build(player, "main_house")
    finish(player, clock, 1200)
    build(player, "lumber_yard")
    finish(player, clock, 291)
    v = finish(player, clock, 48 * 3600)
    assert stock(v)["wood"] == 500  # capacity without storehouse
    assert stock(finish(player, clock, 3600))["wood"] == 500


def test_cancel_refunds_half(player, clock):
    v = build(player, "main_house").json()
    item = v["queue"][0]["id"]
    r = player.post(f"/settlement/queue/{item}/cancel")
    assert r.status_code == 200, r.text
    v = r.json()
    assert v["queue"] == []
    assert stock(v)["wood"] == 150 and stock(v)["iron"] == 25 and v["dollars"] == 100
    # the event is cancelled: nothing happens later
    assert building(finish(player, clock, 3600), "main_house")["level"] == 0
    assert player.post(f"/settlement/queue/{item}/cancel").status_code == 404


def test_chapel_and_ore_shrine_exclude_each_other(player, clock, db_sessionmaker):
    set_stock(db_sessionmaker, clock, dollars=10_000, wood=500, iron=500, black_ore=100)
    build(player, "main_house")
    finish(player, clock, 1200)
    assert build(player, "chapel").status_code == 200
    r = build(player, "ore_shrine")
    assert r.json()["detail"]["code"] in ("excluded", "queue_full")
    finish(player, clock, 900)
    set_stock(db_sessionmaker, clock, wood=500, iron=500, black_ore=100)
    r = build(player, "ore_shrine")
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "excluded"
    assert building(settlement(player), "ore_shrine")["reason"] == "excluded"


def test_worker_processes_due_events(player, clock, db_sessionmaker):
    build(player, "main_house")
    assert tick(now=clock.now + timedelta(seconds=1199), sessions=db_sessionmaker) == 0
    assert tick(now=clock.now + timedelta(seconds=1200), sessions=db_sessionmaker) == 1
    with db_sessionmaker() as db:
        level = db.execute(text("SELECT level FROM buildings WHERE type = 'main_house'")).scalar()
        status = db.execute(text("SELECT status FROM scheduled_events")).scalar()
    assert (level, status) == (1, "done")
    # processing twice is harmless
    assert tick(now=clock.now + timedelta(hours=1), sessions=db_sessionmaker) == 0


def test_unknown_building(player):
    r = build(player, "castle")
    assert r.status_code == 409 and r.json()["detail"]["code"] == "unknown_building"


def test_settlement_needs_character(client):
    register(client)
    r = client.get("/settlement")
    assert r.status_code == 409 and r.json()["detail"]["code"] == "no_character"


# --- Jobs ------------------------------------------------------------------


def jobs(client):
    r = client.get("/jobs")
    assert r.status_code == 200, r.text
    return r.json()


def test_job_runs_and_pays(player, clock):
    j = jobs(player)
    assert j["current"] is None
    chop = next(x for x in j["jobs"] if x["code"] == "chop_wood")
    assert (chop["seconds"], chop["yield"], chop["xp"]) == (900, {"wood": 25}, 10)

    assert player.post("/jobs/chop_wood/start").status_code == 200
    r = player.post("/jobs/sort_ore/start")
    assert r.status_code == 409 and r.json()["detail"]["code"] == "job_running"
    assert player.get("/me").json()["character"]["status"] == "working"

    clock.now += timedelta(seconds=900)
    j = jobs(player)
    assert j["current"] is None
    assert j["last"]["status"] == "done"
    assert j["last"]["result"]["yield"] == {"wood": 25}
    assert stock(settlement(player))["wood"] == 225
    me = player.get("/me").json()["character"]
    assert (me["xp"], me["status"]) == (10, "idle")


def test_job_yield_is_capped_by_storage(player, clock, db_sessionmaker):
    set_stock(db_sessionmaker, clock, wood=490)
    chop = next(x for x in jobs(player)["jobs"] if x["code"] == "chop_wood")
    assert chop["overflow"] == {"wood": 15}
    player.post("/jobs/chop_wood/start")
    clock.now += timedelta(seconds=900)
    assert jobs(player)["last"]["result"]["lost"] == {"wood": 15}
    assert stock(settlement(player))["wood"] == 500


def test_job_cancel_gives_nothing(player, clock):
    player.post("/jobs/haul_crates/start")
    r = player.post("/jobs/cancel")
    assert r.status_code == 200 and r.json()["current"] is None
    clock.now += timedelta(hours=2)
    me = player.get("/me").json()["character"]
    assert (me["dollars"], me["xp"]) == (150, 0)
    assert player.post("/jobs/cancel").json()["detail"]["code"] == "no_job_running"


def test_level_up_and_spend_points(player, clock):
    for _ in range(2):  # 2 × 60 XP = 120 → level 2
        player.post("/jobs/sort_ore/start")
        clock.now += timedelta(hours=2)
        jobs(player)
    me = player.get("/me").json()["character"]
    assert (me["level"], me["xp"]) == (2, 120)
    assert (me["xp_level_start"], me["xp_next_level"]) == (100, 383)
    assert (me["unspent_attribute_points"], me["unspent_skill_points"]) == (2, 8)
    assert me["skill_cap"] == 4

    r = player.post("/me/points", json={"attributes": {"dexterity": 2}, "skills": {"aim": 4}})
    assert r.status_code == 200, r.text
    ch = r.json()
    assert ch["attributes"]["dexterity"] == 7
    assert ch["skills"]["aim"] == 4
    assert ch["duel_values"]["aim"] == 4 + 7 // 2
    assert (ch["unspent_attribute_points"], ch["unspent_skill_points"]) == (0, 4)

    r = player.post("/me/points", json={"skills": {"aim": 1}})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "skill_cap"


def test_level_2_job_yield_grows(player, clock):
    for _ in range(2):
        player.post("/jobs/sort_ore/start")
        clock.now += timedelta(hours=2)
        jobs(player)
    chop = next(x for x in jobs(player)["jobs"] if x["code"] == "chop_wood")
    assert chop["yield"] == {"wood": 28}  # 25 × 1,1 = 27,5 → 28
