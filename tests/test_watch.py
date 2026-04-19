"""Tests for envforge.watch."""

import os
import pytest
from unittest.mock import patch
from envforge.snapshot import save_snapshot, load_snapshot
from envforge.watch import watch_env


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def test_watch_no_changes_no_autosave(tmp_snapshot_dir, capsys):
    env = {"FOO": "bar", "BAZ": "qux"}
    save_snapshot(tmp_snapshot_dir, "base", env)

    with patch.dict(os.environ, env, clear=True):
        watch_env(tmp_snapshot_dir, "base", interval=0, max_iterations=1, auto_save=False)

    out = capsys.readouterr().out
    assert "No changes" in out


def test_watch_detects_changes(tmp_snapshot_dir, capsys):
    env = {"FOO": "bar"}
    save_snapshot(tmp_snapshot_dir, "base", env)

    modified = {"FOO": "bar", "NEW_KEY": "new_val"}
    with patch.dict(os.environ, modified, clear=True):
        watch_env(tmp_snapshot_dir, "base", interval=0, max_iterations=1, auto_save=False)

    out = capsys.readouterr().out
    assert "Changes detected" in out


def test_watch_autosave_updates_snapshot(tmp_snapshot_dir, capsys):
    env = {"FOO": "original"}
    save_snapshot(tmp_snapshot_dir, "base", env)

    modified = {"FOO": "changed"}
    with patch.dict(os.environ, modified, clear=True):
        watch_env(tmp_snapshot_dir, "base", interval=0, max_iterations=1, auto_save=True)

    updated = load_snapshot(tmp_snapshot_dir, "base")
    assert updated["vars"]["FOO"] == "changed"
    out = capsys.readouterr().out
    assert "Auto-saved" in out


def test_watch_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        watch_env(tmp_snapshot_dir, "nonexistent", interval=0, max_iterations=1)
