import pytest
from envforge.snapshot import save_snapshot
from envforge.pin import (
    pin_snapshot, unpin, resolve_pin, list_pins, load_pinned
)


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def _dir(tmp_snapshot_dir):
    save_snapshot("snap1", {"A": "1", "B": "2"}, tmp_snapshot_dir)
    save_snapshot("snap2", {"X": "9"}, tmp_snapshot_dir)
    return tmp_snapshot_dir


def test_pin_and_resolve(_dir):
    pin_snapshot("stable", "snap1", _dir)
    assert resolve_pin("stable", _dir) == "snap1"


def test_pin_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        pin_snapshot("stable", "ghost", tmp_snapshot_dir)


def test_unpin(_dir):
    pin_snapshot("stable", "snap1", _dir)
    unpin("stable", _dir)
    assert "stable" not in list_pins(_dir)


def test_unpin_nonexistent_raises(_dir):
    with pytest.raises(KeyError):
        unpin("nope", _dir)


def test_list_pins_empty(tmp_snapshot_dir):
    assert list_pins(tmp_snapshot_dir) == {}


def test_list_pins_multiple(_dir):
    pin_snapshot("stable", "snap1", _dir)
    pin_snapshot("prod", "snap2", _dir)
    pins = list_pins(_dir)
    assert pins["stable"] == "snap1"
    assert pins["prod"] == "snap2"


def test_load_pinned_returns_env(_dir):
    pin_snapshot("stable", "snap1", _dir)
    env = load_pinned("stable", _dir)
    assert env["A"] == "1"


def test_overwrite_pin(_dir):
    pin_snapshot("stable", "snap1", _dir)
    pin_snapshot("stable", "snap2", _dir)
    assert resolve_pin("stable", _dir) == "snap2"
