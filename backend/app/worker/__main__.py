"""Worker process: processes due scheduled events.

M0 only runs the loop and checks the database. The scheduled_events table and
the handler registry follow in M1.
"""

from __future__ import annotations

import logging
import signal
import time

from sqlalchemy import text

from app.config import get_settings
from app.db import get_engine

log = logging.getLogger("worker")
_running = True


def _stop(*_: object) -> None:
    global _running
    _running = False


def tick() -> int:
    """Process due events; returns the number processed."""
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return 0


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    settings = get_settings()
    log.info("worker started, polling every %.1fs", settings.worker_poll_seconds)
    while _running:
        try:
            tick()
        except Exception:
            log.exception("tick failed")
        time.sleep(settings.worker_poll_seconds)
    log.info("worker stopped")


if __name__ == "__main__":
    main()
