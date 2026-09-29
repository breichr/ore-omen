from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import User, UserSession
from app.services import credentials
from app.services.security import hash_password, hash_token, new_session_token, verify_password


class UsernameTaken(Exception):
    pass


def register(db: Session, username: str, password: str) -> tuple[User, str]:
    """Create an account. Returns the user and the recovery key (shown once)."""
    name = credentials.validate_username(username)
    credentials.validate_password(password)
    recovery_key = credentials.new_recovery_key()
    user = User(
        username=name,
        username_key=credentials.username_key(name),
        password_hash=hash_password(password),
        recovery_key_hash=hash_password(credentials.normalize_recovery_key(recovery_key)),
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError as e:
        db.rollback()
        raise UsernameTaken from e
    return user, recovery_key


def find_user(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username_key == credentials.username_key(username)))


def authenticate(db: Session, username: str, password: str) -> User | None:
    user = find_user(db, username)
    ok = verify_password(user.password_hash if user else None, password)
    return user if ok else None


def recover(db: Session, username: str, recovery_key: str, new_password: str) -> tuple[User, str]:
    """Reset the password with the recovery key.

    Rotates the key, ends all sessions and returns the user and the new key.
    Raises CredentialError("invalid_recovery") on any mismatch.
    """
    credentials.validate_password(new_password)
    user = find_user(db, username)
    normalized = credentials.normalize_recovery_key(recovery_key) or ""
    # Always verify once, so unknown users and malformed keys take the same time
    ok = verify_password(user.recovery_key_hash if user else None, normalized)
    if not ok or user is None:
        raise credentials.CredentialError("invalid_recovery")
    new_key = credentials.new_recovery_key()
    user.password_hash = hash_password(new_password)
    user.recovery_key_hash = hash_password(credentials.normalize_recovery_key(new_key))
    db.execute(delete(UserSession).where(UserSession.user_id == user.id))
    return user, new_key


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
