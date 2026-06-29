from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from uuid import uuid4

from alarm_clock.models import Alarm, AlarmState, JsonObject


class AlarmNotFoundError(Exception):
    pass


class AmbiguousAlarmReferenceError(Exception):
    pass


class AlarmStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def add_alarm(self, scheduled_for: datetime, label: str, now: datetime) -> Alarm:
        alarm = Alarm(
            id=str(uuid4()),
            scheduled_for=scheduled_for,
            label=_normalize_label(label),
            created_at=now,
        )
        alarms = self.list_alarms(include_terminal=True)
        alarms.append(alarm)
        self._write_alarms(alarms)
        return alarm

    def list_alarms(self, include_terminal: bool = False) -> list[Alarm]:
        alarms = [Alarm.from_record(record) for record in self._read_records()]
        if include_terminal:
            return sorted(alarms, key=lambda alarm: alarm.scheduled_for)
        return sorted(
            [alarm for alarm in alarms if alarm.state == AlarmState.PENDING],
            key=lambda alarm: alarm.scheduled_for,
        )

    def cancel_alarm(self, reference: str) -> Alarm:
        return self._update_state(reference=reference, state=AlarmState.CANCELLED)

    def mark_fired(self, reference: str) -> Alarm:
        return self._update_state(reference=reference, state=AlarmState.FIRED)

    def clear_terminal_alarms(self) -> int:
        alarms = self.list_alarms(include_terminal=True)
        remaining = [
            alarm for alarm in alarms if alarm.state == AlarmState.PENDING
        ]
        deleted_count = len(alarms) - len(remaining)
        self._write_alarms(remaining)
        return deleted_count

    def clear_all_alarms(self) -> int:
        deleted_count = len(self.list_alarms(include_terminal=True))
        self._write_alarms([])
        return deleted_count

    def _update_state(self, reference: str, state: AlarmState) -> Alarm:
        alarms = self.list_alarms(include_terminal=True)
        target = _find_alarm(alarms=alarms, reference=reference)
        updated = target.with_state(state)
        self._write_alarms(
            [updated if alarm.id == target.id else alarm for alarm in alarms]
        )
        return updated

    def _read_records(self) -> list[JsonObject]:
        if not self.path.exists():
            return []

        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Alarm store is not valid JSON: {self.path}") from e

        if not isinstance(payload, list):
            raise ValueError("Alarm store must contain a JSON list.")

        records: list[JsonObject] = []
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError("Every alarm record must be a JSON object.")
            records.append(item)
        return records

    def _write_alarms(self, alarms: list[Alarm]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        payload = [alarm.to_record() for alarm in alarms]
        tmp_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(self.path)


def _find_alarm(alarms: list[Alarm], reference: str) -> Alarm:
    normalized = reference.strip()
    matches = [
        alarm
        for alarm in alarms
        if alarm.id == normalized or alarm.id.startswith(normalized)
    ]
    if not matches:
        raise AlarmNotFoundError(f"No alarm matched '{reference}'.")
    if len(matches) > 1:
        raise AmbiguousAlarmReferenceError(
            f"Alarm reference '{reference}' matched multiple alarms."
        )
    return matches[0]


def _normalize_label(label: str) -> str:
    normalized = " ".join(label.strip().split())
    if not normalized:
        return "Alarm"
    if len(normalized) > 120:
        raise ValueError("Alarm label must be 120 characters or fewer.")
    return normalized
