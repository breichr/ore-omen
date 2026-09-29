"""Quests, reputation, travel and effects: connects app/game with the database."""

from __future__ import annotations

import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import content
from app.game import constants as c
from app.game import quests as rules
from app.game import reputation as rep
from app.game import storage
from app.game.character import RuleError
from app.game.gameday import game_day
from app.game.jobs import job_yield
from app.game.progression import gain_xp
from app.game.rounding import round_half_up
from app.game.travel import travel_seconds
from app.models import (
    Activity,
    Building,
    Character,
    CharacterFlag,
    Item,
    Oath,
    QuestInstance,
    Reputation,
    ScheduledEvent,
)
from app.services import settlement
from app.services.timeline import handler, schedule

STORED_ONLY = ("combat", "status", "bounty", "server_flag")

# ---------------------------------------------------------------------------
# Reputation, items, flags
# ---------------------------------------------------------------------------


def reputations(db: Session, character_id: int) -> dict[str, int]:
    rows = db.scalars(select(Reputation).where(Reputation.character_id == character_id))
    values = {f: c.REPUTATION_START for f in c.FACTIONS}
    values.update({r.faction: r.value for r in rows})
    return values


def write_reputations(db: Session, character_id: int, values: Mapping[str, int]) -> None:
    rows = {
        r.faction: r
        for r in db.scalars(select(Reputation).where(Reputation.character_id == character_id))
    }
    for faction, value in values.items():
        if faction in rows:
            rows[faction].value = value
        else:
            db.add(Reputation(character_id=character_id, faction=faction, value=value))


def oath_of(db: Session, character_id: int) -> str | None:
    row = db.get(Oath, character_id)
    return row.faction if row else None


def item_codes(db: Session, character_id: int) -> list[str]:
    return list(db.scalars(select(Item.item_id).where(Item.character_id == character_id)))


def corruption(ch: Character) -> float:
    return ch.corruption_tenths / c.CORRUPTION_SCALE


def context(db: Session, ch: Character) -> rules.Context:
    return rules.Context(
        character_class=ch.character_class,
        corruption=corruption(ch),
        items=set(item_codes(db, ch.id)),
        reputation=reputations(db, ch.id),
        dollars=ch.dollars,
        attributes={a: getattr(ch, a) for a in c.ATTRIBUTES},
        skills=settlement.skills(db, ch.id),
    )


# ---------------------------------------------------------------------------
# Effects (docs/07-auftraege.md, "Effekt-Schlüssel")
# ---------------------------------------------------------------------------


def apply_effects(db: Session, ch: Character, effects: Mapping, now: datetime, source: str) -> dict:
    """Apply quest effects and return what actually changed (for the outcome screen)."""
    applied: dict = {}

    if d := effects.get("dollars"):
        before = ch.dollars
        ch.dollars = max(0, ch.dollars + d)
        applied["dollars"] = ch.dollars - before

    if res := effects.get("resources"):
        lv = settlement.levels(db, ch.id)
        amounts = settlement.snapshot(db, ch.id, lv, now)
        gains = {k: v for k, v in res.items() if v > 0}
        added = storage.add_capped(amounts, gains, settlement.capacity(lv))
        amounts = added.amounts_milli
        for k, v in res.items():
            if v < 0:
                amounts[k] = max(0, amounts.get(k, 0) + v * c.RESOURCE_SCALE)
        settlement.write_amounts(db, ch.id, amounts, now)
        applied["resources"] = {k: v - added.lost.get(k, 0) for k, v in res.items()}
        if added.lost:
            applied["lost"] = added.lost

    if xp := effects.get("xp"):
        up = gain_xp(ch.level, ch.xp, xp)
        ch.level, ch.xp = up.level, up.xp
        ch.unspent_attribute_points += up.attribute_points
        ch.unspent_skill_points += up.skill_points
        applied["xp"] = xp
        if up.levels_gained:
            applied["levels_gained"] = up.levels_gained

    corruption_changed = False
    if (cor := effects.get("corruption")) is not None:
        before = ch.corruption_tenths
        tenths = round_half_up(cor * c.CORRUPTION_SCALE)
        ch.corruption_tenths = max(0, min(c.CORRUPTION_MAX * c.CORRUPTION_SCALE, before + tenths))
        applied["corruption"] = (ch.corruption_tenths - before) / c.CORRUPTION_SCALE
        corruption_changed = True

    direct = effects.get("reputation") or {}
    if direct or corruption_changed:
        values = reputations(db, ch.id)
        change = rep.apply(values, direct, corruption(ch), oath_of(db, ch.id))
        write_reputations(db, ch.id, change.values)
        if change.deltas:
            applied["reputation"] = change.deltas

    for item_id in effects.get("items") or []:
        db.add(Item(character_id=ch.id, item_id=item_id, equipped=False, acquired_at=now))
        applied.setdefault("items", []).append(item_id)

    for key in [*(effects.get("unlock") or []), *([effects["next"]] if "next" in effects else [])]:
        _flag(db, ch, "unlock", key, {}, now, source)
        applied.setdefault("unlock", []).append(key)

    for kind in STORED_ONLY:
        if kind in effects:
            value = effects[kind]
            if kind == "combat":
                value = {"enemy": value, "result": "lost"}  # until M3
            key = next(iter(value)) if kind in ("status", "server_flag") and value else kind
            _flag(
                db,
                ch,
                kind,
                key,
                value if isinstance(value, dict) else {"value": value},
                now,
                source,
            )
            applied.setdefault("stored", {})[kind] = value

    if delay := effects.get("delay_min"):
        _start_activity(db, ch, "delay", source, now, now + timedelta(minutes=delay), "busy")
        applied["delay_min"] = delay

    return applied


def _flag(db, ch, kind, key, value, now, source) -> None:
    db.add(
        CharacterFlag(
            character_id=ch.id, kind=kind, key=key, value=value, created_at=now, source=source
        )
    )


# ---------------------------------------------------------------------------
# Activities (one at a time: job, quest, travel, delay)
# ---------------------------------------------------------------------------


def _start_activity(
    db: Session,
    ch: Character,
    kind: str,
    ref: str,
    now: datetime,
    finishes: datetime,
    status: str,
    data: dict | None = None,
) -> Activity:
    event = schedule(db, "activity_end", finishes, now, ch.id)
    activity = Activity(
        character_id=ch.id,
        kind=kind,
        ref=ref,
        data=data or {},
        started_at=now,
        finishes_at=finishes,
        status="running",
        event_id=event.id,
    )
    db.add(activity)
    event.payload = {"kind": kind}
    ch.status = status
    ch.status_until = finishes
    db.flush()
    return activity


def ensure_idle(db: Session, ch: Character) -> None:
    if settlement.running_activity(db, ch.id) is not None:
        raise RuleError("busy")


@handler("activity_end")
def on_activity_end(db: Session, ch: Character, event: ScheduledEvent) -> None:
    activity = db.scalar(select(Activity).where(Activity.event_id == event.id))
    if activity is None or activity.status != "running":
        return
    activity.status = "done"
    if activity.kind == "travel":
        ch.region = activity.ref
    elif activity.kind == "quest":
        instance = db.get(QuestInstance, activity.data["instance_id"])
        if instance is not None and instance.state == "traveling":
            arrive(db, ch, instance, event.due_at)
    ch.status = "idle"
    ch.status_until = None


# ---------------------------------------------------------------------------
# Quests
# ---------------------------------------------------------------------------


@dataclass
class QuestStatus:
    quest: dict
    available: bool
    reason: str | None  # rule code why not


def instances(db: Session, character_id: int) -> list[QuestInstance]:
    return list(
        db.scalars(
            select(QuestInstance)
            .where(QuestInstance.character_id == character_id)
            .order_by(QuestInstance.started_at.desc(), QuestInstance.id.desc())
        )
    )


def daily_offers(character_id: int, now: datetime) -> set[str]:
    pools: dict[str, list[str]] = {}
    for qid, q in content.quests().items():
        if q["type"] == "daily":
            pools.setdefault(q["faction"], []).append(qid)
    today = game_day(now)
    offered: set[str] = set()
    for faction, pool in pools.items():
        offered.update(rules.daily_offer(pool, character_id, today, faction))
    return offered


def statuses(db: Session, ch: Character, now: datetime) -> list[QuestStatus]:
    """Every quest the player can see, with the reason if it cannot be started now."""
    all_instances = instances(db, ch.id)
    done = {i.quest_id for i in all_instances if i.state == "done"}
    open_ = {i.quest_id for i in all_instances if i.state != "done"}
    today = game_day(now)
    done_today = {i.quest_id for i in all_instances if i.day == today and i.state == "done"}
    offered = daily_offers(ch.id, now)
    values = reputations(db, ch.id)
    busy = settlement.running_activity(db, ch.id) is not None

    result: list[QuestStatus] = []
    for qid, q in content.quests().items():
        if q["type"] == "daily":
            if qid not in offered:
                continue
            reason = "done_today" if qid in done_today else None
        else:
            if qid in done:
                continue
            if "after" in q and q["after"] not in done:
                continue  # hidden until the previous step is done
            reason = None
            if q.get("faction") and values.get(q["faction"], 0) < q.get("min_reputation", -1000):
                reason = "reputation_too_low"
        if reason is None and qid in open_:
            reason = "in_progress"
        if reason is None and q["region"] != ch.region:
            reason = "wrong_region"
        if reason is None and busy:
            reason = "busy"
        result.append(QuestStatus(q, reason is None, reason))
    return result


def start(db: Session, ch: Character, quest_id: str, now: datetime) -> QuestInstance:
    q = content.quests().get(quest_id)
    if q is None:
        raise RuleError("unknown_quest")
    status = next((s for s in statuses(db, ch, now) if s.quest["id"] == quest_id), None)
    if status is None:
        raise RuleError("not_available")
    if not status.available:
        raise RuleError(status.reason or "not_available")

    task = q.get("task") or {}
    data: dict = {}
    if "build" in task:
        data["build"] = _pay_task_build(db, ch, task["build"], now)

    finishes = now + timedelta(minutes=q["duration_min"])
    instance = QuestInstance(
        character_id=ch.id,
        quest_id=quest_id,
        seed=secrets.randbits(62),
        state="traveling",
        day=game_day(now),
        data=data,
        started_at=now,
        finishes_at=finishes,
    )
    db.add(instance)
    db.flush()
    if q["duration_min"] == 0:
        arrive(db, ch, instance, now)
    else:
        _start_activity(
            db, ch, "quest", quest_id, now, finishes, "questing", {"instance_id": instance.id}
        )
    return instance


def _pay_task_build(db: Session, ch: Character, code: str, now: datetime) -> dict:
    """Onboarding build task: pay like a normal build; the level comes on arrival."""
    lv = settlement.levels(db, ch.id)
    items = settlement.queue(db, ch.id)
    amounts = settlement.amounts_at(db, ch.id, lv, now)
    whole = {k: storage.whole(v) for k, v in amounts.items()}
    plan = settlement.plan_for(code, lv, [i.type for i in items], whole, ch.dollars)
    for res, amount in plan.cost.items():
        if res == "dollars":
            ch.dollars -= amount
        else:
            amounts[res] -= amount * c.RESOURCE_SCALE
    settlement.write_amounts(db, ch.id, amounts, now)
    return {"type": code, "level": plan.target_level, "cost": plan.cost}


def arrive(db: Session, ch: Character, instance: QuestInstance, at: datetime) -> None:
    """End of the "Unterwegs" timer: show the event, or resolve task / direct outcome."""
    q = content.quests()[instance.quest_id]
    if q.get("options"):
        instance.state = "choice"
        return
    task = q.get("task") or {}
    effects: dict = dict(q.get("effects") or {})
    if "job" in task:
        job = content.jobs()[task["job"]]
        effects.update({"xp": effects.get("xp", 0) + job.xp})
        gained = job_yield(job.yield_, ch.level)
        if d := gained.pop("dollars", 0):
            effects["dollars"] = effects.get("dollars", 0) + d
        if gained:
            effects["resources"] = gained
    applied = apply_effects(db, ch, effects, at, instance.quest_id)
    if "build" in instance.data:
        b = instance.data["build"]
        lv = settlement.levels(db, ch.id)
        settlement.snapshot(db, ch.id, lv, at)
        row = db.get(Building, (ch.id, b["type"]))
        if row is None:
            db.add(Building(character_id=ch.id, type=b["type"], level=b["level"]))
        elif row.level < b["level"]:
            row.level = b["level"]
        applied["built"] = {b["type"]: b["level"]}
    instance.state = "done"
    instance.data = {**instance.data, "outcome": {"text": q.get("text", ""), "applied": applied}}


def choose(
    db: Session, ch: Character, instance_id: int, index: int, now: datetime
) -> QuestInstance:
    instance = db.get(QuestInstance, instance_id)
    if instance is None or instance.character_id != ch.id:
        raise RuleError("not_found")
    if instance.state != "choice":
        raise RuleError("no_choice_pending")
    q = content.quests()[instance.quest_id]
    options = q["options"]
    if not 0 <= index < len(options):
        raise RuleError("unknown_option")
    option = options[index]
    outcome = rules.resolve(option, index, instance.seed, context(db, ch))
    applied = apply_effects(db, ch, outcome.effects, now, instance.quest_id)
    check = None
    if outcome.check:
        check = {
            "roll": outcome.check.roll,
            "total": outcome.check.total,
            "difficulty": outcome.check.difficulty,
        }
    instance.state = "done"
    instance.data = {
        **instance.data,
        "outcome": {
            "option": index,
            "label": option["label"],
            "text": outcome.text,
            "success": outcome.success,
            "check": check,
            "applied": applied,
        },
    }
    return instance


# ---------------------------------------------------------------------------
# Travel and oath
# ---------------------------------------------------------------------------


def travel_time(db: Session, ch: Character, destination: str) -> int:
    lv = settlement.levels(db, ch.id)
    return travel_seconds(
        ch.region, destination, lv.get("map_room", 0), reputations(db, ch.id)["keepers"]
    )


def travel(db: Session, ch: Character, destination: str, now: datetime) -> Activity:
    seconds = travel_time(db, ch, destination)
    ensure_idle(db, ch)
    return _start_activity(
        db,
        ch,
        "travel",
        destination,
        now,
        now + timedelta(seconds=seconds),
        "traveling",
        {"from": ch.region},
    )


def swear_oath(db: Session, ch: Character, faction: str, now: datetime) -> int:
    values = reputations(db, ch.id)
    current = db.get(Oath, ch.id)
    result = rep.swear(values, current.faction if current else None, faction)
    if current is None:
        db.add(Oath(character_id=ch.id, faction=faction, sworn_at=now))
    else:
        current.faction = faction
        current.sworn_at = now
    # Apply the new caps right away (the abandoned side drops to 799 at most)
    capped = rep.apply(result.values, {}, corruption(ch), faction)
    write_reputations(db, ch.id, capped.values)
    return result.lost
