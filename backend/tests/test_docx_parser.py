from pathlib import Path

from app.parsers.docx_parser import DocxScheduleParser


def test_parser_reads_actual_docx() -> None:
    result = DocxScheduleParser().parse(Path(__file__).parents[2] / "schedule.docx")

    assert not result.errors
    assert result.valid_rows > 20
    assert {"РЗ-251", "РЗ-252", "РЗ-253"}.issubset({lesson.group_name for lesson in result.lessons})
    assert any(lesson.week_parity == "odd" for lesson in result.lessons)
    assert any(lesson.week_parity == "even" for lesson in result.lessons)
    assert any(lesson.meeting_url for lesson in result.lessons)
