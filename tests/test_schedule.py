"""Tests for envforge.schedule and cli_schedule."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envforge.cli_schedule import schedule_cmd
from envforge.schedule import (
    get_schedule,
    list_schedules,
    remove_schedule,
    set_schedule,
)
from envforge.snapshot import save_snapshot


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


@pytest.fixture()
def _dir(tmp_snapshot_dir: Path) -> Path:
    save_snapshot(tmp_snapshot_dir, "dev", {"FOO": "bar"})
    return tmp_snapshot_dir


def test_set_and_get_schedule(_dir: Path) -> None:
    set_schedule(_dir, "dev", "0 9 * * 1-5", label="weekday mornings")
    entry = get_schedule(_dir, "dev")
    assert entry is not None
    assert entry["cron"] == "0 9 * * 1-5"
    assert entry["label"] == "weekday mornings"


def test_get_schedule_missing_returns_none(_dir: Path) -> None:
    assert get_schedule(_dir, "dev") is None


def test_set_schedule_missing_snapshot_raises(tmp_snapshot_dir: Path) -> None:
    with pytest.raises(FileNotFoundError, match="not found"):
        set_schedule(tmp_snapshot_dir, "ghost", "* * * * *")


def test_remove_schedule(_dir: Path) -> None:
    set_schedule(_dir, "dev", "@daily")
    remove_schedule(_dir, "dev")
    assert get_schedule(_dir, "dev") is None


def test_remove_schedule_noop_if_absent(_dir: Path) -> None:
    remove_schedule(_dir, "dev")  # should not raise


def test_list_schedules(_dir: Path) -> None:
    save_snapshot(_dir, "prod", {"ENV": "production"})
    set_schedule(_dir, "dev", "@hourly")
    set_schedule(_dir, "prod", "@daily", label="nightly")
    result = list_schedules(_dir)
    assert "dev" in result
    assert "prod" in result
    assert result["prod"]["label"] == "nightly"


# --- CLI tests ---

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def _dir_args(d: Path) -> list[str]:
    return ["--dir", str(d)]


def test_cli_set_and_list(_dir: Path, runner: CliRunner) -> None:
    r = runner.invoke(schedule_cmd, ["set", "dev", "@hourly"] + _dir_args(_dir))
    assert r.exit_code == 0
    assert "dev" in r.output

    r = runner.invoke(schedule_cmd, ["list"] + _dir_args(_dir))
    assert r.exit_code == 0
    assert "@hourly" in r.output


def test_cli_show_no_schedule(_dir: Path, runner: CliRunner) -> None:
    r = runner.invoke(schedule_cmd, ["show", "dev"] + _dir_args(_dir))
    assert r.exit_code == 0
    assert "No schedule" in r.output


def test_cli_set_missing_snapshot(tmp_snapshot_dir: Path, runner: CliRunner) -> None:
    r = runner.invoke(schedule_cmd, ["set", "ghost", "@daily"] + _dir_args(tmp_snapshot_dir))
    assert r.exit_code != 0
    assert "not found" in r.output.lower() or "Error" in r.output
