"""Tests for envforge.snapshot_copy."""
import pytest

from envforge.snapshot import save_snapshot, load_snapshot
from envforge.snapshot_copy import copy_keys, copy_all, CopyError


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name, vars_, d):
    save_snapshot(name, vars_, snapshot_dir=d)


def test_copy_keys_basic(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"A": "1", "B": "2", "C": "3"}, d)
    result = copy_keys("src", "dst", ["A", "C"], snapshot_dir=d)
    assert result == {"A": "1", "C": "3"}
    loaded = load_snapshot("dst", snapshot_dir=d)
    assert loaded["vars"] == {"A": "1", "C": "3"}


def test_copy_keys_missing_key_raises(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"A": "1"}, d)
    with pytest.raises(CopyError, match="NOPE"):
        copy_keys("src", "dst", ["NOPE"], snapshot_dir=d)


def test_copy_keys_merges_into_existing_dst(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"X": "10", "Y": "20"}, d)
    _save("dst", {"Z": "99"}, d)
    result = copy_keys("src", "dst", ["X"], snapshot_dir=d)
    assert result["Z"] == "99"
    assert result["X"] == "10"


def test_copy_keys_no_overwrite(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"A": "new"}, d)
    _save("dst", {"A": "original"}, d)
    result = copy_keys("src", "dst", ["A"], snapshot_dir=d, overwrite=False)
    assert result["A"] == "original"


def test_copy_keys_overwrite_default(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"A": "new"}, d)
    _save("dst", {"A": "original"}, d)
    result = copy_keys("src", "dst", ["A"], snapshot_dir=d)
    assert result["A"] == "new"


def test_copy_all(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"P": "1", "Q": "2"}, d)
    result = copy_all("src", "dst", snapshot_dir=d)
    assert result == {"P": "1", "Q": "2"}


def test_copy_all_no_overwrite_keeps_existing(tmp_snapshot_dir):
    d = tmp_snapshot_dir
    _save("src", {"K": "from_src", "L": "from_src"}, d)
    _save("dst", {"K": "keep_me"}, d)
    result = copy_all("src", "dst", snapshot_dir=d, overwrite=False)
    assert result["K"] == "keep_me"
    assert result["L"] == "from_src"
