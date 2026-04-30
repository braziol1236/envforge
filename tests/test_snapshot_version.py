"""Tests for envforge.snapshot_version."""

from __future__ import annotations

from pathlib import Path

import pytest

from envforge.snapshot import save_snapshot
from envforge.snapshot_version import (
    VersionError,
    commit_version,
    delete_versions,
    get_version,
    list_versions,
    restore_version,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envforge"
    d.mkdir()
    return d


def _save(name: str, d: Path, vars: dict) -> None:
    save_snapshot(name, vars, d)


def test_commit_version_increments(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"A": "1"})
    v1 = commit_version("proj", tmp_snapshot_dir, "initial")
    assert v1 == 1
    _save("proj", tmp_snapshot_dir, {"A": "2"})
    v2 = commit_version("proj", tmp_snapshot_dir)
    assert v2 == 2


def test_list_versions_empty(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"X": "y"})
    assert list_versions("proj", tmp_snapshot_dir) == []


def test_list_versions_returns_all(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"A": "1"})
    commit_version("proj", tmp_snapshot_dir, "first")
    _save("proj", tmp_snapshot_dir, {"A": "2"})
    commit_version("proj", tmp_snapshot_dir, "second")
    versions = list_versions("proj", tmp_snapshot_dir)
    assert len(versions) == 2
    assert versions[0]["version"] == 1
    assert versions[1]["version"] == 2


def test_get_version_returns_correct_vars(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"ENV": "dev"})
    commit_version("proj", tmp_snapshot_dir)
    _save("proj", tmp_snapshot_dir, {"ENV": "prod"})
    commit_version("proj", tmp_snapshot_dir)
    v1 = get_version("proj", 1, tmp_snapshot_dir)
    assert v1["vars"]["ENV"] == "dev"
    v2 = get_version("proj", 2, tmp_snapshot_dir)
    assert v2["vars"]["ENV"] == "prod"


def test_get_version_missing_raises(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"A": "1"})
    commit_version("proj", tmp_snapshot_dir)
    with pytest.raises(VersionError, match="Version 99"):
        get_version("proj", 99, tmp_snapshot_dir)


def test_restore_version_overwrites_live(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"MODE": "alpha"})
    commit_version("proj", tmp_snapshot_dir)
    _save("proj", tmp_snapshot_dir, {"MODE": "beta"})
    commit_version("proj", tmp_snapshot_dir)
    restore_version("proj", 1, tmp_snapshot_dir)
    from envforge.snapshot import load_snapshot
    snap = load_snapshot("proj", tmp_snapshot_dir)
    assert snap["vars"]["MODE"] == "alpha"


def test_delete_versions_removes_all(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"K": "v"})
    commit_version("proj", tmp_snapshot_dir)
    commit_version("proj", tmp_snapshot_dir)
    removed = delete_versions("proj", tmp_snapshot_dir)
    assert removed == 2
    assert list_versions("proj", tmp_snapshot_dir) == []


def test_delete_versions_noop_when_none(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"K": "v"})
    removed = delete_versions("proj", tmp_snapshot_dir)
    assert removed == 0


def test_version_message_stored(tmp_snapshot_dir):
    _save("proj", tmp_snapshot_dir, {"A": "1"})
    commit_version("proj", tmp_snapshot_dir, "my message")
    v = get_version("proj", 1, tmp_snapshot_dir)
    assert v["message"] == "my message"
