from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app import clock
from app.config import Settings, get_settings
from app.db import get_db
from app.models import User, UserSession
from app.services import auth
from app.services.ratelimit import limiter


def get_now() -> datetime:
    return clock.utcnow()


DbDep = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
NowDep = Annotated[datetime, Depends(get_now)]


def api_error(status_code: int, code: str) -> HTTPException:
    """Errors carry a stable English code; the client maps it to German text."""
    return HTTPException(status_code=status_code, detail={"code": code})


@dataclass
class CurrentSession:
    user: User
    session: UserSession
    token: str


def get_current_session(
    request: Request, db: DbDep, settings: SettingsDep, now: NowDep
) -> CurrentSession:
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        session = auth.resolve_session(db, token, now, settings)
        if session is not None:
            user = db.get(User, session.user_id)
            if user is not None:
                return CurrentSession(user=user, session=session, token=token)
    raise api_error(status.HTTP_401_UNAUTHORIZED, "not_authenticated")


CurrentSessionDep = Annotated[CurrentSession, Depends(get_current_session)]


def get_current_user(current: CurrentSessionDep) -> User:
    return current.user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def rate_limit(bucket: str, setting: str) -> Callable[..., None]:
    """Dependency limiting requests per client IP for one bucket."""

    def dependency(request: Request, settings: SettingsDep) -> None:
        ip = request.client.host if request.client else "unknown"
        limit = getattr(settings, setting)
        if not limiter.allow(f"{bucket}:{ip}", limit, settings.rate_limit_window_seconds):
            raise api_error(status.HTTP_429_TOO_MANY_REQUESTS, "rate_limited")

    return dependency
