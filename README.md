# Alarm Clock

Python CLI alarm clock for adding, listing, cancelling, and running alarms in a
foreground terminal process. It uses a local JSON file for persistence and does
not use a web UI, React, or a database.

## Requirements

- Python 3.12+
- Poetry

## Setup

```bash
poetry install
```

## Usage

Add an alarm using a relative duration:

```bash
poetry run alarm-clock add --in 10m "Tea break"
```

Add an alarm using a local time. If the time has already passed today, it is
scheduled for tomorrow.

```bash
poetry run alarm-clock add --at 07:30 "Wake up"
```

Add an alarm using an ISO datetime:

```bash
poetry run alarm-clock add --at 2026-06-30T09:00:00 "Daily standup"
```

List pending alarms:

```bash
poetry run alarm-clock list
```

Cancel an alarm with its full id or unique prefix:

```bash
poetry run alarm-clock cancel 8f3a21c9
```

Run the scheduler in the foreground:

```bash
poetry run alarm-clock run
```

The scheduler emits the terminal bell and prints the alarm label when an alarm
is due. It exits once there are no pending alarms. Use `Ctrl+C` to stop it
earlier.

By default alarms are stored in `~/.alarm_clock/alarms.json`. For isolated
testing or demos:

```bash
poetry run alarm-clock --file /tmp/alarms.json add --in 30s "Demo"
poetry run alarm-clock --file /tmp/alarms.json run
```

## Commands

- `add --in DURATION LABEL`: Add an alarm after `30s`, `10m`, `2h`, `1d`, or
  combined values like `1h30m`.
- `add --at TIME LABEL`: Add an alarm at `HH:MM`, `HH:MM:SS`, or an ISO
  datetime.
- `list`: List pending alarms.
- `list --all`: Include fired and cancelled alarms.
- `cancel ALARM_ID`: Cancel by full id or unique prefix.
- `clear --completed`: Remove fired and cancelled records.
- `clear --all`: Remove every record.
- `run`: Run the foreground scheduler.
- `run --once`: Fire alarms that are already due, then exit.

## Validation

```bash
make check
```

Individual checks:

```bash
make test
make lint
make typecheck
make poetry-check
```

## Design Notes

See [docs/AI_DESIGN_PLAN.md](docs/AI_DESIGN_PLAN.md) for the AI-assisted
requirements refinement, design choices, implementation plan, and validation
plan used before coding.
