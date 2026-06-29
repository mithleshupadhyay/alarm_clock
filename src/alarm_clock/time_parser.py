from __future__ import annotations

from datetime import datetime, timedelta, tzinfo
import re


_DURATION_TOKEN_PATTERN = re.compile(r"(?P<amount>\d+)(?P<unit>[smhd])")
_TIME_FORMATS = ("%H:%M:%S", "%H:%M")


def parse_alarm_schedule(value: str, now: datetime) -> datetime:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Alarm time is required.")

    duration = _parse_duration(normalized)
    if duration is not None:
        return now + duration

    if _looks_like_datetime(normalized):
        scheduled_for = datetime.fromisoformat(normalized)
        return _with_local_timezone(scheduled_for, now.tzinfo)

    scheduled_for = _parse_time_of_day(normalized, now)
    if scheduled_for <= now:
        scheduled_for += timedelta(days=1)
    return scheduled_for


def _parse_duration(value: str) -> timedelta | None:
    normalized = value.lower().replace(" ", "")
    matches = list(_DURATION_TOKEN_PATTERN.finditer(normalized))
    if not matches:
        return None

    consumed = "".join(match.group(0) for match in matches)
    if consumed != normalized:
        raise ValueError(
            "Duration must use tokens like 30s, 10m, 2h, 1d, or 1h30m."
        )

    seconds = 0
    for match in matches:
        amount = int(match.group("amount"))
        unit = match.group("unit")
        if unit == "s":
            seconds += amount
        elif unit == "m":
            seconds += amount * 60
        elif unit == "h":
            seconds += amount * 60 * 60
        elif unit == "d":
            seconds += amount * 24 * 60 * 60

    if seconds <= 0:
        raise ValueError("Duration must be greater than zero.")
    return timedelta(seconds=seconds)


def _looks_like_datetime(value: str) -> bool:
    return "T" in value or bool(re.match(r"^\d{4}-\d{2}-\d{2} ", value))


def _parse_time_of_day(value: str, now: datetime) -> datetime:
    for time_format in _TIME_FORMATS:
        try:
            parsed = datetime.strptime(value, time_format)
        except ValueError:
            continue

        return now.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=parsed.second,
            microsecond=0,
        )

    raise ValueError(
        "Alarm time must be a duration, HH:MM, HH:MM:SS, or ISO datetime."
    )


def _with_local_timezone(value: datetime, fallback_timezone: tzinfo | None) -> datetime:
    if value.tzinfo is not None:
        return value
    if fallback_timezone is None:
        return value.astimezone()
    return value.replace(tzinfo=fallback_timezone)
