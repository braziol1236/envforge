import pytest
from envforge.clone import clone_snapshot, rename_snapshot
from envforge.snapshot import save_snapshot, load_snapshot, list_snapshots


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir(d):
    return {"snapshot_dir": d}


def test_clone_creates_new_snapshot(tmp_snapshot_dir):
    save_snapshot("original", {"FOO": "bar", "BAZ": "qux"}, **_dir(tmp_snapshot_dir))
    env = clone_snapshot("original", "copy", snapshot_dir=tmp_snapshot_dir)
    loaded = load_snapshot("copy", **_dir(tmp_snapshot_dir))
    assert loaded["env"] == {"FOO": "bar", "BAZ": "qux"}
    assert env == {"FOO": "bar", "BAZ": "qux"}


def test_clone_with_overrides(tmp_snapshot_dir):
    save_snapshot("base", {"FOO": "1", "BAR": "2"}, **_dir(tmp_snapshot_dir))
    clone_snapshot("base", "modified", overrides={"FOO": "99", "NEW": "val"}, snapshot_dir=tmp_snapshot_dir)
    loaded = load_snapshot("modified", **_dir(tmp_snapshot_dir))
    assert loaded["env"]["FOO"] == "99"
    assert loaded["env"]["BAR"] == "2"
    assert loaded["env"]["NEW"] == "val"


def test_clone_does_not_mutate_source(tmp_snapshot_dir):
    save_snapshot("src", {"X": "1"}, **_dir(tmp_snapshot_dir))
    clone_snapshot("src", "dst", overrides={"X": "2"}, snapshot_dir=tmp_snapshot_dir)
    src = load_snapshot("src", **_dir(tmp_snapshot_dir))
    assert src["env"]["X"] == "1"


def test_clone_missing_source_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        clone_snapshot("ghost", "new", snapshot_dir=tmp_snapshot_dir)


def test_rename_snapshot(tmp_snapshot_dir):
    save_snapshot("old", {"K": "v"}, **_dir(tmp_snapshot_dir))
    rename_snapshot("old", "new", snapshot_dir=tmp_snapshot_dir)
    names = [s["name"] for s in list_snapshots(**_dir(tmp_snapshot_dir))]
    assert "new" in names
    assert "old" not in names


def test_rename_missing_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        rename_snapshot("nope", "something", snapshot_dir=tmp_snapshot_dir)
