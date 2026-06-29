from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


JsonObject = dict[str, Any]


class AlarmState(StrEnum):
    PENDING = "pending"
    FIRED = "fired"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Alarm:
    id: str
    scheduled_for: datetime
    label: str
    created_at: datetime
    state: AlarmState = AlarmState.PENDING

    def is_due(self, now: datetime) -> bool:
        return self.state == AlarmState.PENDING and self.scheduled_for <= now

    def with_state(self, state: AlarmState) -> Alarm:
        return Alarm(
            id=self.id,
            scheduled_for=self.scheduled_for,
            label=self.label,
            created_at=self.created_at,
            state=state,
        )

    def to_record(self) -> JsonObject:
        return {
            "id": self.id,
            "scheduled_for": self.scheduled_for.isoformat(),
            "label": self.label,
            "created_at": self.created_at.isoformat(),
            "state": self.state.value,
        }

    @classmethod
    def from_record(cls, record: JsonObject) -> Alarm:
        return cls(
            id=str(record["id"]),
            scheduled_for=datetime.fromisoformat(str(record["scheduled_for"])),
            label=str(record["label"]),
            created_at=datetime.fromisoformat(str(record["created_at"])),
            state=AlarmState(str(record["state"])),
        )
