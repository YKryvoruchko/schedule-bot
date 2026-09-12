from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import Settings
from app.models import ScheduleEntry, ScheduleVersion
from app.schemas.schedule import DayScheduleOut, LessonOut, WeekScheduleOut


class ScheduleService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings

    async def for_date(self, target_date: date, group: str | None = None) -> DayScheduleOut:
        now = datetime.now(self.settings.tz)
        stmt = (
            select(ScheduleEntry)
            .join(ScheduleVersion)
            .options(selectinload(ScheduleEntry.group))
            .where(ScheduleVersion.is_active.is_(True), ScheduleEntry.day_of_week == target_date.weekday())
            .order_by(ScheduleEntry.lesson_number, ScheduleEntry.starts_at)
        )
        if group:
            from app.models import StudentGroup

            stmt = stmt.join(StudentGroup).where(StudentGroup.name == group)
        entries = (await self.session.scalars(stmt)).all()
        lessons = [self._to_lesson(entry, target_date, now) for entry in entries if self._matches_week(entry, target_date)]
        current = next((lesson for lesson in lessons if lesson.status == "current"), None)
        next_lesson = next((lesson for lesson in lessons if lesson.status == "upcoming"), None)
        return DayScheduleOut(
            date=target_date,
            timezone=self.settings.timezone,
            server_now=now,
            lessons=lessons,
            current_lesson=current,
            next_lesson=next_lesson,
        )

    async def today(self, group: str | None = None) -> DayScheduleOut:
        return await self.for_date(datetime.now(self.settings.tz).date(), group)

    async def tomorrow(self, group: str | None = None) -> DayScheduleOut:
        return await self.for_date(datetime.now(self.settings.tz).date() + timedelta(days=1), group)

    async def week(self, group: str | None = None) -> WeekScheduleOut:
        today = datetime.now(self.settings.tz).date()
        monday = today - timedelta(days=today.weekday())
        return WeekScheduleOut(
            timezone=self.settings.timezone,
            server_now=datetime.now(self.settings.tz),
            days=[await self.for_date(monday + timedelta(days=offset), group) for offset in range(7)],
        )

    def _to_lesson(self, entry: ScheduleEntry, target_date: date, now: datetime) -> LessonOut:
        starts = self._combine(target_date, entry.starts_at)
        ends = self._combine(target_date, entry.ends_at)
        if starts <= now < ends:
            status = "current"
        elif now >= ends:
            status = "finished"
        else:
            status = "upcoming"
        return LessonOut(
            id=entry.id,
            date=target_date,
            group=entry.group.name,
            day_of_week=entry.day_of_week,
            lesson_number=entry.lesson_number,
            starts_at=starts,
            ends_at=ends,
            subject=entry.subject,
            teacher=entry.teacher,
            meeting_url=entry.meeting_url,
            room=entry.room,
            description=entry.description,
            lesson_type=entry.lesson_type,
            week_start=entry.week_start,
            week_end=entry.week_end,
            week_parity=entry.week_parity,
            status=status,
        )

    def _combine(self, target_date: date, value: time) -> datetime:
        return datetime.combine(target_date, value, tzinfo=self.settings.tz)

    def _matches_week(self, entry: ScheduleEntry, target_date: date) -> bool:
        week_no = ((target_date - self.settings.semester_start_date).days // 7) + 1
        if entry.week_start and week_no < entry.week_start:
            return False
        if entry.week_end and week_no > entry.week_end:
            return False
        if entry.week_parity == "odd" and week_no % 2 == 0:
            return False
        if entry.week_parity == "even" and week_no % 2 != 0:
            return False
        return True
