from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import SessionSigner
from app.db.session import get_session


def get_app_settings() -> Settings:
    return get_settings()


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


def require_admin(
    admin_session: str | None = Cookie(default=None),
    settings: Settings = Depends(get_app_settings),
) -> str:
    if not admin_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    username = SessionSigner(settings.secret_key).verify(admin_session)
    if username != settings.admin_username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return username
