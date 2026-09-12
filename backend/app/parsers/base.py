from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ParsedLesson:
    group_name: str
    day_of_week: int
    lesson_number: int
    starts_at: time
    ends_at: time
    subject: str
    teacher: str | None = None
    meeting_url: str | None = None
    room: str | None = None
    description: str | None = None
    lesson_type: str | None = None
    week_start: int | None = None
    week_end: int | None = None
    week_parity: str = "any"
    source_table: int | None = None
    source_row: int | None = None
    source_col: int | None = None


@dataclass
class ParseResult:
    lessons: list[ParsedLesson] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    total_rows: int = 0

    @property
    def valid_rows(self) -> int:
        return len(self.lessons)

    @property
    def invalid_rows(self) -> int:
        return len(self.errors)


class ScheduleParser(Protocol):
    def parse(self, path: Path) -> ParseResult:
        ...
