from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
from typing import Sequence

from alarm_clock.models import Alarm
from alarm_clock.scheduler import (
    TerminalNotifier,
    format_alarm_datetime,
    run_alarm_loop,
)
from alarm_clock.store import (
    AlarmNotFoundError,
    AlarmStore,
    AmbiguousAlarmReferenceError,
)
from alarm_clock.time_parser import parse_alarm_schedule


DEFAULT_STORE_PATH = Path(
    os.environ.get("ALARM_CLOCK_STORE", "~/.alarm_clock/alarms.json")
).expanduser()


def main(argv: Sequence[str] | None = None) -> None:
    raise SystemExit(run(argv))


def run(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    store = AlarmStore(path=args.file)

    try:
        if args.command == "add":
            return _add_alarm(args=args, store=store)
        if args.command == "list":
            return _list_alarms(args=args, store=store)
        if args.command == "cancel":
            return _cancel_alarm(args=args, store=store)
        if args.command == "clear":
            return _clear_alarms(args=args, store=store)
        if args.command == "run":
            return _run_alarms(args=args, store=store)
    except (AlarmNotFoundError, AmbiguousAlarmReferenceError, ValueError) as e:
        parser.exit(status=1, message=f"alarm-clock: error: {e}\n")

    parser.print_help()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="alarm-clock",
        description="CLI alarm clock with foreground scheduling.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_STORE_PATH,
        help=f"alarm store path, defaults to {DEFAULT_STORE_PATH}",
    )

    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="add a new alarm")
    schedule_group = add_parser.add_mutually_exclusive_group(required=True)
    schedule_group.add_argument(
        "--at",
        dest="at_value",
        help="absolute time: HH:MM, HH:MM:SS, or ISO datetime",
    )
    schedule_group.add_argument(
        "--in",
        dest="in_value",
        help="relative duration: 30s, 10m, 2h, 1d, or 1h30m",
    )
    add_parser.add_argument("label", nargs="?", default="Alarm")

    list_parser = subparsers.add_parser("list", help="list alarms")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="include fired and cancelled alarms",
    )

    cancel_parser = subparsers.add_parser("cancel", help="cancel an alarm")
    cancel_parser.add_argument("alarm_id", help="full alarm id or unique prefix")

    clear_parser = subparsers.add_parser("clear", help="clear alarm records")
    clear_group = clear_parser.add_mutually_exclusive_group(required=True)
    clear_group.add_argument(
        "--completed",
        action="store_true",
        help="remove fired and cancelled alarms",
    )
    clear_group.add_argument(
        "--all",
        action="store_true",
        help="remove every alarm",
    )

    run_parser = subparsers.add_parser("run", help="run alarms in the foreground")
    run_parser.add_argument(
        "--poll-seconds",
        type=float,
        default=1.0,
        help="scheduler polling interval",
    )
    run_parser.add_argument(
        "--once",
        action="store_true",
        help="fire due alarms once and exit",
    )

    return parser


def _add_alarm(args: argparse.Namespace, store: AlarmStore) -> int:
    now = _now()
    schedule_value = args.at_value or args.in_value
    scheduled_for = parse_alarm_schedule(value=schedule_value, now=now)
    alarm = store.add_alarm(
        scheduled_for=scheduled_for,
        label=args.label,
        now=now,
    )
    print(f"Added alarm {alarm.id[:8]} for {format_alarm_datetime(alarm.scheduled_for)}")
    return 0


def _list_alarms(args: argparse.Namespace, store: AlarmStore) -> int:
    alarms = store.list_alarms(include_terminal=args.all)
    if not alarms:
        print("No alarms found.")
        return 0

    for alarm in alarms:
        print(_format_alarm_row(alarm))
    return 0


def _cancel_alarm(args: argparse.Namespace, store: AlarmStore) -> int:
    alarm = store.cancel_alarm(args.alarm_id)
    print(f"Cancelled alarm {alarm.id[:8]} ({alarm.label})")
    return 0


def _clear_alarms(args: argparse.Namespace, store: AlarmStore) -> int:
    if args.all:
        deleted_count = store.clear_all_alarms()
    else:
        deleted_count = store.clear_terminal_alarms()
    print(f"Deleted {deleted_count} alarm record(s).")
    return 0


def _run_alarms(args: argparse.Namespace, store: AlarmStore) -> int:
    pending_alarms = store.list_alarms()
    if not pending_alarms:
        print("No pending alarms. Add one with: alarm-clock add --in 10m \"Tea\"")
        return 0

    next_alarm = pending_alarms[0]
    print(
        "Running alarm clock. "
        f"Next alarm {next_alarm.id[:8]} at "
        f"{format_alarm_datetime(next_alarm.scheduled_for)}"
    )
    fired_count = run_alarm_loop(
        store=store,
        notifier=TerminalNotifier(),
        poll_seconds=args.poll_seconds,
        once=args.once,
    )
    print(f"Fired {fired_count} alarm(s).")
    return 0


def _format_alarm_row(alarm: Alarm) -> str:
    return (
        f"{alarm.id[:8]}  "
        f"{alarm.state.value:<9}  "
        f"{format_alarm_datetime(alarm.scheduled_for)}  "
        f"{alarm.label}"
    )


def _now() -> datetime:
    return datetime.now().astimezone()
