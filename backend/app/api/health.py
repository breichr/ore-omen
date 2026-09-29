from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbDep

router = APIRouter()


@router.get("/health")
def health(db: DbDep) -> JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse({"status": "error", "db": "unreachable"}, status_code=503)
    return JSONResponse({"status": "ok", "db": "ok"})
