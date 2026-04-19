"""Tests for envforge snapshot module."""

import json
import time
from pathlib import Path

import pytest

from envforge import snapshot as snap_mod
from envforge.snapshot import (
    capture_env,
    delete_snapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)


@pytest.fixture(autouse=True)
def tmp_snapshot_dir(tmp_path, monkeypatch):
    """Redirect snapshot storage to a temp directory."""
    monkeypatch.setattr(snap_mod, "SNAPSHOT_DIR", tmp_path / "snapshots")


def test_save_and_load_snapshot():
    env = {"FOO": "bar", "BAZ": "qux"}
    save_snapshot("mysnap", env, description="test snap")
    loaded = load_snapshot("mysnap")
    assert loaded["name"] == "mysnap"
    assert loaded["env"] == env
    assert loaded["description"] == "test snap"


def test_load_missing_snapshot_raises():
    with pytest.raises(FileNotFoundError, match="not found"):
        load_snapshot("nonexistent")


def test_list_snapshots_empty():
    assert list_snapshots() == []


def test_list_snapshots_returns_metadata():
    save_snapshot("a", {"X": "1"})
    save_snapshot("b", {"Y": "2", "Z": "3"})
    result = list_snapshots()
    names = [s["name"] for s in result]
    assert "a" in names and "b" in names
    b_entry = next(s for s in result if s["name"] == "b")
    assert b_entry["var_count"] == 2


def test_delete_snapshot():
    save_snapshot("todelete", {"K": "v"})
    assert delete_snapshot("todelete") is True
    with pytest.raises(FileNotFoundError):
        load_snapshot("todelete")


def test_delete_nonexistent_returns_false():
    assert delete_snapshot("ghost") is False


def test_capture_env_all(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "hello")
    env = capture_env()
    assert "TEST_VAR" in env
    assert env["TEST_VAR"] == "hello"


def test_capture_env_filtered(monkeypatch):
    monkeypatch.setenv("KEEP", "yes")
    monkeypatch.setenv("DROP", "no")
    env = capture_env(keys=["KEEP"])
    assert "KEEP" in env
    assert "DROP" not in env
