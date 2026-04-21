"""Tests for envforge.notify."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envforge.notify import (
    register_hook,
    unregister_hook,
    list_hooks,
    fire_event,
)
from envforge.cli_notify import notify_cmd


@pytest.fixture
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_register_and_list(tmp_snapshot_dir):
    register_hook("save", "echo saved", tmp_snapshot_dir)
    hooks = list_hooks(tmp_snapshot_dir)
    assert "save" in hooks
    assert "echo saved" in hooks["save"]


def test_register_idempotent(tmp_snapshot_dir):
    register_hook("save", "echo saved", tmp_snapshot_dir)
    register_hook("save", "echo saved", tmp_snapshot_dir)
    hooks = list_hooks(tmp_snapshot_dir)
    assert hooks["save"].count("echo saved") == 1


def test_unregister_existing(tmp_snapshot_dir):
    register_hook("delete", "echo deleted", tmp_snapshot_dir)
    result = unregister_hook("delete", "echo deleted", tmp_snapshot_dir)
    assert result is True
    hooks = list_hooks(tmp_snapshot_dir)
    assert "echo deleted" not in hooks.get("delete", [])


def test_unregister_nonexistent_returns_false(tmp_snapshot_dir):
    result = unregister_hook("load", "echo nope", tmp_snapshot_dir)
    assert result is False


def test_list_empty_when_no_hooks(tmp_snapshot_dir):
    hooks = list_hooks(tmp_snapshot_dir)
    assert hooks == {}


def test_fire_event_runs_hooks(tmp_snapshot_dir):
    register_hook("save", "true", tmp_snapshot_dir)
    with patch("subprocess.run") as mock_run:
        executed = fire_event("save", {"snapshot": "mysnap"}, tmp_snapshot_dir)
    assert "true" in executed
    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args
    assert call_kwargs[1]["shell"] is True


def test_fire_event_no_hooks_returns_empty(tmp_snapshot_dir):
    executed = fire_event("unknown_event", {}, tmp_snapshot_dir)
    assert executed == []


def test_cli_add_and_list(tmp_snapshot_dir):
    runner = CliRunner()
    result = runner.invoke(
        notify_cmd,
        ["add", "save", "echo hi", "--dir", str(tmp_snapshot_dir)],
    )
    assert result.exit_code == 0
    assert "registered" in result.output

    result = runner.invoke(
        notify_cmd, ["list", "--dir", str(tmp_snapshot_dir)]
    )
    assert "echo hi" in result.output


def test_cli_remove_hook(tmp_snapshot_dir):
    runner = CliRunner()
    register_hook("delete", "echo bye", tmp_snapshot_dir)
    result = runner.invoke(
        notify_cmd,
        ["remove", "delete", "echo bye", "--dir", str(tmp_snapshot_dir)],
    )
    assert result.exit_code == 0
    assert "removed" in result.output
