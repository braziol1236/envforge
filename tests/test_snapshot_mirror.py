"""Tests for envforge.snapshot_mirror."""

import json
import pytest
from pathlib import Path

from envforge.snapshot import save_snapshot
from envforge.snapshot_mirror import (
    mirror_to_path,
    mirror_all,
    restore_from_mirror,
    list_mirror_contents,
    MirrorError,
)


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def _save(name, vars_, snap_dir):
    save_snapshot(name, vars_, base_dir=snap_dir)


def test_mirror_to_path_creates_file(tmp_snapshot_dir, tmp_path):
    _save("dev", {"FOO": "bar"}, tmp_snapshot_dir)
    dest = tmp_path / "mirror"
    result = mirror_to_path("dev", dest, snapshot_dir=tmp_snapshot_dir)
    assert result.exists()
    assert result.name == "dev.json"
    data = json.loads(result.read_text())
    assert data["vars"]["FOO"] == "bar"


def test_mirror_to_path_missing_snapshot_raises(tmp_snapshot_dir, tmp_path):
    with pytest.raises(MirrorError, match="does not exist"):
        mirror_to_path("ghost", tmp_path / "mirror", snapshot_dir=tmp_snapshot_dir)


def test_mirror_all_copies_all_snapshots(tmp_snapshot_dir, tmp_path):
    _save("alpha", {"A": "1"}, tmp_snapshot_dir)
    _save("beta", {"B": "2"}, tmp_snapshot_dir)
    dest = tmp_path / "mirror"
    copied = mirror_all(dest, snapshot_dir=tmp_snapshot_dir)
    names = {p.stem for p in copied}
    assert names == {"alpha", "beta"}


def test_mirror_all_empty_dir(tmp_snapshot_dir, tmp_path):
    tmp_snapshot_dir.mkdir(parents=True, exist_ok=True)
    dest = tmp_path / "mirror"
    copied = mirror_all(dest, snapshot_dir=tmp_snapshot_dir)
    assert copied == []


def test_restore_from_mirror(tmp_snapshot_dir, tmp_path):
    mirror_dir = tmp_path / "mirror"
    _save("prod", {"ENV": "production"}, tmp_snapshot_dir)
    mirror_to_path("prod", mirror_dir, snapshot_dir=tmp_snapshot_dir)

    new_snap_dir = tmp_path / "restored"
    vars_ = restore_from_mirror("prod", mirror_dir, snapshot_dir=new_snap_dir)
    assert vars_["ENV"] == "production"
    restored_file = new_snap_dir / "prod.json"
    assert restored_file.exists()


def test_restore_from_mirror_missing_raises(tmp_path):
    with pytest.raises(MirrorError, match="not found in mirror"):
        restore_from_mirror("nope", tmp_path / "empty", snapshot_dir=tmp_path / "snaps")


def test_list_mirror_contents(tmp_snapshot_dir, tmp_path):
    _save("x", {}, tmp_snapshot_dir)
    _save("y", {}, tmp_snapshot_dir)
    dest = tmp_path / "mirror"
    mirror_all(dest, snapshot_dir=tmp_snapshot_dir)
    names = list_mirror_contents(dest)
    assert names == ["x", "y"]


def test_list_mirror_contents_nonexistent_dir(tmp_path):
    result = list_mirror_contents(tmp_path / "no_such_dir")
    assert result == []
