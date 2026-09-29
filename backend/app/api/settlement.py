from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import content
from app.api.deps import CharacterDep, DbDep, NowDep, api_error, rate_limit
from app.game import buildings as bf
from app.game import constants as c
from app.game import storage
from app.game.character import RuleError
from app.game.jobs import job_yield
from app.models import Character
from app.services import settlement as svc

router = APIRouter(tags=["settlement"])
write = [Depends(rate_limit("write", "rate_limit_write"))]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ResourceOut(BaseModel):
    name: str
    amount_milli: int  # stock at `as_of`; the client may extrapolate with rate/capacity
    rate_per_hour: int


class NextLevel(BaseModel):
    level: int
    cost: dict[str, int]
    seconds: int


class BuildingOut(BaseModel):
    code: str
    category: str
    name: str
    description: str
    level: int
    variant: str | None  # main house: tent, hut, log_house, ranch_house, manor
    produces: dict[str, int]  # per hour at the current level
    next: NextLevel | None
    can_build: bool
    reason: str | None  # rule code why not


class QueueItemOut(BaseModel):
    id: int
    type: str
    target_level: int
    started_at: datetime
    finishes_at: datetime


class SettlementOut(BaseModel):
    as_of: datetime
    dollars: int
    capacity: int
    protected_share: float
    resources: list[ResourceOut]
    buildings: list[BuildingOut]
    queue: list[QueueItemOut]
    queue_slots: int
    lost: dict[str, int] = Field(default_factory=dict)  # after a cancel: what did not fit


class JobOut(BaseModel):
    code: str
    name: str
    description: str
    seconds: int
    yield_: dict[str, int] = Field(serialization_alias="yield")
    xp: int
    overflow: dict[str, int]  # would be lost right now because storage is full


class ActivityOut(BaseModel):
    id: int
    job: str
    started_at: datetime
    finishes_at: datetime
    status: str
    result: dict


class JobsOut(BaseModel):
    as_of: datetime
    current: ActivityOut | None
    last: ActivityOut | None
    jobs: list[JobOut]


class BuildIn(BaseModel):
    type: str = Field(max_length=32)


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


def settlement_view(db: Session, ch: Character, now: datetime) -> SettlementOut:
    lv = svc.levels(db, ch.id)
    items = svc.queue(db, ch.id)
    in_queue = [i.type for i in items]
    amounts = svc.amounts_at(db, ch.id, lv, now)
    whole = {k: storage.whole(v) for k, v in amounts.items()}
    r = svc.rates(lv)

    out: list[BuildingOut] = []
    for code, d in content.buildings().items():
        level = lv.get(code, 0)
        produces = {
            res: bf.production_per_hour(base, level)
            for res, base in d.produces.items()
            if level >= d.produces_from_level.get(res, 1)
        }
        nxt, reason = None, None
        if level < c.BUILDING_MAX_LEVEL:
            target = level + 1
            nxt = NextLevel(
                level=target,
                cost=bf.cost(d.cost, target, d.black_ore_per_level),
                seconds=bf.build_time_seconds(d.time_seconds, target, lv.get("main_house", 0)),
            )
        try:
            svc.plan_for(code, lv, in_queue, whole, ch.dollars)
        except RuleError as e:
            reason = e.code
        out.append(
            BuildingOut(
                code=code,
                category=d.category,
                name=d.name,
                description=d.description,
                level=level,
                variant=bf.main_house_name(level) if code == "main_house" and level else None,
                produces=produces,
                next=nxt,
                can_build=reason is None,
                reason=reason,
            )
        )
    storehouse = lv.get("storehouse", 0)
    return SettlementOut(
        as_of=now,
        dollars=ch.dollars,
        capacity=svc.capacity(lv),
        protected_share=float(bf.protected_share(storehouse)),
        resources=[
            ResourceOut(name=n, amount_milli=amounts[n], rate_per_hour=r.get(n, 0))
            for n in c.RESOURCES
        ],
        buildings=out,
        queue=[
            QueueItemOut(
                id=i.id,
                type=i.type,
                target_level=i.target_level,
                started_at=i.started_at,
                finishes_at=i.finishes_at,
            )
            for i in items
        ],
        queue_slots=bf.queue_slots(lv.get("main_house", 0)),
    )


def _activity(a) -> ActivityOut | None:
    if a is None:
        return None
    return ActivityOut(
        id=a.id,
        job=a.ref,
        started_at=a.started_at,
        finishes_at=a.finishes_at,
        status=a.status,
        result=a.data or {},
    )


def jobs_view(db: Session, ch: Character, now: datetime) -> JobsOut:
    lv = svc.levels(db, ch.id)
    amounts = svc.amounts_at(db, ch.id, lv, now)
    cap = svc.capacity(lv)
    jobs = []
    for code, j in content.jobs().items():
        y = job_yield(j.yield_, ch.level)
        resources = {k: v for k, v in y.items() if k != "dollars"}
        jobs.append(
            JobOut(
                code=code,
                name=j.name,
                description=j.description,
                seconds=j.seconds,
                yield_=y,
                xp=j.xp,
                overflow=storage.overflow(amounts, resources, cap),
            )
        )
    current = svc.running_job(db, ch.id)
    return JobsOut(
        as_of=now,
        current=_activity(current),
        last=None if current else _activity(svc.last_job(db, ch.id)),
        jobs=jobs,
    )


def _rule_error(e: RuleError):
    code = status.HTTP_404_NOT_FOUND if e.code == "not_found" else status.HTTP_409_CONFLICT
    return api_error(code, e.code)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/settlement", response_model_by_alias=True)
def get_settlement(ch: CharacterDep, db: DbDep, now: NowDep) -> SettlementOut:
    view = settlement_view(db, ch, now)
    db.commit()  # persist events processed while catching up
    return view


@router.post("/settlement/build", dependencies=write)
def build(body: BuildIn, ch: CharacterDep, db: DbDep, now: NowDep) -> SettlementOut:
    try:
        svc.start_build(db, ch, body.type, now)
    except RuleError as e:
        db.rollback()
        raise _rule_error(e) from None
    view = settlement_view(db, ch, now)
    db.commit()
    return view


@router.post("/settlement/queue/{item_id}/cancel", dependencies=write)
def cancel(item_id: int, ch: CharacterDep, db: DbDep, now: NowDep) -> SettlementOut:
    try:
        lost = svc.cancel_build(db, ch, item_id, now)
    except RuleError as e:
        db.rollback()
        raise _rule_error(e) from None
    view = settlement_view(db, ch, now)
    view.lost = lost
    db.commit()
    return view


@router.get("/jobs")
def get_jobs(ch: CharacterDep, db: DbDep, now: NowDep) -> JobsOut:
    view = jobs_view(db, ch, now)
    db.commit()
    return view


@router.post("/jobs/{code}/start", dependencies=write)
def start_job(code: str, ch: CharacterDep, db: DbDep, now: NowDep) -> JobsOut:
    try:
        svc.start_job(db, ch, code, now)
    except RuleError as e:
        db.rollback()
        raise _rule_error(e) from None
    view = jobs_view(db, ch, now)
    db.commit()
    return view


@router.post("/jobs/cancel", dependencies=write)
def cancel_job(ch: CharacterDep, db: DbDep, now: NowDep) -> JobsOut:
    try:
        svc.cancel_job(db, ch, now)
    except RuleError as e:
        db.rollback()
        raise _rule_error(e) from None
    view = jobs_view(db, ch, now)
    db.commit()
    return view
