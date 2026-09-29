from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import User, UserSession
from app.services.security import hash_password, hash_token, new_session_token, verify_password


class EmailTaken(Exception):
    pass


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register(db: Session, email: str, password: str) -> User:
    user = User(email=normalize_email(email), password_hash=hash_password(password))
    db.add(user)
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise EmailTaken from e
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    ok = verify_password(user.password_hash if user else None, password)
    return user if ok else None


def create_session(
    db: Session, user: User, now: datetime, settings: Settings, user_agent: str | None
) -> str:
    token = new_session_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_token(token),
            created_at=now,
            last_seen_at=now,
            expires_at=now + timedelta(days=settings.session_days),
            user_agent=(user_agent or "")[:255] or None,
        )
    )
    return token


def resolve_session(
    db: Session, token: str, now: datetime, settings: Settings
) -> UserSession | None:
    """Return the valid session for a token and slide its expiry forward."""
    session = db.scalar(select(UserSession).where(UserSession.token_hash == hash_token(token)))
    if session is None:
        return None
    if session.expires_at <= now:
        db.delete(session)
        db.commit()
        return None
    if now - session.last_seen_at >= timedelta(minutes=settings.session_touch_minutes):
        session.last_seen_at = now
        session.expires_at = now + timedelta(days=settings.session_days)
        db.commit()
    return session


def end_session(db: Session, token: str) -> None:
    db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
