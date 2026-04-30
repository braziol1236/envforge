"""Tests for envforge.snapshot_labels."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_labels import labels_cmd
from envforge.snapshot import save_snapshot
from envforge.snapshot_labels import (
    LabelError,
    find_by_label,
    get_labels,
    remove_label,
    set_label,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(snapshot_dir, name, vars=None):
    save_snapshot(snapshot_dir, name, vars or {"K": "v"})


def test_set_and_get_label(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    set_label(tmp_snapshot_dir, "snap1", "env", "production")
    labels = get_labels(tmp_snapshot_dir, "snap1")
    assert labels == {"env": "production"}


def test_set_multiple_labels(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    set_label(tmp_snapshot_dir, "snap1", "env", "staging")
    set_label(tmp_snapshot_dir, "snap1", "team", "backend")
    labels = get_labels(tmp_snapshot_dir, "snap1")
    assert labels["env"] == "staging"
    assert labels["team"] == "backend"


def test_set_label_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(LabelError):
        set_label(tmp_snapshot_dir, "ghost", "env", "prod")


def test_remove_existing_label(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    set_label(tmp_snapshot_dir, "snap1", "env", "prod")
    removed = remove_label(tmp_snapshot_dir, "snap1", "env")
    assert removed is True
    assert get_labels(tmp_snapshot_dir, "snap1") == {}


def test_remove_nonexistent_label_returns_false(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    assert remove_label(tmp_snapshot_dir, "snap1", "missing") is False


def test_get_labels_empty(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    assert get_labels(tmp_snapshot_dir, "snap1") == {}


def test_find_by_label_key_only(tmp_snapshot_dir):
    for name in ("a", "b", "c"):
        _save(tmp_snapshot_dir, name)
    set_label(tmp_snapshot_dir, "a", "env", "prod")
    set_label(tmp_snapshot_dir, "b", "env", "dev")
    set_label(tmp_snapshot_dir, "c", "team", "ops")
    results = find_by_label(tmp_snapshot_dir, "env")
    assert set(results) == {"a", "b"}


def test_find_by_label_key_and_value(tmp_snapshot_dir):
    for name in ("x", "y"):
        _save(tmp_snapshot_dir, name)
    set_label(tmp_snapshot_dir, "x", "env", "prod")
    set_label(tmp_snapshot_dir, "y", "env", "dev")
    results = find_by_label(tmp_snapshot_dir, "env", "prod")
    assert results == ["x"]


def test_cli_set_and_show(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    runner = CliRunner()
    res = runner.invoke(
        labels_cmd, ["set", "snap1", "env", "prod", "--dir", tmp_snapshot_dir]
    )
    assert res.exit_code == 0
    res2 = runner.invoke(labels_cmd, ["show", "snap1", "--dir", tmp_snapshot_dir])
    assert "env=prod" in res2.output


def test_cli_find(tmp_snapshot_dir):
    _save(tmp_snapshot_dir, "snap1")
    _save(tmp_snapshot_dir, "snap2")
    runner = CliRunner()
    runner.invoke(labels_cmd, ["set", "snap1", "tier", "gold", "--dir", tmp_snapshot_dir])
    runner.invoke(labels_cmd, ["set", "snap2", "tier", "silver", "--dir", tmp_snapshot_dir])
    res = runner.invoke(
        labels_cmd, ["find", "tier", "--value", "gold", "--dir", tmp_snapshot_dir]
    )
    assert "snap1" in res.output
    assert "snap2" not in res.output
