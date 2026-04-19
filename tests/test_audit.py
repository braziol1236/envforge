"""Tests for envforge.audit module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.audit import record_audit, get_audit_log, clear_audit_log


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


def test_empty_audit_log(tmp_snapshot_dir):
    assert get_audit_log(tmp_snapshot_dir) == []


def test_record_and_retrieve(tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "mysnap", user="alice")
    entries = get_audit_log(tmp_snapshot_dir)
    assert len(entries) == 1
    assert entries[0]["action"] == "save"
    assert entries[0]["snapshot"] == "mysnap"
    assert entries[0]["user"] == "alice"
    assert "timestamp" in entries[0]


def test_record_with_note(tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "delete", "oldsnap", user="bob", note="cleanup")
    entries = get_audit_log(tmp_snapshot_dir)
    assert entries[0]["note"] == "cleanup"


def test_filter_by_snapshot(tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "snap_a", user="alice")
    record_audit(tmp_snapshot_dir, "load", "snap_b", user="alice")
    record_audit(tmp_snapshot_dir, "save", "snap_a", user="bob")

    results = get_audit_log(tmp_snapshot_dir, snapshot_name="snap_a")
    assert len(results) == 2
    assert all(e["snapshot"] == "snap_a" for e in results)


def test_multiple_actions_preserved(tmp_snapshot_dir):
    for action in ["save", "load", "delete"]:
        record_audit(tmp_snapshot_dir, action, "snap", user="ci")
    entries = get_audit_log(tmp_snapshot_dir)
    assert [e["action"] for e in entries] == ["save", "load", "delete"]


def test_clear_audit_log(tmp_snapshot_dir):
    record_audit(tmp_snapshot_dir, "save", "snap", user="alice")
    clear_audit_log(tmp_snapshot_dir)
    assert get_audit_log(tmp_snapshot_dir) == []


def test_clear_noop_if_missing(tmp_snapshot_dir):
    # Should not raise even if file doesn't exist
    clear_audit_log(tmp_snapshot_dir)
    assert get_audit_log(tmp_snapshot_dir) == []
