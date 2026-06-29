# AI Design Plan

## Refined Requirements

The assignment asks for a Python CLI alarm clock with no web UI, no React, and
no database. Because this is a 30-minute build exercise, the useful scope is a
small but complete CLI workflow rather than a broad feature set.

Required behavior:

- Add one-shot alarms.
- Accept human-friendly schedules.
- List scheduled alarms.
- Cancel mistakes.
- Run a foreground process that fires due alarms.
- Persist alarms without a database.
- Include tests and a README.

Chosen constraints:

- Use standard-library `argparse` for the CLI to keep installation simple.
- Use a JSON file at `~/.alarm_clock/alarms.json` for local persistence.
- Keep scheduling foreground-only. No daemon, cron integration, or background
  service is created implicitly.
- Treat recurring alarms, snooze, custom audio files, and desktop
  notifications as non-goals for this exercise.

## CLI Shape

Commands:

- `alarm-clock add --in 10m "Tea"`
- `alarm-clock add --at 07:30 "Wake up"`
- `alarm-clock list`
- `alarm-clock list --all`
- `alarm-clock cancel ALARM_ID`
- `alarm-clock clear --completed`
- `alarm-clock clear --all`
- `alarm-clock run`
- `alarm-clock run --once`

Scheduling inputs:

- Durations: `30s`, `10m`, `2h`, `1d`, `1h30m`.
- Time of day: `HH:MM` or `HH:MM:SS`.
- ISO datetime: `YYYY-MM-DDTHH:MM:SS`.

## Implementation Design

Modules:

- `models.py`: `Alarm` dataclass and `AlarmState` enum.
- `time_parser.py`: schedule parsing with explicit validation errors.
- `store.py`: JSON-backed `AlarmStore` with atomic file replacement.
- `scheduler.py`: due-alarm detection and terminal notification.
- `cli.py`: argparse command routing and user-facing output.

Persistence:

- Records are JSON objects.
- Datetimes are stored as ISO strings.
- Fired and cancelled alarms remain available through `list --all`.
- `clear --completed` removes fired and cancelled records.

Failure handling:

- Invalid schedules fail with a clear CLI error.
- Missing alarm references fail with a clear CLI error.
- Prefix cancellation is allowed only when the prefix is unique.
- Invalid JSON in the store fails fast instead of silently dropping data.

## Validation Plan

Automated tests:

- Parse relative durations.
- Move past `HH:MM` alarms to tomorrow.
- Parse ISO datetimes.
- Reject invalid schedules.
- Persist alarms through the JSON store.
- Cancel by unique prefix.
- Reject missing and ambiguous references.
- Fire only due alarms and mark them fired.
- Exercise core CLI add/list/run-once flows.

Manual demo flow:

```bash
poetry run alarm-clock --file /tmp/alarms.json add --in 5s "Demo alarm"
poetry run alarm-clock --file /tmp/alarms.json list
poetry run alarm-clock --file /tmp/alarms.json run
poetry run alarm-clock --file /tmp/alarms.json list --all
```

Repository checks:

```bash
make check
```
