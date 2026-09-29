from __future__ import annotations

from fastapi import FastAPI

from app.api import auth, characters, health, me, quests, settlement


def create_app() -> FastAPI:
    app = FastAPI(title="Ore & Omen API", version="0.1.0")
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(me.router)
    app.include_router(characters.router)
    app.include_router(settlement.router)
    app.include_router(quests.router)
    return app


app = create_app()
