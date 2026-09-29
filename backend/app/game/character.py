"""Pure rules for characters (docs/01-welt.md, docs/04-duelle.md)."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

from app.game import constants as c

# Letters incl. umlauts, spaces, hyphen, apostrophe (docs/08-technik.md, "Auth")
_NAME_RE = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$")


class RuleError(ValueError):
    """A game rule rejected the input. `code` is stable for API clients."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code


def normalize_name(name: str) -> str:
    """Canonical display form: NFC, trimmed, inner whitespace collapsed."""
    return " ".join(unicodedata.normalize("NFC", name).split())


def name_key(name: str) -> str:
    """Key for the case-insensitive uniqueness check."""
    return normalize_name(name).casefold()


def validate_name(name: str) -> str:
    """Return the normalized name or raise RuleError."""
    n = normalize_name(name)
    if not c.CHARACTER_NAME_MIN_LEN <= len(n) <= c.CHARACTER_NAME_MAX_LEN:
        raise RuleError("name_length")
    if not _NAME_RE.match(n):
        raise RuleError("name_chars")
    return n


def validate_class(character_class: str) -> str:
    if character_class not in c.CLASSES:
        raise RuleError("unknown_class")
    return character_class


def starting_attributes(allocation: Mapping[str, int]) -> dict[str, int]:
    """Start values: every attribute 5, plus exactly 4 freely allocated points."""
    unknown = set(allocation) - set(c.ATTRIBUTES)
    if unknown:
        raise RuleError("unknown_attribute")
    if any(v < 0 for v in allocation.values()):
        raise RuleError("negative_points")
    if sum(allocation.values()) != c.ATTRIBUTE_START_FREE_POINTS:
        raise RuleError("points_not_spent")
    return {a: c.ATTRIBUTE_START_VALUE + allocation.get(a, 0) for a in c.ATTRIBUTES}


def skill_cap(level: int) -> int:
    return level + c.SKILL_CAP_OVER_LEVEL


def attribute_of_skill(skill: str) -> str:
    for attribute, skills in c.SKILLS_BY_ATTRIBUTE.items():
        if skill in skills:
            return attribute
    raise RuleError("unknown_skill")


def duel_value(skill_points: int, attribute: int, equipment_bonus: int = 0) -> int:
    """Duellwert = Skillpunkte + floor(Attribut / 2) + Ausrüstung."""
    return skill_points + attribute // 2 + equipment_bonus


def duel_values(
    attributes: Mapping[str, int],
    skills: Mapping[str, int] | None = None,
    equipment: Mapping[str, int] | None = None,
) -> dict[str, int]:
    skills = skills or {}
    equipment = equipment or {}
    return {
        s: duel_value(skills.get(s, 0), attributes[attribute_of_skill(s)], equipment.get(s, 0))
        for s in c.DUEL_SKILLS
    }


def max_life(toughness: int) -> int:
    """Leben = 40 + 4 × Zähigkeit."""
    return c.LIFE_BASE + c.LIFE_PER_TOUGHNESS * toughness


@dataclass(frozen=True)
class NewCharacter:
    name: str
    character_class: str
    attributes: dict[str, int]
    level: int
    unspent_attribute_points: int
    unspent_skill_points: int
    dollars: int
    region: str


def create_character(
    name: str, character_class: str, allocation: Mapping[str, int]
) -> NewCharacter:
    return NewCharacter(
        name=validate_name(name),
        character_class=validate_class(character_class),
        attributes=starting_attributes(allocation),
        level=c.START_LEVEL,
        unspent_attribute_points=0,
        unspent_skill_points=c.SKILL_START_POINTS,
        dollars=c.START_DOLLARS,
        region=c.START_REGION,
    )
