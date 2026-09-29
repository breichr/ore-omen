from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, EmailStr, Field

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

router = APIRouter(prefix="/auth", tags=["auth"])

PASSWORD_MIN = 8
PASSWORD_MAX = 128


class Credentials(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX)


class LoginCredentials(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=PASSWORD_MAX)


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
) -> dict:
    try:
        user = auth.register(db, body.email, body.password)
    except auth.EmailTaken:
        raise api_error(status.HTTP_409_CONFLICT, "email_taken") from None
    token = auth.create_session(db, user, now, settings, request.headers.get("user-agent"))
    db.commit()
    _set_cookie(response, token, settings)
    return {"ok": True}


@router.post("/login", dependencies=[Depends(rate_limit("login", "rate_limit_login"))])
def login(
    body: LoginCredentials,
    request: Request,
    response: Response,
    db: DbDep,
    settings: SettingsDep,
    now: NowDep,
) -> dict:
    user = auth.authenticate(db, body.email, body.password)
    if user is None:
        raise api_error(status.HTTP_401_UNAUTHORIZED, "invalid_credentials")
    token = auth.create_session(db, user, now, settings, request.headers.get("user-agent"))
    db.commit()
    _set_cookie(response, token, settings)
    return {"ok": True}


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
