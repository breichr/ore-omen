from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from app.api.deps import CurrentUserDep, DbDep, NowDep, api_error, rate_limit
from app.api.schemas import CharacterOut, character_out
from app.game.character import RuleError
from app.services import characters

router = APIRouter(prefix="/characters", tags=["characters"])


class CharacterIn(BaseModel):
    name: str = Field(max_length=64)
    character_class: str = Field(alias="class", max_length=32)
    # Freely allocated start points on top of 5 per attribute (must sum to 4)
    allocation: dict[str, int] = Field(max_length=4)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("write", "rate_limit_write"))],
)
def create_character(
    body: CharacterIn, user: CurrentUserDep, db: DbDep, now: NowDep
) -> CharacterOut:
    try:
        ch = characters.create(db, user, body.name, body.character_class, body.allocation, now)
    except RuleError as e:
        raise api_error(status.HTTP_422_UNPROCESSABLE_CONTENT, e.code) from None
    except characters.CharacterExists:
        raise api_error(status.HTTP_409_CONFLICT, "character_exists") from None
    except characters.NameTaken:
        raise api_error(status.HTTP_409_CONFLICT, "name_taken") from None
    db.commit()
    return character_out(ch, {})
