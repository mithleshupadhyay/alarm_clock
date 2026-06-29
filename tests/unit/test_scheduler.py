from datetime import datetime, timedelta, timezone

from alarm_clock.models import Alarm
from alarm_clock.scheduler import fire_due_alarms
from alarm_clock.store import AlarmStore


class CapturingNotifier:
    def __init__(self) -> None:
        self.alarms: list[Alarm] = []

    def notify(self, alarm: Alarm) -> None:
        self.alarms.append(alarm)


def test_fire_due_alarms_marks_only_due_pending_alarms(tmp_path) -> None:
    store = AlarmStore(path=tmp_path / "alarms.json")
    now = datetime(2026, 6, 29, 9, 0, tzinfo=timezone.utc)
    due = store.add_alarm(
        scheduled_for=now - timedelta(seconds=1),
        label="Due",
        now=now,
    )
    store.add_alarm(
        scheduled_for=now + timedelta(minutes=1),
        label="Future",
        now=now,
    )
    notifier = CapturingNotifier()

    fired = fire_due_alarms(store=store, now=now, notifier=notifier)

    assert [alarm.id for alarm in fired] == [due.id]
    assert [alarm.id for alarm in notifier.alarms] == [due.id]
    assert [alarm.label for alarm in store.list_alarms()] == ["Future"]
