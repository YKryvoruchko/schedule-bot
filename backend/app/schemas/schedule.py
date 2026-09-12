from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, HttpUrl


class GroupOut(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class LessonOut(BaseModel):
    id: int
    date: date
    group: str
    day_of_week: int
    lesson_number: int
    starts_at: datetime
    ends_at: datetime
    subject: str
    teacher: str | None
    meeting_url: str | None
    room: str | None
    description: str | None
    lesson_type: str | None
    week_start: int | None
    week_end: int | None
    week_parity: str
    status: str


class DayScheduleOut(BaseModel):
    date: date
    timezone: str
    server_now: datetime
    lessons: list[LessonOut]
    current_lesson: LessonOut | None
    next_lesson: LessonOut | None


class WeekScheduleOut(BaseModel):
    timezone: str
    server_now: datetime
    days: list[DayScheduleOut]


class VersionOut(BaseModel):
    id: int
    filename: str
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class ImportOut(BaseModel):
    id: int
    filename: str
    status: str
    uploaded_at: datetime
    processed_at: datetime | None
    row_count: int
    valid_rows: int
    invalid_rows: int
    warnings: list[str]
    errors: list[str]


class ImportPreviewOut(ImportOut):
    preview: list[dict]


class LoginIn(BaseModel):
    username: str
    password: str


class NotificationSettingsIn(BaseModel):
    enabled: bool
    minutes_before: int


class TelegramUserIn(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
