from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUserDep, DbDep, NowDep
from app.api.schemas import CharacterOut, character_out
from app.services import characters

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
    return MeOut(
        user=UserOut(username=user.username, timezone=user.timezone),
        character=character_out(ch) if ch else None,
        server_time=now.isoformat(),
    )
