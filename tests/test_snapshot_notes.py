"""Tests for snapshot notes feature."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.snapshot_notes import set_note, get_note, delete_note, list_notes
from envforge.cli_notes import notes_cmd


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


def _save(name: str, snapshot_dir: str, vars: dict | None = None) -> None:
    save_snapshot(name, vars or {"KEY": "val"}, snapshot_dir)


# --- unit tests ---

def test_set_and_get_note(tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    set_note("mysnap", "initial deploy env", tmp_snapshot_dir)
    assert get_note("mysnap", tmp_snapshot_dir) == "initial deploy env"


def test_get_note_missing_returns_none(tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    assert get_note("mysnap", tmp_snapshot_dir) is None


def test_set_note_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        set_note("ghost", "some note", tmp_snapshot_dir)


def test_overwrite_note(tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    set_note("mysnap", "first", tmp_snapshot_dir)
    set_note("mysnap", "second", tmp_snapshot_dir)
    assert get_note("mysnap", tmp_snapshot_dir) == "second"


def test_delete_existing_note(tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    set_note("mysnap", "to be removed", tmp_snapshot_dir)
    result = delete_note("mysnap", tmp_snapshot_dir)
    assert result is True
    assert get_note("mysnap", tmp_snapshot_dir) is None


def test_delete_nonexistent_note_returns_false(tmp_snapshot_dir):
    _save("mysnap", tmp_snapshot_dir)
    assert delete_note("mysnap", tmp_snapshot_dir) is False


def test_list_notes(tmp_snapshot_dir):
    _save("a", tmp_snapshot_dir)
    _save("b", tmp_snapshot_dir)
    set_note("a", "note A", tmp_snapshot_dir)
    set_note("b", "note B", tmp_snapshot_dir)
    notes = list_notes(tmp_snapshot_dir)
    assert notes == {"a": "note A", "b": "note B"}


def test_list_notes_empty(tmp_snapshot_dir):
    assert list_notes(tmp_snapshot_dir) == {}


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def _dir_args(d):
    return ["--dir", d]


def test_cli_set_and_show(runner, tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    r = runner.invoke(notes_cmd, ["set"] + _dir_args(tmp_snapshot_dir) + ["snap1", "hello world"])
    assert r.exit_code == 0
    r2 = runner.invoke(notes_cmd, ["show"] + _dir_args(tmp_snapshot_dir) + ["snap1"])
    assert "hello world" in r2.output


def test_cli_list_empty(runner, tmp_snapshot_dir):
    r = runner.invoke(notes_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert "No notes" in r.output


def test_cli_delete_note(runner, tmp_snapshot_dir):
    _save("snap1", tmp_snapshot_dir)
    runner.invoke(notes_cmd, ["set"] + _dir_args(tmp_snapshot_dir) + ["snap1", "temp"])
    r = runner.invoke(notes_cmd, ["delete"] + _dir_args(tmp_snapshot_dir) + ["snap1"])
    assert "removed" in r.output
    r2 = runner.invoke(notes_cmd, ["show"] + _dir_args(tmp_snapshot_dir) + ["snap1"])
    assert "No note" in r2.output
