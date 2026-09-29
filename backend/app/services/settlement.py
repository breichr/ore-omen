"""Settlement, resources, jobs and points: connects app/game with the database."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app import content
from app.game import buildings as bf
from app.game import constants as c
from app.game import storage
from app.game.character import RuleError
from app.game.jobs import job_yield
from app.game.progression import gain_xp, spend_points
from app.game.settlement import BuildPlan, plan_build
from app.models import (
    Activity,
    Building,
    BuildQueueItem,
    Character,
    CharacterSkill,
    Resource,
    ScheduledEvent,
)
from app.services.timeline import handler, schedule

# ---------------------------------------------------------------------------
# Reading state
# ---------------------------------------------------------------------------


def levels(db: Session, character_id: int) -> dict[str, int]:
    rows = db.scalars(select(Building).where(Building.character_id == character_id))
    return {b.type: b.level for b in rows}


def rates(lv: Mapping[str, int]) -> dict[str, int]:
    """Production per hour per resource for the given building levels."""
    result: dict[str, int] = {}
    for code, d in content.buildings().items():
        level = lv.get(code, 0)
        for res, base in d.produces.items():
            if level >= d.produces_from_level.get(res, 1):
                result[res] = result.get(res, 0) + bf.production_per_hour(base, level)
    return result


def capacity(lv: Mapping[str, int]) -> int:
    return bf.storage_capacity(lv.get("storehouse", 0))


def _rows(db: Session, character_id: int) -> dict[str, Resource]:
    rows = db.scalars(select(Resource).where(Resource.character_id == character_id))
    return {r.name: r for r in rows}


def _ms(delta: timedelta) -> int:
    return max(0, int(delta.total_seconds() * 1000))


def amounts_at(db: Session, character_id: int, lv: Mapping[str, int], t: datetime) -> dict:
    """Milli amounts at time t, computed lazily (nothing is written)."""
    r, cap = rates(lv), capacity(lv)
    rows = _rows(db, character_id)
    return {
        name: storage.current_milli(
            row.amount_milli if (row := rows.get(name)) else 0,
            r.get(name, 0),
            cap,
            _ms(t - row.updated_at) if row else 0,
        )
        for name in c.RESOURCES
    }


def write_amounts(db: Session, character_id: int, amounts: Mapping[str, int], t: datetime) -> None:
    rows = _rows(db, character_id)
    for name in c.RESOURCES:
        row = rows.get(name)
        if row is None:
            row = Resource(character_id=character_id, name=name)
            db.add(row)
        row.amount_milli = amounts.get(name, 0)
        row.updated_at = t


def snapshot(db: Session, character_id: int, lv: Mapping[str, int], t: datetime) -> dict:
    """Fix the stock at time t (before rates or amounts change)."""
    amounts = amounts_at(db, character_id, lv, t)
    write_amounts(db, character_id, amounts, t)
    return amounts


def init_resources(db: Session, character_id: int, now: datetime) -> None:
    start = {k: v * c.RESOURCE_SCALE for k, v in c.START_RESOURCES.items()}
    write_amounts(db, character_id, start, now)


def queue(db: Session, character_id: int) -> list[BuildQueueItem]:
    return list(
        db.scalars(
            select(BuildQueueItem)
            .where(BuildQueueItem.character_id == character_id)
            .order_by(BuildQueueItem.finishes_at)
        )
    )


def running_job(db: Session, character_id: int) -> Activity | None:
    return db.scalar(
        select(Activity).where(
            Activity.character_id == character_id,
            Activity.kind == "job",
            Activity.status == "running",
        )
    )


def last_job(db: Session, character_id: int) -> Activity | None:
    return db.scalar(
        select(Activity)
        .where(Activity.character_id == character_id, Activity.kind == "job")
        .order_by(Activity.finishes_at.desc(), Activity.id.desc())
        .limit(1)
    )


def skills(db: Session, character_id: int) -> dict[str, int]:
    rows = db.scalars(select(CharacterSkill).where(CharacterSkill.character_id == character_id))
    return {r.skill: r.points for r in rows}


# ---------------------------------------------------------------------------
# Building
# ---------------------------------------------------------------------------


def plan_for(
    code: str, lv: Mapping[str, int], in_queue: list[str], whole: Mapping[str, int], dollars: int
) -> BuildPlan:
    d = content.buildings().get(code)
    if d is None:
        raise RuleError("unknown_building")
    return plan_build(
        code,
        base_cost=d.cost,
        base_seconds=d.time_seconds,
        black_ore_per_level=d.black_ore_per_level,
        excludes=d.excludes,
        levels=lv,
        in_queue=in_queue,
        resources=whole,
        dollars=dollars,
    )


def start_build(db: Session, ch: Character, code: str, now: datetime) -> BuildQueueItem:
    lv = levels(db, ch.id)
    items = queue(db, ch.id)
    amounts = amounts_at(db, ch.id, lv, now)
    whole = {k: storage.whole(v) for k, v in amounts.items()}
    plan = plan_for(code, lv, [i.type for i in items], whole, ch.dollars)

    for res, amount in plan.cost.items():
        if res == "dollars":
            ch.dollars -= amount
        else:
            amounts[res] -= amount * c.RESOURCE_SCALE
    write_amounts(db, ch.id, amounts, now)

    finishes = now + timedelta(seconds=plan.seconds)
    event = schedule(db, "build_complete", finishes, now, ch.id, type=code, level=plan.target_level)
    item = BuildQueueItem(
        character_id=ch.id,
        type=code,
        target_level=plan.target_level,
        cost=plan.cost,
        started_at=now,
        finishes_at=finishes,
        event_id=event.id,
    )
    db.add(item)
    db.flush()
    return item


def cancel_build(db: Session, ch: Character, item_id: int, now: datetime) -> dict[str, int]:
    """Cancel a running build: 50 % refund, resources capped by storage. Returns what was lost."""
    item = db.get(BuildQueueItem, item_id)
    if item is None or item.character_id != ch.id:
        raise RuleError("not_found")
    lv = levels(db, ch.id)
    amounts = snapshot(db, ch.id, lv, now)
    refund = bf.cancel_refund(item.cost)
    ch.dollars += refund.pop("dollars", 0)
    added = storage.add_capped(amounts, refund, capacity(lv))
    write_amounts(db, ch.id, added.amounts_milli, now)
    event = db.get(ScheduledEvent, item.event_id)
    if event is not None:
        event.status = "cancelled"
        event.processed_at = now
    db.delete(item)
    return added.lost


@handler("build_complete")
def on_build_complete(db: Session, ch: Character, event: ScheduledEvent) -> None:
    item = db.scalar(select(BuildQueueItem).where(BuildQueueItem.event_id == event.id))
    if item is None:  # cancelled in the meantime
        return
    lv = levels(db, ch.id)
    # Production up to the moment of completion uses the old levels
    snapshot(db, ch.id, lv, event.due_at)
    building = db.get(Building, (ch.id, item.type))
    if building is None:
        db.add(Building(character_id=ch.id, type=item.type, level=item.target_level))
    else:
        building.level = item.target_level
    db.delete(item)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------


def start_job(db: Session, ch: Character, code: str, now: datetime) -> Activity:
    job = content.jobs().get(code)
    if job is None:
        raise RuleError("unknown_job")
    if running_job(db, ch.id) is not None:
        raise RuleError("job_running")
    finishes = now + timedelta(seconds=job.seconds)
    event = schedule(db, "job_complete", finishes, now, ch.id, job=code)
    activity = Activity(
        character_id=ch.id,
        kind="job",
        ref=code,
        data={},
        started_at=now,
        finishes_at=finishes,
        status="running",
        event_id=event.id,
    )
    db.add(activity)
    ch.status = "working"
    ch.status_until = finishes
    db.flush()
    return activity


def cancel_job(db: Session, ch: Character, now: datetime) -> None:
    activity = running_job(db, ch.id)
    if activity is None:
        raise RuleError("no_job_running")
    activity.status = "cancelled"
    activity.data = {"cancelled_at": now.isoformat()}
    if activity.event_id and (event := db.get(ScheduledEvent, activity.event_id)):
        event.status = "cancelled"
        event.processed_at = now
    ch.status = "idle"
    ch.status_until = None


@handler("job_complete")
def on_job_complete(db: Session, ch: Character, event: ScheduledEvent) -> None:
    activity = db.scalar(select(Activity).where(Activity.event_id == event.id))
    if activity is None or activity.status != "running":
        return
    job = content.jobs()[activity.ref]
    t = event.due_at
    lv = levels(db, ch.id)
    amounts = snapshot(db, ch.id, lv, t)
    gained = job_yield(job.yield_, ch.level)
    dollars = gained.pop("dollars", 0)
    added = storage.add_capped(amounts, gained, capacity(lv))
    write_amounts(db, ch.id, added.amounts_milli, t)
    ch.dollars += dollars
    up = gain_xp(ch.level, ch.xp, job.xp)
    ch.level, ch.xp = up.level, up.xp
    ch.unspent_attribute_points += up.attribute_points
    ch.unspent_skill_points += up.skill_points
    activity.status = "done"
    activity.data = {
        "yield": {**gained, **({"dollars": dollars} if dollars else {})},
        "lost": added.lost,
        "xp": job.xp,
        "levels_gained": up.levels_gained,
    }
    ch.status = "idle"
    ch.status_until = None


# ---------------------------------------------------------------------------
# Points
# ---------------------------------------------------------------------------


def spend(db: Session, ch: Character, add_attributes: dict, add_skills: dict) -> None:
    current = skills(db, ch.id)
    result = spend_points(
        ch.level,
        {a: getattr(ch, a) for a in c.ATTRIBUTES},
        current,
        ch.unspent_attribute_points,
        ch.unspent_skill_points,
        add_attributes,
        add_skills,
    )
    for a, v in result.attributes.items():
        setattr(ch, a, v)
    ch.unspent_attribute_points = result.unspent_attribute_points
    ch.unspent_skill_points = result.unspent_skill_points
    db.execute(delete(CharacterSkill).where(CharacterSkill.character_id == ch.id))
    for s, v in result.skills.items():
        db.add(CharacterSkill(character_id=ch.id, skill=s, points=v))
