"""Tests for envforge.snapshot_rename."""

import pytest
from pathlib import Path
from envforge.snapshot import save_snapshot, load_snapshot, get_snapshot_path
from envforge.snapshot_rename import rename_snapshot, RenameError


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _save(name, vars_, d):
    save_snapshot(name, vars_, d)


def test_rename_basic(tmp_snapshot_dir):
    _save("alpha", {"FOO": "bar"}, tmp_snapshot_dir)
    rename_snapshot("alpha", "beta", tmp_snapshot_dir)

    assert not get_snapshot_path("alpha", tmp_snapshot_dir).exists()
    data = load_snapshot("beta", tmp_snapshot_dir)
    assert data["vars"] == {"FOO": "bar"}


def test_rename_missing_source_raises(tmp_snapshot_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_snapshot("ghost", "new", tmp_snapshot_dir)


def test_rename_target_exists_raises(tmp_snapshot_dir):
    _save("src", {"A": "1"}, tmp_snapshot_dir)
    _save("dst", {"B": "2"}, tmp_snapshot_dir)

    with pytest.raises(RenameError, match="already exists"):
        rename_snapshot("src", "dst", tmp_snapshot_dir)


def test_rename_target_exists_overwrite(tmp_snapshot_dir):
    _save("src", {"A": "1"}, tmp_snapshot_dir)
    _save("dst", {"B": "2"}, tmp_snapshot_dir)

    rename_snapshot("src", "dst", tmp_snapshot_dir, overwrite=True)
    data = load_snapshot("dst", tmp_snapshot_dir)
    assert data["vars"] == {"A": "1"}


def test_rename_preserves_vars(tmp_snapshot_dir):
    vars_ = {"KEY1": "val1", "KEY2": "val2", "KEY3": "val3"}
    _save("snap", vars_, tmp_snapshot_dir)
    rename_snapshot("snap", "snap_new", tmp_snapshot_dir)

    loaded = load_snapshot("snap_new", tmp_snapshot_dir)
    assert loaded["vars"] == vars_


def test_rename_migrates_aliases(tmp_snapshot_dir):
    from envforge.alias import set_alias, resolve_alias

    _save("mysnap", {"X": "1"}, tmp_snapshot_dir)
    set_alias("prod", "mysnap", tmp_snapshot_dir)

    rename_snapshot("mysnap", "mysnap_v2", tmp_snapshot_dir)
    assert resolve_alias("prod", tmp_snapshot_dir) == "mysnap_v2"


def test_rename_no_migrate_aliases(tmp_snapshot_dir):
    from envforge.alias import set_alias, resolve_alias

    _save("mysnap", {"X": "1"}, tmp_snapshot_dir)
    set_alias("prod", "mysnap", tmp_snapshot_dir)

    rename_snapshot("mysnap", "mysnap_v2", tmp_snapshot_dir, migrate_aliases=False)
    # alias still points to old name
    assert resolve_alias("prod", tmp_snapshot_dir) == "mysnap"
