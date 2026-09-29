from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, Field

from app.api.deps import (
    CurrentSessionDep,
    DbDep,
    NowDep,
    SettingsDep,
    api_error,
    rate_limit,
)
from app.config import Settings
from app.services import auth
from app.services.credentials import CredentialError

router = APIRouter(prefix="/auth", tags=["auth"])


class Credentials(BaseModel):
    # Rules are checked in app/services/credentials.py to return stable codes
    username: str = Field(max_length=64)
    password: str = Field(max_length=256)


class RecoverIn(BaseModel):
    username: str = Field(max_length=64)
    recovery_key: str = Field(max_length=64)
    new_password: str = Field(max_length=256)


class RecoveryKeyOut(BaseModel):
    """Returned exactly once; the server only keeps a hash."""

    recovery_key: str


def _set_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        settings.session_cookie_name,
        token,
        max_age=settings.session_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("register", "rate_limit_register"))],
)
def register(
    body: Credentials,
    request: Request,
    response: Response,
    db: DbDep,
    settings: SettingsDep,
    now: NowDep,
) -> RecoveryKeyOut:
    try:
        user, recovery_key = auth.register(db, body.username, body.password)
    except CredentialError as e:
        raise api_error(status.HTTP_422_UNPROCESSABLE_CONTENT, e.code) from None
    except auth.UsernameTaken:
        raise api_error(status.HTTP_409_CONFLICT, "username_taken") from None
    token = auth.create_session(db, user, now, settings, request.headers.get("user-agent"))
    db.commit()
    _set_cookie(response, token, settings)
    return RecoveryKeyOut(recovery_key=recovery_key)


@router.post("/login", dependencies=[Depends(rate_limit("login", "rate_limit_login"))])
def login(
    body: Credentials,
    request: Request,
    response: Response,
    db: DbDep,
    settings: SettingsDep,
    now: NowDep,
) -> dict:
    user = auth.authenticate(db, body.username, body.password)
    if user is None:
        raise api_error(status.HTTP_401_UNAUTHORIZED, "invalid_credentials")
    token = auth.create_session(db, user, now, settings, request.headers.get("user-agent"))
    db.commit()
    _set_cookie(response, token, settings)
    return {"ok": True}


@router.post("/recover", dependencies=[Depends(rate_limit("recover", "rate_limit_recover"))])
def recover(
    body: RecoverIn,
    request: Request,
    response: Response,
    db: DbDep,
    settings: SettingsDep,
    now: NowDep,
) -> RecoveryKeyOut:
    try:
        user, new_key = auth.recover(db, body.username, body.recovery_key, body.new_password)
    except CredentialError as e:
        code = status.HTTP_401_UNAUTHORIZED if e.code == "invalid_recovery" else 422
        raise api_error(code, e.code) from None
    token = auth.create_session(db, user, now, settings, request.headers.get("user-agent"))
    db.commit()
    _set_cookie(response, token, settings)
    return RecoveryKeyOut(recovery_key=new_key)


class PasswordIn(BaseModel):
    password: str = Field(max_length=256)


@router.post(
    "/recovery-key",
    dependencies=[Depends(rate_limit("rekey", "rate_limit_recover"))],
)
def rotate_recovery_key(body: PasswordIn, current: CurrentSessionDep, db: DbDep) -> RecoveryKeyOut:
    try:
        new_key = auth.rotate_recovery_key(db, current.user, body.password)
    except CredentialError as e:
        raise api_error(status.HTTP_401_UNAUTHORIZED, e.code) from None
    db.commit()
    return RecoveryKeyOut(recovery_key=new_key)


@router.post("/logout")
def logout(
    current: CurrentSessionDep, response: Response, db: DbDep, settings: SettingsDep
) -> dict:
    auth.end_session(db, current.token)
    db.commit()
    response.delete_cookie(
        settings.session_cookie_name,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )
    return {"ok": True}
