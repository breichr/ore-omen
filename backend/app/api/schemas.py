from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel

from app.game import constants as c
from app.game.character import duel_values, max_life, skill_cap
from app.game.progression import total_xp_for_level
from app.models import Character


class CharacterOut(BaseModel):
    id: int
    name: str
    character_class: str
    level: int
    xp: int
    xp_level_start: int  # cumulative XP where the current level began
    xp_next_level: int  # cumulative XP needed for the next level
    attributes: dict[str, int]
    skills: dict[str, int]
    skill_cap: int
    unspent_attribute_points: int
    unspent_skill_points: int
    duel_values: dict[str, int]
    max_life: int
    dollars: int
    bank_dollars: int
    corruption: float
    region: str
    status: str


def character_out(ch: Character, skills: Mapping[str, int]) -> CharacterOut:
    attributes = {a: getattr(ch, a) for a in c.ATTRIBUTES}
    values = duel_values(attributes, skills)  # equipment follows in M3
    return CharacterOut(
        id=ch.id,
        name=ch.name,
        character_class=ch.character_class,
        level=ch.level,
        xp=ch.xp,
        xp_level_start=total_xp_for_level(ch.level),
        xp_next_level=total_xp_for_level(ch.level + 1),
        attributes=attributes,
        skills={s: skills.get(s, 0) for s in c.SKILLS},
        skill_cap=skill_cap(ch.level),
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
