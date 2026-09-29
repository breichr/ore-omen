"""Game day: changes at 04:00 server time (docs/08-technik.md, "Zeit und Timer")."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.game import constants as c

_TZ = ZoneInfo(c.SERVER_TIMEZONE)


def game_day(moment: datetime) -> date:
    """The game day a UTC moment belongs to (DST-safe via zoneinfo)."""
    local = moment.astimezone(_TZ)
    return (local - timedelta(hours=c.DAILY_RESET_HOUR)).date()


def next_reset(moment: datetime) -> datetime:
    """UTC time of the next 04:00 in Vienna after `moment`."""
    day = game_day(moment) + timedelta(days=1)
    local = datetime(day.year, day.month, day.day, c.DAILY_RESET_HOUR, tzinfo=_TZ)
    return local.astimezone(moment.tzinfo)
