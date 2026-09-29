from __future__ import annotations

from collections.abc import Mapping

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.game import character as rules
from app.models import Character, User


class CharacterExists(Exception):
    pass


class NameTaken(Exception):
    pass


def get_for_user(db: Session, user: User) -> Character | None:
    return db.scalar(select(Character).where(Character.user_id == user.id))


def create(
    db: Session, user: User, name: str, character_class: str, allocation: Mapping[str, int]
) -> Character:
    new = rules.create_character(name, character_class, allocation)
    if get_for_user(db, user) is not None:
        raise CharacterExists
    key = rules.name_key(new.name)
    if db.scalar(select(Character.id).where(Character.name_key == key)) is not None:
        raise NameTaken
    ch = Character(
        user_id=user.id,
        name=new.name,
        name_key=key,
        character_class=new.character_class,
        level=new.level,
        xp=0,
        **new.attributes,
        unspent_attribute_points=new.unspent_attribute_points,
        unspent_skill_points=new.unspent_skill_points,
        dollars=new.dollars,
        bank_dollars=0,
        corruption_tenths=0,
        region=new.region,
        status="idle",
    )
    db.add(ch)
    try:
        db.flush()
    except IntegrityError as e:  # concurrent insert
        db.rollback()
        if get_for_user(db, user) is not None:
            raise CharacterExists from e
        raise NameTaken from e
    return ch
