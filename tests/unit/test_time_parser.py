from datetime import datetime, timedelta, timezone

import pytest

from alarm_clock.time_parser import parse_alarm_schedule


def test_parse_alarm_schedule_accepts_duration_tokens() -> None:
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    scheduled_for = parse_alarm_schedule("1h30m", now=now)

    assert scheduled_for == now + timedelta(minutes=90)


def test_parse_alarm_schedule_moves_past_time_to_tomorrow() -> None:
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    scheduled_for = parse_alarm_schedule("08:30", now=now)

    assert scheduled_for == datetime(2026, 6, 30, 8, 30, tzinfo=timezone.utc)


def test_parse_alarm_schedule_keeps_future_time_today() -> None:
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    scheduled_for = parse_alarm_schedule("09:30:05", now=now)

    assert scheduled_for == datetime(2026, 6, 29, 9, 30, 5, tzinfo=timezone.utc)


def test_parse_alarm_schedule_accepts_iso_datetime() -> None:
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    scheduled_for = parse_alarm_schedule("2026-06-30T07:15:00", now=now)

    assert scheduled_for == datetime(2026, 6, 30, 7, 15, tzinfo=timezone.utc)


def test_parse_alarm_schedule_rejects_invalid_duration() -> None:
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        parse_alarm_schedule("10x", now=now)
