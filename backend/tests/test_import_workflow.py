from pathlib import Path

from app.core.config import get_settings
from app.services.import_service import ImportService
from app.services.schedule_service import ScheduleService


async def test_import_preview_confirm_and_schedule(client) -> None:
    async for session in client._transport.app.dependency_overrides[next(iter(client._transport.app.dependency_overrides))]():
        service = ImportService(session, get_settings())
        record = await service.create_import("schedule.docx", Path(__file__).parents[2] / "schedule.docx")
        assert record.status == "parsed"
        assert record.valid_rows > 20

        version = await service.confirm(record.id)
        assert version.is_active

        day = await ScheduleService(session, get_settings()).for_date(get_settings().semester_start_date, "РЗ-252")
        assert day.lessons
        assert all(lesson.group == "РЗ-252" for lesson in day.lessons)
