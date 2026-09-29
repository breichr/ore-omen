"""M2 integration: onboarding, reputation matrix, checks, dailies, travel, oath."""

from datetime import timedelta

import pytest
from sqlalchemy import text

from tests.conftest import register

ROSA = {"name": "Rosa", "class": "preacher", "allocation": {"charisma": 4}}


@pytest.fixture
def player(client):
    register(client)
    assert client.post("/characters", json=ROSA).status_code == 201
    return client


def sql(db_sessionmaker, stmt, **params):
    with db_sessionmaker() as db:
        db.execute(text(stmt), params)
        db.commit()


def quests(client):
    r = client.get("/quests")
    assert r.status_code == 200, r.text
    return r.json()


def quest(view, qid):
    return next((q for q in view["quests"] if q["id"] == qid), None)


def start(client, qid):
    return client.post(f"/quests/{qid}/start")


def choose(client, instance_id, option):
    return client.post(f"/quests/instances/{instance_id}/choose", json={"option": option})


def reps(client):
    return {f["code"]: f["value"] for f in client.get("/factions").json()["factions"]}


def test_onboarding_start_to_end(player, clock):
    v = quests(player)
    assert quest(v, "onboarding_arrival")["available"]
    assert quest(v, "onboarding_work") is None  # hidden until step 1 is done

    # 1 · Ankunft: instant, take the coat
    inst = start(player, "onboarding_arrival").json()
    assert inst["state"] == "choice" and inst["event"].startswith("Der Schaffner ist fort")
    done = choose(player, inst["id"], 0).json()
    assert done["state"] == "done" and done["outcome"]["applied"]["items"] == ["strange_coat"]

    # 2 · Erste Arbeit: 1 minute, pays like hauling crates
    inst = start(player, "onboarding_work").json()
    assert inst["state"] == "traveling"
    assert player.post("/jobs/chop_wood/start").json()["detail"]["code"] == "busy"
    clock.now += timedelta(minutes=1)
    assert quest(quests(player), "onboarding_roof")["available"]
    me = player.get("/me").json()["character"]
    assert (me["dollars"], me["xp"]) == (200, 35)

    # 3 · Ein Dach: pays the tent, done after 1 minute
    start(player, "onboarding_roof")
    s = player.get("/settlement").json()
    assert s["dollars"] == 100
    clock.now += timedelta(minutes=1)
    s = player.get("/settlement").json()
    assert next(b for b in s["buildings"] if b["code"] == "main_house")["level"] == 1

    # 4 · Der Mann aus dem Abteil: check + options with requirements
    inst = start(player, "onboarding_stranger").json()
    opts = inst["options"]
    assert opts[0]["chance"] == 75  # Charisma 9 + 0 gegen leicht 15 → W20 ≥ 6 → 15/20
    assert opts[2]["blocked"] is None  # has the coat
    done = choose(player, inst["id"], 2).json()
    assert done["outcome"]["applied"]["dollars"] == 10

    # 6 · Die Stadt ruft: matrix side effects visible
    inst = start(player, "onboarding_city").json()
    choose(player, inst["id"], 2)  # ash gang +20
    assert reps(player) == {"company": -10, "order": -10, "ash_gang": 20, "keepers": -2}
    assert all(q["chain"] != "onboarding" for q in quests(player)["quests"])


def test_reload_does_not_change_check_result(player, db_sessionmaker):
    for qid in ("onboarding_arrival", "onboarding_work", "onboarding_roof"):
        sql(
            db_sessionmaker,
            "INSERT INTO quest_instances (character_id, quest_id, seed, state, day, data, "
            "started_at, finishes_at) "
            "VALUES (1, :q, 1, 'done', '2026-01-01', '{}', now(), now())",
            q=qid,
        )
    inst = start(player, "onboarding_stranger").json()
    # Reloading the event shows the same options and chances, no roll happens
    again = player.get(f"/quests/instances/{inst['id']}").json()
    assert again["options"] == inst["options"]
    first = choose(player, inst["id"], 0).json()["outcome"]
    # Choosing again is rejected, the stored result stays
    assert choose(player, inst["id"], 0).json()["detail"]["code"] == "no_choice_pending"
    assert player.get(f"/quests/instances/{inst['id']}").json()["outcome"] == first
    assert "seed" not in str(first)
    assert first["check"]["total"] == first["check"]["roll"] + 9


def test_dailies_offered_once_per_game_day_and_need_region(player, clock):
    v = quests(player)
    daily = quest(v, "orden_salz")
    assert daily["reason"] == "wrong_region"  # Kiefernhang
    travel = {t["region"]: t for t in v["travel"]}
    assert travel["pine_slope"]["seconds"] == 900
    assert travel["the_gorge"]["reason"] == "gorge_closed"

    r = player.post("/travel", json={"region": "pine_slope"})
    assert r.status_code == 200 and r.json()["activity"]["kind"] == "travel"
    assert player.post("/travel", json={"region": "salt_flats"}).json()["detail"]["code"] == "busy"
    clock.now += timedelta(minutes=15)
    v = quests(player)
    assert v["region"] == "pine_slope" and quest(v, "orden_salz")["available"]

    start(player, "orden_salz")
    clock.now += timedelta(minutes=30)
    v = quests(player)
    assert quest(v, "orden_salz")["reason"] == "done_today"
    assert reps(player)["order"] == 10
    stock = {r["name"]: r["amount_milli"] for r in player.get("/settlement").json()["resources"]}
    assert stock["salt"] == 1000

    clock.now += timedelta(days=1)  # next game day
    assert quest(quests(player), "orden_salz")["available"]


def test_combat_is_lost_until_m3_and_delay_blocks(player, clock, db_sessionmaker):
    sql(db_sessionmaker, "UPDATE characters SET region = 'pine_slope'")
    inst = start(player, "kompanie_lohngeld").json()
    clock.now += timedelta(hours=1)
    inst = player.get(f"/quests/instances/{inst['id']}").json()
    assert inst["state"] == "choice"
    assert inst["options"][0]["combat"] is True
    out = choose(player, inst["id"], 0).json()["outcome"]
    assert out["success"] is False
    assert out["applied"]["stored"]["combat"] == {"enemy": "bandit_1", "result": "lost"}
    assert reps(player)["company"] == 0


def test_faction_quest_needs_reputation(player, db_sessionmaker, clock):
    sql(db_sessionmaker, "UPDATE characters SET region = 'pine_slope'")
    glocke = quest(quests(player), "orden_glocke")
    assert (glocke["reason"], glocke["min_tier"]) == ("reputation_too_low", "known")
    sql(db_sessionmaker, "INSERT INTO reputation VALUES (1, 'order', 200)")
    assert quest(quests(player), "orden_glocke")["available"]
    inst = start(player, "orden_glocke").json()
    clock.now += timedelta(minutes=45)
    out = choose(player, inst["id"], 2).json()["outcome"]  # sell the bell
    assert out["applied"]["dollars"] == 300
    assert out["applied"]["corruption"] == 3
    assert out["applied"]["reputation"] == {"order": -40}
    assert out["applied"]["stored"]["status"] == {"whispers_days": 3}
    assert quest(quests(player), "orden_glocke") is None  # one-time


def test_corruption_and_black_ore_from_shaft(player, db_sessionmaker, clock):
    sql(db_sessionmaker, "UPDATE characters SET region = 'deep_vein'")
    sql(db_sessionmaker, "INSERT INTO reputation VALUES (1, 'company', 500)")
    inst = start(player, "kompanie_stiller_schacht").json()
    clock.now += timedelta(hours=1)
    out = choose(player, inst["id"], 2).json()["outcome"]
    assert out["applied"]["resources"] == {"black_ore": 8}
    assert player.get("/me").json()["character"]["corruption"] == 6


def test_oath(player, db_sessionmaker):
    f = player.get("/factions").json()
    assert f["oath"] is None
    company = next(x for x in f["factions"] if x["code"] == "company")
    assert (company["cap"], company["can_swear"]) == (799, False)
    assert player.post("/factions/company/oath").json()["detail"]["code"] == "reputation_too_low"

    sql(db_sessionmaker, "INSERT INTO reputation VALUES (1, 'company', 700), (1, 'ash_gang', 600)")
    r = player.post("/factions/company/oath")
    assert r.status_code == 200 and r.json()["oath"] == "company"
    company = next(x for x in r.json()["factions"] if x["code"] == "company")
    assert company["cap"] == 1000

    r = player.post("/factions/ash_gang/oath").json()  # switching costs 50 % at the company
    assert r["oath"] == "ash_gang"
    assert next(x for x in r["factions"] if x["code"] == "company")["value"] == 350


def test_roof_step_completes_if_tent_already_built(player, clock, db_sessionmaker):
    for qid in ("onboarding_arrival", "onboarding_work"):
        sql(
            db_sessionmaker,
            "INSERT INTO quest_instances (character_id, quest_id, seed, state, day, data, "
            "started_at, finishes_at) "
            "VALUES (1, :q, 1, 'done', '2026-01-01', '{}', now(), now())",
            q=qid,
        )
    player.post("/settlement/build", json={"type": "main_house"})  # built by hand
    inst = start(player, "onboarding_roof").json()
    assert inst["state"] == "done"
    assert player.get("/me").json()["character"]["dollars"] == 50  # paid only once
    assert quest(quests(player), "onboarding_stranger")["available"]
