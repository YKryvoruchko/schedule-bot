from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import ScheduleEntry, ScheduleVersion, StudentGroup
from app.services.schedule_service import ScheduleService


async def test_current_and_next_lesson_status(client) -> None:
    async for session in client._transport.app.dependency_overrides[next(iter(client._transport.app.dependency_overrides))]():
        assert isinstance(session, AsyncSession)
        group = StudentGroup(name="РЗ-252")
        version = ScheduleVersion(filename="test.docx", is_active=True)
        session.add_all([group, version])
        await session.flush()
        session.add_all(
            [
                ScheduleEntry(version_id=version.id, group_id=group.id, day_of_week=1, lesson_number=1, starts_at=time(8, 30), ends_at=time(10), subject="A", week_parity="any"),
                ScheduleEntry(version_id=version.id, group_id=group.id, day_of_week=1, lesson_number=2, starts_at=time(10, 15), ends_at=time(11, 45), subject="B", week_parity="any"),
            ]
        )
        await session.commit()
        service = ScheduleService(session, get_settings())
        day = await service.for_date(get_settings().semester_start_date, "РЗ-252")
        assert [lesson.subject for lesson in day.lessons] == ["A", "B"]
