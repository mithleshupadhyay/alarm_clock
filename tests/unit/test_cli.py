from alarm_clock.cli import run


def test_cli_add_and_list_alarm(tmp_path, capsys) -> None:
    store_path = tmp_path / "alarms.json"

    exit_code = run(
        [
            "--file",
            str(store_path),
            "add",
            "--in",
            "10m",
            "Tea",
        ]
    )
    list_exit_code = run(["--file", str(store_path), "list"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert list_exit_code == 0
    assert "Added alarm" in output
    assert "Tea" in output
    assert "pending" in output


def test_cli_run_once_without_pending_alarm(tmp_path, capsys) -> None:
    store_path = tmp_path / "alarms.json"

    exit_code = run(["--file", str(store_path), "run", "--once"])

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "No pending alarms" in output
