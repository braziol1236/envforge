"""Tests for envforge.alias."""
from __future__ import annotations

import pytest

from envforge.snapshot import save_snapshot
from envforge.alias import (
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    resolve_name_or_alias,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


@pytest.fixture()
def _dir(tmp_snapshot_dir):
    save_snapshot("prod", {"APP_ENV": "production"}, tmp_snapshot_dir)
    save_snapshot("dev", {"APP_ENV": "development"}, tmp_snapshot_dir)
    return tmp_snapshot_dir


def test_set_and_resolve_alias(_dir):
    set_alias("p", "prod", _dir)
    assert resolve_alias("p", _dir) == "prod"


def test_set_alias_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        set_alias("ghost", "nonexistent", tmp_snapshot_dir)


def test_remove_existing_alias(_dir):
    set_alias("p", "prod", _dir)
    result = remove_alias("p", _dir)
    assert result is True
    assert resolve_alias("p", _dir) is None


def test_remove_nonexistent_alias_returns_false(_dir):
    assert remove_alias("nope", _dir) is False


def test_list_aliases_empty(tmp_snapshot_dir):
    assert list_aliases(tmp_snapshot_dir) == {}


def test_list_aliases_multiple(_dir):
    set_alias("p", "prod", _dir)
    set_alias("d", "dev", _dir)
    result = list_aliases(_dir)
    assert result == {"p": "prod", "d": "dev"}


def test_overwrite_alias(_dir):
    set_alias("env", "prod", _dir)
    set_alias("env", "dev", _dir)
    assert resolve_alias("env", _dir) == "dev"


def test_resolve_name_or_alias_with_alias(_dir):
    set_alias("p", "prod", _dir)
    assert resolve_name_or_alias("p", _dir) == "prod"


def test_resolve_name_or_alias_without_alias(_dir):
    assert resolve_name_or_alias("prod", _dir) == "prod"
