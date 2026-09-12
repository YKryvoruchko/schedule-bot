from __future__ import annotations

import json
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_app_settings, get_db, require_admin
from app.core.config import Settings
from app.core.security import SessionSigner, verify_password
from app.models import ScheduleEntry, ScheduleImport, ScheduleVersion
from app.schemas.schedule import ImportOut, ImportPreviewOut, LoginIn, VersionOut
from app.services.import_service import ImportService, import_to_dict

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/login")
async def login(payload: LoginIn, response: Response, settings: Settings = Depends(get_app_settings)) -> dict[str, str]:
    if payload.username != settings.admin_username or not verify_password(payload.password, settings.admin_password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    response.set_cookie(
        "admin_session",
        SessionSigner(settings.secret_key).sign(payload.username),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 12,
    )
    return {"status": "ok"}


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("admin_session")
    return {"status": "ok"}


@router.post("/import", response_model=ImportOut)
async def import_docx(
    _: str = Depends(require_admin),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
):
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are accepted.")
    payload = await file.read(settings.max_upload_bytes + 1)
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    record = await ImportService(session, settings).create_import(file.filename, __import__("pathlib").Path(tmp_path))
    return import_to_dict(record)


@router.get("/import/{import_id}", response_model=ImportOut)
async def get_import(import_id: int, _: str = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    record = await session.get(ScheduleImport, import_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Import not found")
    return import_to_dict(record)


@router.get("/import/{import_id}/preview", response_model=ImportPreviewOut)
async def get_preview(import_id: int, _: str = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    record = await session.get(ScheduleImport, import_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Import not found")
    return {**import_to_dict(record), "preview": json.loads(record.preview or "[]")}


@router.post("/import/{import_id}/confirm", response_model=VersionOut)
async def confirm_import(import_id: int, _: str = Depends(require_admin), session: AsyncSession = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    try:
        return await ImportService(session, settings).confirm(import_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/schedule")
async def admin_schedule(_: str = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    stmt = (
        select(ScheduleEntry)
        .join(ScheduleVersion)
        .options(selectinload(ScheduleEntry.group), selectinload(ScheduleEntry.version))
        .where(ScheduleVersion.is_active.is_(True))
        .order_by(ScheduleEntry.day_of_week, ScheduleEntry.lesson_number)
    )
    entries = (await session.scalars(stmt)).all()
    return [
        {
            "id": item.id,
            "group": item.group.name,
            "day_of_week": item.day_of_week,
            "lesson_number": item.lesson_number,
            "subject": item.subject,
            "teacher": item.teacher,
            "week_parity": item.week_parity,
        }
        for item in entries
    ]


@router.get("/versions", response_model=list[VersionOut])
async def versions(_: str = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    return (await session.scalars(select(ScheduleVersion).order_by(ScheduleVersion.created_at.desc()))).all()


@router.post("/versions/{version_id}/activate", response_model=VersionOut)
async def activate_version(version_id: int, _: str = Depends(require_admin), session: AsyncSession = Depends(get_db)):
    version = await session.get(ScheduleVersion, version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="Version not found")
    await session.execute(update(ScheduleVersion).values(is_active=False))
    version.is_active = True
    await session.commit()
    await session.refresh(version)
    return version
