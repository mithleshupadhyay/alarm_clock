from __future__ import annotations

from datetime import datetime
from typing import Protocol
import time

from alarm_clock.models import Alarm, AlarmState
from alarm_clock.store import AlarmStore


class Notifier(Protocol):
    def notify(self, alarm: Alarm) -> None:
        pass


class TerminalNotifier:
    def notify(self, alarm: Alarm) -> None:
        scheduled_at = format_alarm_datetime(alarm.scheduled_for)
        print("\a", end="", flush=True)
        print(f"[Alarm] {scheduled_at} - {alarm.label}", flush=True)


def fire_due_alarms(store: AlarmStore, now: datetime, notifier: Notifier) -> list[Alarm]:
    due_alarms = [
        alarm
        for alarm in store.list_alarms(include_terminal=True)
        if alarm.is_due(now)
    ]

    fired_alarms = []
    for alarm in due_alarms:
        notifier.notify(alarm)
        fired_alarms.append(store.mark_fired(alarm.id))

    return fired_alarms


def run_alarm_loop(
    store: AlarmStore,
    notifier: Notifier,
    poll_seconds: float,
    once: bool = False,
) -> int:
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be greater than zero.")

    fired_count = 0
    while True:
        now = datetime.now().astimezone()
        fired_count += len(fire_due_alarms(store=store, now=now, notifier=notifier))

        if once:
            return fired_count

        pending_alarms = [
            alarm
            for alarm in store.list_alarms()
            if alarm.state == AlarmState.PENDING
        ]
        if not pending_alarms:
            return fired_count

        time.sleep(poll_seconds)


def format_alarm_datetime(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
