"""Tests for envforge.rollback."""

import pytest

from envforge.rollback import get_rollback_candidates, rollback_snapshot
from envforge.snapshot import save_snapshot, load_snapshot
from envforge.history import record_event


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def test_rollback_candidates_empty_when_no_history(tmp_snapshot_dir):
    candidates = get_rollback_candidates("mysnap", tmp_snapshot_dir)
    assert candidates == []


def test_rollback_candidates_filters_by_name(tmp_snapshot_dir):
    record_event(tmp_snapshot_dir, "mysnap", "save", vars={"A": "1"})
    record_event(tmp_snapshot_dir, "other", "save", vars={"B": "2"})
    candidates = get_rollback_candidates("mysnap", tmp_snapshot_dir)
    assert len(candidates) == 1
    assert candidates[0]["snapshot"] == "mysnap"


def test_rollback_restores_previous_vars(tmp_snapshot_dir):
    # Record an old state in history
    old_vars = {"FOO": "old", "BAR": "123"}
    record_event(tmp_snapshot_dir, "snap", "save", vars=old_vars)

    # Save a newer state as the current snapshot
    new_vars = {"FOO": "new", "BAR": "999"}
    save_snapshot("snap", new_vars, tmp_snapshot_dir)

    restored = rollback_snapshot("snap", tmp_snapshot_dir, steps=1)
    assert restored == old_vars

    on_disk = load_snapshot("snap", tmp_snapshot_dir)
    assert on_disk == old_vars


def test_rollback_raises_if_not_enough_history(tmp_snapshot_dir):
    save_snapshot("snap", {"X": "1"}, tmp_snapshot_dir)
    with pytest.raises(ValueError, match="Not enough history"):
        rollback_snapshot("snap", tmp_snapshot_dir, steps=3)


def test_rollback_multiple_steps(tmp_snapshot_dir):
    v1 = {"VER": "1"}
    v2 = {"VER": "2"}
    record_event(tmp_snapshot_dir, "snap", "save", vars=v1)
    record_event(tmp_snapshot_dir, "snap", "save", vars=v2)
    save_snapshot("snap", {"VER": "3"}, tmp_snapshot_dir)

    restored = rollback_snapshot("snap", tmp_snapshot_dir, steps=2)
    assert restored == v1
