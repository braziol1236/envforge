"""Tests for envforge.promote."""

from __future__ import annotations

import pytest

from envforge.snapshot import save_snapshot, load_snapshot
from envforge.promote import promote_snapshot, list_tiers, _tier_snapshot_name


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def test_tier_snapshot_name():
    assert _tier_snapshot_name("myapp", "staging") == "myapp:staging"


def test_promote_copies_vars(tmp_snapshot_dir, _dir):
    save_snapshot("myapp:dev", {"FOO": "bar", "DB": "dev_db"}, **_dir)
    result = promote_snapshot("myapp", "dev", "staging", snapshot_dir=tmp_snapshot_dir)
    assert result == {"FOO": "bar", "DB": "dev_db"}
    loaded = load_snapshot("myapp:staging", **_dir)
    assert loaded == {"FOO": "bar", "DB": "dev_db"}


def test_promote_with_overrides(tmp_snapshot_dir, _dir):
    save_snapshot("myapp:dev", {"FOO": "bar", "DB": "dev_db"}, **_dir)
    result = promote_snapshot(
        "myapp", "dev", "staging",
        overrides={"DB": "staging_db"},
        snapshot_dir=tmp_snapshot_dir,
    )
    assert result["DB"] == "staging_db"
    assert result["FOO"] == "bar"
    loaded = load_snapshot("myapp:staging", **_dir)
    assert loaded["DB"] == "staging_db"


def test_promote_does_not_mutate_source(tmp_snapshot_dir, _dir):
    save_snapshot("myapp:dev", {"X": "1"}, **_dir)
    promote_snapshot("myapp", "dev", "staging", overrides={"X": "999"}, snapshot_dir=tmp_snapshot_dir)
    src = load_snapshot("myapp:dev", **_dir)
    assert src["X"] == "1"


def test_promote_missing_source_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        promote_snapshot("ghost", "dev", "staging", snapshot_dir=tmp_snapshot_dir)


def test_list_tiers_returns_existing(tmp_snapshot_dir, _dir):
    save_snapshot("myapp:dev", {"A": "1"}, **_dir)
    save_snapshot("myapp:prod", {"A": "2"}, **_dir)
    tiers = list_tiers("myapp", snapshot_dir=tmp_snapshot_dir)
    assert "dev" in tiers
    assert "prod" in tiers
    assert "staging" not in tiers


def test_list_tiers_empty_when_none_exist(tmp_snapshot_dir):
    tiers = list_tiers("ghost", snapshot_dir=tmp_snapshot_dir)
    assert tiers == []


def test_list_tiers_custom_tier_list(tmp_snapshot_dir, _dir):
    save_snapshot("app:alpha", {"K": "v"}, **_dir)
    tiers = list_tiers("app", tiers=["alpha", "beta"], snapshot_dir=tmp_snapshot_dir)
    assert tiers == ["alpha"]
