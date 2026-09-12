from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import ScheduleEntry, ScheduleImport, ScheduleVersion, StudentGroup
from app.parsers.base import ParseResult, ParsedLesson
from app.parsers.docx_parser import DocxScheduleParser


class ImportService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
        self.parser = DocxScheduleParser()

    async def create_import(self, filename: str, path: Path) -> ScheduleImport:
        record = ScheduleImport(filename=filename, status="processing")
        self.session.add(record)
        await self.session.flush()
        result = self.parser.parse(path)
        record.status = "parsed" if not result.errors else "failed"
        record.processed_at = datetime.now(self.settings.tz)
        record.row_count = result.total_rows
        record.valid_rows = result.valid_rows
        record.invalid_rows = result.invalid_rows
        record.warnings = json.dumps(result.warnings, ensure_ascii=False)
        record.errors = json.dumps(result.errors, ensure_ascii=False)
        record.preview = json.dumps([lesson.__dict__ | {"starts_at": lesson.starts_at.isoformat(), "ends_at": lesson.ends_at.isoformat()} for lesson in result.lessons], ensure_ascii=False)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def confirm(self, import_id: int) -> ScheduleVersion:
        record = await self.session.get(ScheduleImport, import_id)
        if record is None:
            raise ValueError("Import not found.")
        if record.status != "parsed":
            raise ValueError("Only successfully parsed imports can be confirmed.")
        lessons = [self._lesson_from_dict(item) for item in json.loads(record.preview)]
        async with self.session.begin_nested():
            await self.session.execute(update(ScheduleVersion).values(is_active=False))
            version = ScheduleVersion(filename=record.filename, is_active=True)
            self.session.add(version)
            await self.session.flush()
            group_cache: dict[str, StudentGroup] = {}
            for lesson in lessons:
                group = await self._group(lesson.group_name, group_cache)
                self.session.add(
                    ScheduleEntry(
                        version_id=version.id,
                        group_id=group.id,
                        day_of_week=lesson.day_of_week,
                        lesson_number=lesson.lesson_number,
                        starts_at=lesson.starts_at,
                        ends_at=lesson.ends_at,
                        subject=lesson.subject,
                        teacher=lesson.teacher,
                        meeting_url=lesson.meeting_url,
                        room=lesson.room,
                        description=lesson.description,
                        lesson_type=lesson.lesson_type,
                        week_start=lesson.week_start,
                        week_end=lesson.week_end,
                        week_parity=lesson.week_parity,
                    )
                )
            record.status = "confirmed"
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def _group(self, name: str, cache: dict[str, StudentGroup]) -> StudentGroup:
        if name in cache:
            return cache[name]
        group = await self.session.scalar(select(StudentGroup).where(StudentGroup.name == name))
        if group is None:
            group = StudentGroup(name=name)
            self.session.add(group)
            await self.session.flush()
        cache[name] = group
        return group

    def _lesson_from_dict(self, data: dict) -> ParsedLesson:
        from datetime import time

        return ParsedLesson(
            **{
                **data,
                "starts_at": time.fromisoformat(data["starts_at"]),
                "ends_at": time.fromisoformat(data["ends_at"]),
            }
        )


def import_to_dict(record: ScheduleImport) -> dict:
    return {
        "id": record.id,
        "filename": record.filename,
        "status": record.status,
        "uploaded_at": record.uploaded_at,
        "processed_at": record.processed_at,
        "row_count": record.row_count,
        "valid_rows": record.valid_rows,
        "invalid_rows": record.invalid_rows,
        "warnings": json.loads(record.warnings or "[]"),
        "errors": json.loads(record.errors or "[]"),
    }
