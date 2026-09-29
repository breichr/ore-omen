"""Worker process: processes due scheduled events (docs/08-technik.md).

Uses the same catch-up code as the API (app/services/timeline.py): per character
with due events, lock the character row with FOR UPDATE SKIP LOCKED and process
its events in order. Characters locked by a request or another worker are skipped
and picked up on the next tick.
"""

from __future__ import annotations

import logging
import signal
import time
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app import clock
from app.config import get_settings
from app.db import get_sessionmaker
from app.models import ScheduledEvent
from app.services import timeline

log = logging.getLogger("worker")
_running = True


def _stop(*_: object) -> None:
    global _running
    _running = False


def tick(
    now: datetime | None = None, batch: int = 100, sessions: sessionmaker[Session] | None = None
) -> int:
    """Process due events; returns the number processed."""
    now = now or clock.utcnow()
    processed = 0
    with (sessions or get_sessionmaker())() as db:
        character_ids = db.scalars(
            select(ScheduledEvent.character_id)
            .where(
                ScheduledEvent.status == "pending",
                ScheduledEvent.due_at <= now,
                ScheduledEvent.character_id.is_not(None),
            )
            .group_by(ScheduledEvent.character_id)
            .order_by(func.min(ScheduledEvent.due_at))
            .limit(batch)
        ).all()
        for character_id in character_ids:
            try:
                character = timeline.lock_character(db, character_id, skip_locked=True)
                if character is not None:
                    processed += timeline.process_due(db, character, now)
                db.commit()
            except Exception:
                db.rollback()
                log.exception("processing character %s failed", character_id)
    return processed


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    settings = get_settings()
    log.info("worker started, polling every %.1fs", settings.worker_poll_seconds)
    while _running:
        try:
            if n := tick():
                log.info("processed %d events", n)
        except Exception:
            log.exception("tick failed")
        time.sleep(settings.worker_poll_seconds)
    log.info("worker stopped")


if __name__ == "__main__":
    main()
