"""Tests for envforge.diff module."""

import pytest
from envforge.diff import diff_snapshots, diff_snapshot_with_env, EnvDiff


def make_snapshot(vars_dict):
    return {"vars": vars_dict, "metadata": {}}


def test_diff_no_changes():
    snap = make_snapshot({"FOO": "bar", "BAZ": "qux"})
    result = diff_snapshots(snap, snap)
    assert not result.has_changes


def test_diff_added_keys():
    a = make_snapshot({"FOO": "1"})
    b = make_snapshot({"FOO": "1", "NEW_VAR": "hello"})
    result = diff_snapshots(a, b)
    assert result.added == {"NEW_VAR": "hello"}
    assert not result.removed
    assert not result.changed


def test_diff_removed_keys():
    a = make_snapshot({"FOO": "1", "OLD": "gone"})
    b = make_snapshot({"FOO": "1"})
    result = diff_snapshots(a, b)
    assert result.removed == {"OLD": "gone"}
    assert not result.added
    assert not result.changed


def test_diff_changed_keys():
    a = make_snapshot({"FOO": "old"})
    b = make_snapshot({"FOO": "new"})
    result = diff_snapshots(a, b)
    assert result.changed == {"FOO": ("old", "new")}
    assert not result.added
    assert not result.removed


def test_diff_has_changes_true():
    a = make_snapshot({"A": "1"})
    b = make_snapshot({"B": "2"})
    result = diff_snapshots(a, b)
    assert result.has_changes


def test_summary_no_changes():
    snap = make_snapshot({"X": "y"})
    result = diff_snapshots(snap, snap)
    assert result.summary() == "  (no differences)"


def test_summary_contains_symbols():
    a = make_snapshot({"OLD": "v", "SHARED": "x"})
    b = make_snapshot({"NEW": "w", "SHARED": "y"})
    result = diff_snapshots(a, b)
    summary = result.summary()
    assert "+ NEW=w" in summary
    assert "- OLD=v" in summary
    assert "~ SHARED" in summary


def test_diff_with_env():
    snap = make_snapshot({"FAKE_VAR_XYZ": "123"})
    fake_env = {"FAKE_VAR_XYZ": "999", "EXTRA": "yes"}
    result = diff_snapshot_with_env(snap, env=fake_env)
    assert result.changed.get("FAKE_VAR_XYZ") == ("123", "999")
    assert "EXTRA" in result.added
