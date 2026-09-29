from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import content
from app.api.deps import CharacterDep, DbDep, NowDep, api_error, rate_limit
from app.game import constants as c
from app.game import reputation as rep
from app.game.character import RuleError
from app.game.checks import percent
from app.game.gameday import game_day, next_reset
from app.game.quests import blocked, chance
from app.models import Activity, Character, QuestInstance
from app.services import quests as svc
from app.services import settlement

router = APIRouter(tags=["quests"])
write = [Depends(rate_limit("write", "rate_limit_write"))]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ActivityOut(BaseModel):
    kind: str  # job | quest | travel | delay
    ref: str
    started_at: datetime
    finishes_at: datetime


class QuestOut(BaseModel):
    id: str
    type: str
    chain: str | None
    faction: str | None
    region: str
    duration_min: int
    title: str
    intro: str
    min_reputation: int | None
    available: bool
    reason: str | None


class InstanceSummary(BaseModel):
    id: int
    quest_id: str
    title: str
    state: str
    finishes_at: datetime


class TravelOption(BaseModel):
    region: str
    seconds: int | None
    reason: str | None


class QuestsOut(BaseModel):
    as_of: datetime
    region: str
    day: str
    next_reset: datetime
    activity: ActivityOut | None
    open: list[InstanceSummary]  # waiting for arrival or a choice
    quests: list[QuestOut]
    travel: list[TravelOption]


class OptionOut(BaseModel):
    index: int
    label: str
    chance: int | None  # percent, if there is a check
    check: dict | None  # attribute, skill, difficulty
    combat: bool
    blocked: str | None


class InstanceOut(BaseModel):
    id: int
    quest_id: str
    title: str
    intro: str
    event: str | None
    state: str
    started_at: datetime
    finishes_at: datetime
    options: list[OptionOut]
    outcome: dict | None


class ChooseIn(BaseModel):
    option: int = Field(ge=0, le=10)


class TravelIn(BaseModel):
    region: str = Field(max_length=32)


class FactionOut(BaseModel):
    code: str
    value: int
    tier: str
    cap: int
    can_swear: bool


class FactionsOut(BaseModel):
    oath: str | None
    factions: list[FactionOut]


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


def _activity(a: Activity | None) -> ActivityOut | None:
    if a is None:
        return None
    return ActivityOut(kind=a.kind, ref=a.ref, started_at=a.started_at, finishes_at=a.finishes_at)


def quests_view(db: Session, ch: Character, now: datetime) -> QuestsOut:
    quests = [
        QuestOut(
            id=s.quest["id"],
            type=s.quest["type"],
            chain=s.quest.get("chain"),
            faction=s.quest.get("faction"),
            region=s.quest["region"],
            duration_min=s.quest["duration_min"],
            title=s.quest["title"],
            intro=s.quest["intro"],
            min_reputation=s.quest.get("min_reputation"),
            available=s.available,
            reason=s.reason,
        )
        for s in svc.statuses(db, ch, now)
    ]
    open_ = [
        InstanceSummary(
            id=i.id,
            quest_id=i.quest_id,
            title=content.quests()[i.quest_id]["title"],
            state=i.state,
            finishes_at=i.finishes_at,
        )
        for i in svc.instances(db, ch.id)
        if i.state != "done"
    ]
    travel = []
    for region in c.REGIONS:
        if region == ch.region:
            continue
        try:
            travel.append(
                TravelOption(region=region, seconds=svc.travel_time(db, ch, region), reason=None)
            )
        except RuleError as e:
            travel.append(TravelOption(region=region, seconds=None, reason=e.code))
    return QuestsOut(
        as_of=now,
        region=ch.region,
        day=game_day(now).isoformat(),
        next_reset=next_reset(now),
        activity=_activity(settlement.running_activity(db, ch.id)),
        open=open_,
        quests=quests,
        travel=travel,
    )


def instance_view(db: Session, ch: Character, instance: QuestInstance) -> InstanceOut:
    q = content.quests()[instance.quest_id]
    options: list[OptionOut] = []
    if instance.state == "choice":
        ctx = svc.context(db, ch)
        for i, opt in enumerate(q.get("options") or []):
            ch_ = chance(opt, ctx)
            options.append(
                OptionOut(
                    index=i,
                    label=opt["label"],
                    chance=percent(ch_) if ch_ is not None else None,
                    check=opt.get("check"),
                    combat="combat" in opt,
                    blocked=blocked(opt, ctx),
                )
            )
    return InstanceOut(
        id=instance.id,
        quest_id=instance.quest_id,
        title=q["title"],
        intro=q["intro"],
        event=q.get("event") if instance.state != "traveling" else None,
        state=instance.state,
        started_at=instance.started_at,
        finishes_at=instance.finishes_at,
        options=options,
        outcome=(instance.data or {}).get("outcome"),
    )


def factions_view(db: Session, ch: Character) -> FactionsOut:
    values = svc.reputations(db, ch.id)
    oath = svc.oath_of(db, ch.id)
    out = []
    for f in c.FACTIONS:
        can = f in c.OATH_FACTIONS and oath != f and values[f] >= c.OATH_MIN_REPUTATION
        out.append(
            FactionOut(
                code=f,
                value=values[f],
                tier=rep.tier(values[f]),
                cap=rep.cap(f, svc.corruption(ch), oath),
                can_swear=can,
            )
        )
    return FactionsOut(oath=oath, factions=out)


def _err(e: RuleError):
    code = status.HTTP_404_NOT_FOUND if e.code in ("not_found", "unknown_quest") else 409
    return api_error(code, e.code)


def _instance(db: Session, ch: Character, instance_id: int) -> QuestInstance:
    instance = db.get(QuestInstance, instance_id)
    if instance is None or instance.character_id != ch.id:
        raise api_error(status.HTTP_404_NOT_FOUND, "not_found")
    return instance


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/quests")
def get_quests(ch: CharacterDep, db: DbDep, now: NowDep) -> QuestsOut:
    view = quests_view(db, ch, now)
    db.commit()
    return view


@router.post("/quests/{quest_id}/start", dependencies=write)
def start_quest(quest_id: str, ch: CharacterDep, db: DbDep, now: NowDep) -> InstanceOut:
    try:
        instance = svc.start(db, ch, quest_id, now)
    except RuleError as e:
        db.rollback()
        raise _err(e) from None
    view = instance_view(db, ch, instance)
    db.commit()
    return view


@router.get("/quests/instances/{instance_id}")
def get_instance(instance_id: int, ch: CharacterDep, db: DbDep) -> InstanceOut:
    view = instance_view(db, ch, _instance(db, ch, instance_id))
    db.commit()
    return view


@router.post("/quests/instances/{instance_id}/choose", dependencies=write)
def choose(
    instance_id: int, body: ChooseIn, ch: CharacterDep, db: DbDep, now: NowDep
) -> InstanceOut:
    try:
        instance = svc.choose(db, ch, instance_id, body.option, now)
    except RuleError as e:
        db.rollback()
        raise _err(e) from None
    view = instance_view(db, ch, instance)
    db.commit()
    return view


@router.post("/travel", dependencies=write)
def travel(body: TravelIn, ch: CharacterDep, db: DbDep, now: NowDep) -> QuestsOut:
    try:
        svc.travel(db, ch, body.region, now)
    except RuleError as e:
        db.rollback()
        raise _err(e) from None
    view = quests_view(db, ch, now)
    db.commit()
    return view


@router.get("/factions")
def get_factions(ch: CharacterDep, db: DbDep) -> FactionsOut:
    view = factions_view(db, ch)
    db.commit()
    return view


@router.post("/factions/{faction}/oath", dependencies=write)
def swear(faction: str, ch: CharacterDep, db: DbDep, now: NowDep) -> FactionsOut:
    try:
        svc.swear_oath(db, ch, faction, now)
    except RuleError as e:
        db.rollback()
        raise _err(e) from None
    db.flush()
    view = factions_view(db, ch)
    db.commit()
    return view
