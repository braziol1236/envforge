"""CLI tests for the alias commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.snapshot import save_snapshot
from envforge.cli_alias import alias_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    d = tmp_path / ".envforge"
    d.mkdir()
    return str(d)


@pytest.fixture()
def _dir_args(tmp_snapshot_dir):
    save_snapshot("prod", {"APP_ENV": "production"}, tmp_snapshot_dir)
    save_snapshot("dev", {"APP_ENV": "development"}, tmp_snapshot_dir)
    return ["--dir", tmp_snapshot_dir]


def test_set_and_show(runner, _dir_args):
    r = runner.invoke(alias_cmd, ["set", "p", "prod"] + _dir_args)
    assert r.exit_code == 0
    assert "saved" in r.output

    r = runner.invoke(alias_cmd, ["show", "p"] + _dir_args)
    assert r.exit_code == 0
    assert "prod" in r.output


def test_list_aliases(runner, _dir_args):
    runner.invoke(alias_cmd, ["set", "p", "prod"] + _dir_args)
    runner.invoke(alias_cmd, ["set", "d", "dev"] + _dir_args)
    r = runner.invoke(alias_cmd, ["list"] + _dir_args)
    assert r.exit_code == 0
    assert "prod" in r.output
    assert "dev" in r.output


def test_list_empty(runner, tmp_snapshot_dir):
    r = runner.invoke(alias_cmd, ["list", "--dir", tmp_snapshot_dir])
    assert r.exit_code == 0
    assert "No aliases" in r.output


def test_remove_alias(runner, _dir_args):
    runner.invoke(alias_cmd, ["set", "p", "prod"] + _dir_args)
    r = runner.invoke(alias_cmd, ["remove", "p"] + _dir_args)
    assert r.exit_code == 0
    assert "removed" in r.output


def test_set_missing_snapshot_fails(runner, _dir_args):
    r = runner.invoke(alias_cmd, ["set", "x", "ghost"] + _dir_args)
    assert r.exit_code != 0


def test_show_missing_alias_fails(runner, _dir_args):
    r = runner.invoke(alias_cmd, ["show", "nope"] + _dir_args)
    assert r.exit_code != 0
