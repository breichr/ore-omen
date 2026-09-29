from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.deps import CharacterDep, CurrentUserDep, DbDep, NowDep, api_error, rate_limit
from app.api.schemas import CharacterOut, character_out
from app.game.character import RuleError
from app.services import characters, settlement, timeline

router = APIRouter(tags=["me"])


class UserOut(BaseModel):
    username: str
    timezone: str


class MeOut(BaseModel):
    user: UserOut
    character: CharacterOut | None
    server_time: str  # UTC ISO timestamp, lets the client correct its clock for countdowns


@router.get("/me")
def me(user: CurrentUserDep, db: DbDep, now: NowDep) -> MeOut:
    ch = characters.get_for_user(db, user)
    out = None
    if ch is not None:
        ch = timeline.sync(db, ch.id, now)
        out = character_out(ch, settlement.skills(db, ch.id))
        db.commit()
    return MeOut(
        user=UserOut(username=user.username, timezone=user.timezone),
        character=out,
        server_time=now.isoformat(),
    )


class PointsIn(BaseModel):
    attributes: dict[str, int] = Field(default_factory=dict, max_length=4)
    skills: dict[str, int] = Field(default_factory=dict, max_length=12)


@router.post("/me/points", dependencies=[Depends(rate_limit("write", "rate_limit_write"))])
def spend_points(body: PointsIn, ch: CharacterDep, db: DbDep) -> CharacterOut:
    try:
        settlement.spend(db, ch, body.attributes, body.skills)
    except RuleError as e:
        db.rollback()
        raise api_error(status.HTTP_422_UNPROCESSABLE_CONTENT, e.code) from None
    db.flush()
    out = character_out(ch, settlement.skills(db, ch.id))
    db.commit()
    return out
