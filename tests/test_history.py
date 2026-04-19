import pytest
from pathlib import Path
from envforge.history import record_event, get_history, clear_history
from envforge.snapshot import save_snapshot


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path


def test_record_and_get_history(tmp_snapshot_dir):
    save_snapshot("proj", {"KEY": "val"}, snapshot_dir=tmp_snapshot_dir)
    record_event(tmp_snapshot_dir, "proj", "saved")
    record_event(tmp_snapshot_dir, "proj", "loaded")
    history = get_history(tmp_snapshot_dir, "proj")
    assert len(history) == 2
    assert history[0]["event"] == "saved"
    assert history[1]["event"] == "loaded"
    assert "timestamp" in history[0]


def test_get_history_empty(tmp_snapshot_dir):
    history = get_history(tmp_snapshot_dir, "nonexistent")
    assert history == []


def test_clear_history(tmp_snapshot_dir):
    save_snapshot("proj", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    record_event(tmp_snapshot_dir, "proj", "saved")
    clear_history(tmp_snapshot_dir, "proj")
    assert get_history(tmp_snapshot_dir, "proj") == []


def test_clear_history_noop_if_missing(tmp_snapshot_dir):
    # should not raise
    clear_history(tmp_snapshot_dir, "ghost")


def test_multiple_events_accumulate(tmp_snapshot_dir):
    save_snapshot("x", {}, snapshot_dir=tmp_snapshot_dir)
    for event in ["saved", "loaded", "diffed", "exported"]:
        record_event(tmp_snapshot_dir, "x", event)
    history = get_history(tmp_snapshot_dir, "x")
    assert [h["event"] for h in history] == ["saved", "loaded", "diffed", "exported"]
