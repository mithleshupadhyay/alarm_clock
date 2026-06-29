from datetime import datetime, timedelta, timezone

import pytest

from alarm_clock.models import AlarmState
from alarm_clock.store import (
    AlarmNotFoundError,
    AlarmStore,
    AmbiguousAlarmReferenceError,
)


def test_alarm_store_adds_and_persists_alarm(tmp_path) -> None:
    store_path = tmp_path / "alarms.json"
    store = AlarmStore(path=store_path)
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)

    alarm = store.add_alarm(
        scheduled_for=now + timedelta(minutes=5),
        label="  Morning   standup  ",
        now=now,
    )
    reloaded = AlarmStore(path=store_path).list_alarms()

    assert alarm.id == reloaded[0].id
    assert reloaded[0].label == "Morning standup"
    assert reloaded[0].state == AlarmState.PENDING


def test_alarm_store_cancels_by_unique_prefix(tmp_path) -> None:
    store = AlarmStore(path=tmp_path / "alarms.json")
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)
    alarm = store.add_alarm(
        scheduled_for=now + timedelta(minutes=5),
        label="Tea",
        now=now,
    )

    cancelled = store.cancel_alarm(alarm.id[:8])

    assert cancelled.state == AlarmState.CANCELLED
    assert store.list_alarms() == []
    assert store.list_alarms(include_terminal=True)[0].state == AlarmState.CANCELLED


def test_alarm_store_rejects_missing_alarm_reference(tmp_path) -> None:
    store = AlarmStore(path=tmp_path / "alarms.json")

    with pytest.raises(AlarmNotFoundError):
        store.cancel_alarm("missing")


def test_alarm_store_rejects_ambiguous_prefix(tmp_path) -> None:
    store = AlarmStore(path=tmp_path / "alarms.json")
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)
    store.add_alarm(scheduled_for=now, label="A", now=now)
    store.add_alarm(scheduled_for=now, label="B", now=now)

    with pytest.raises(AmbiguousAlarmReferenceError):
        store.cancel_alarm("")


def test_alarm_store_clears_terminal_alarms(tmp_path) -> None:
    store = AlarmStore(path=tmp_path / "alarms.json")
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)
    pending = store.add_alarm(scheduled_for=now, label="Pending", now=now)
    fired = store.add_alarm(scheduled_for=now, label="Fired", now=now)
    store.mark_fired(fired.id)

    deleted_count = store.clear_terminal_alarms()

    alarms = store.list_alarms(include_terminal=True)
    assert deleted_count == 1
    assert alarms[0].id == pending.id
