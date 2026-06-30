# AI-Assisted Design Plan

## Refined Requirements

The assignment asks for a Python CLI alarm clock with no web UI, no React, and
no database. Because the spec is intentionally open, I used AI before coding to
turn that brief into a small, complete workflow that could be built and
validated within the exercise time.

Required behavior:

- Add one-shot alarms.
- Accept human-friendly schedules.
- List scheduled alarms.
- Cancel mistakes.
- Run a scheduler that fires due alarms.
- Persist alarms without a database.
- Include tests and a README.

Chosen constraints and non-goals:

- Use standard-library `argparse` for the CLI to keep installation simple.
- Use a JSON file at `~/.alarm_clock/alarms.json` for local persistence.
- Keep scheduling foreground-only. No daemon, cron integration, or background
  service is created implicitly.
- Treat recurring alarms, snooze, custom audio files, and desktop
  notifications as non-goals for this exercise.

The key scope decision is that `alarm-clock add` stores an alarm, while
`alarm-clock run` is responsible for firing it. This avoids hiding background
process behavior inside a simple CLI.

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

Expected behavior:

- A past time-of-day value schedules for tomorrow.
- A due alarm emits the terminal bell and prints the label.
- Fired and cancelled alarms are hidden from the default list but visible with
  `list --all`.

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

## Engineering Tradeoffs

- `argparse` was chosen over a richer CLI framework to avoid unnecessary
  dependencies.
- JSON persistence was chosen over SQLite because the assignment explicitly says
  no database and the data model is small.
- Foreground scheduling was chosen over daemon behavior because it is explicit,
  easy to test, and honest for a small CLI submission.
- One-shot alarms were chosen over recurring rules because recurring schedules
  introduce more parsing and edge cases than the core exercise needs.

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
