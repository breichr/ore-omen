from __future__ import annotations

from pydantic import BaseModel

from app.game import constants as c
from app.game.character import duel_values, max_life
from app.models import Character


class CharacterOut(BaseModel):
    id: int
    name: str
    character_class: str
    level: int
    xp: int
    attributes: dict[str, int]
    unspent_attribute_points: int
    unspent_skill_points: int
    duel_values: dict[str, int]
    max_life: int
    dollars: int
    bank_dollars: int
    corruption: float
    region: str
    status: str


def character_out(ch: Character) -> CharacterOut:
    attributes = {a: getattr(ch, a) for a in c.ATTRIBUTES}
    values = duel_values(attributes)  # skills and equipment follow in M3
    return CharacterOut(
        id=ch.id,
        name=ch.name,
        character_class=ch.character_class,
        level=ch.level,
        xp=ch.xp,
        attributes=attributes,
        unspent_attribute_points=ch.unspent_attribute_points,
        unspent_skill_points=ch.unspent_skill_points,
        duel_values=values,
        max_life=max_life(values["toughness"]),
        dollars=ch.dollars,
        bank_dollars=ch.bank_dollars,
        corruption=ch.corruption_tenths / c.CORRUPTION_SCALE,
        region=ch.region,
        status=ch.status,
    )
