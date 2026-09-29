"""Scheduled events and the catch-up rule (docs/08-technik.md, "Zeit und Timer").

Every request that reads or changes a character first locks the character row
and processes its due events in order, each at its own `due_at`. The worker uses
the same code, so game state never depends on when the worker runs.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Character, ScheduledEvent

log = logging.getLogger(__name__)

Handler = Callable[[Session, Character, ScheduledEvent], None]
HANDLERS: dict[str, Handler] = {}


def handler(kind: str) -> Callable[[Handler], Handler]:
    def register(fn: Handler) -> Handler:
        HANDLERS[kind] = fn
        return fn

    return register


def schedule(
    db: Session, kind: str, due_at: datetime, now: datetime, character_id: int | None, **payload
) -> ScheduledEvent:
    event = ScheduledEvent(
        kind=kind,
        due_at=due_at,
        payload=payload,
        character_id=character_id,
        status="pending",
        created_at=now,
    )
    db.add(event)
    db.flush()
    return event


def lock_character(db: Session, character_id: int, skip_locked: bool = False) -> Character | None:
    stmt = select(Character).where(Character.id == character_id)
    stmt = stmt.with_for_update(skip_locked=skip_locked)
    return db.scalar(stmt.execution_options(populate_existing=True))


def process_due(db: Session, character: Character, now: datetime) -> int:
    """Run all due events of a locked character, oldest first. Returns the count."""
    # Imported for its side effect: registers the handlers
    from app.services import settlement  # noqa: F401

    events = db.scalars(
        select(ScheduledEvent)
        .where(
            ScheduledEvent.character_id == character.id,
            ScheduledEvent.status == "pending",
            ScheduledEvent.due_at <= now,
        )
        .order_by(ScheduledEvent.due_at, ScheduledEvent.id)
        .with_for_update()
    ).all()
    for event in events:
        fn = HANDLERS.get(event.kind)
        try:
            with db.begin_nested():
                if fn is None:
                    raise LookupError(f"no handler for {event.kind}")
                fn(db, character, event)
            event.status = "done"
        except Exception as e:  # one broken event must not block the character forever
            log.exception("event %s (%s) failed", event.id, event.kind)
            event.status = "failed"
            event.error = repr(e)[:2000]
        event.processed_at = now
    return len(events)


def sync(db: Session, character_id: int, now: datetime) -> Character:
    """Lock the character and catch up on its due events."""
    character = lock_character(db, character_id)
    if character is None:
        raise LookupError(f"character {character_id} not found")
    process_due(db, character, now)
    return character
