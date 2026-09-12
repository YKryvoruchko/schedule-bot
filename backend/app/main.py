from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, health, schedule
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("schedule_backend")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="University Schedule API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(schedule.router)
    app.include_router(admin.router)
    logger.info("backend startup timezone=%s", settings.timezone)
    return app


app = create_app()
