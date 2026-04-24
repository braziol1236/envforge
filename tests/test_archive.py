"""Tests for envforge.archive."""

import pytest
from pathlib import Path

from envforge.snapshot import save_snapshot
from envforge.archive import archive_snapshots, restore_archive, list_archive_contents


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _save(name, vars_, d):
    save_snapshot(name, vars_, snapshot_dir=d)


def test_archive_creates_zip(tmp_snapshot_dir, tmp_path):
    _save("dev", {"FOO": "bar"}, tmp_snapshot_dir)
    out = archive_snapshots(["dev"], tmp_path / "bundle", snapshot_dir=tmp_snapshot_dir)
    assert out.exists()
    assert out.suffix == ".zip"


def test_archive_multiple_snapshots(tmp_snapshot_dir, tmp_path):
    _save("dev", {"FOO": "1"}, tmp_snapshot_dir)
    _save("prod", {"BAR": "2"}, tmp_snapshot_dir)
    out = archive_snapshots(["dev", "prod"], tmp_path / "multi.zip", snapshot_dir=tmp_snapshot_dir)
    contents = list_archive_contents(out)
    assert set(contents) == {"dev", "prod"}


def test_list_archive_contents(tmp_snapshot_dir, tmp_path):
    _save("staging", {"X": "y"}, tmp_snapshot_dir)
    out = archive_snapshots(["staging"], tmp_path / "s.zip", snapshot_dir=tmp_snapshot_dir)
    names = list_archive_contents(out)
    assert names == ["staging"]


def test_restore_archive(tmp_snapshot_dir, tmp_path):
    _save("dev", {"FOO": "bar", "PORT": "8080"}, tmp_snapshot_dir)
    out = archive_snapshots(["dev"], tmp_path / "b.zip", snapshot_dir=tmp_snapshot_dir)

    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()
    restored = restore_archive(out, snapshot_dir=restore_dir)
    assert restored == ["dev"]

    snap_file = restore_dir / "dev.json"
    assert snap_file.exists()


def test_restore_raises_on_existing_without_overwrite(tmp_snapshot_dir, tmp_path):
    _save("dev", {"A": "1"}, tmp_snapshot_dir)
    out = archive_snapshots(["dev"], tmp_path / "b.zip", snapshot_dir=tmp_snapshot_dir)

    with pytest.raises(FileExistsError, match="dev"):
        restore_archive(out, snapshot_dir=tmp_snapshot_dir, overwrite=False)


def test_restore_with_overwrite(tmp_snapshot_dir, tmp_path):
    _save("dev", {"A": "old"}, tmp_snapshot_dir)
    out = archive_snapshots(["dev"], tmp_path / "b.zip", snapshot_dir=tmp_snapshot_dir)
    _save("dev", {"A": "new"}, tmp_snapshot_dir)

    restored = restore_archive(out, snapshot_dir=tmp_snapshot_dir, overwrite=True)
    assert "dev" in restored


def test_list_archive_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        list_archive_contents(tmp_path / "nope.zip")


def test_restore_missing_archive_raises(tmp_path, tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        restore_archive(tmp_path / "ghost.zip", snapshot_dir=tmp_snapshot_dir)
