"""Tests for envforge.compare module."""
import os
import pytest
from click.testing import CliRunner
from envforge.snapshot import save_snapshot
from envforge.compare import compare_two, compare_with_env, format_diff
from envforge.cli_compare import compare_cmd


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def test_compare_two_added(tmp_snapshot_dir):
    save_snapshot("a", {"X": "1"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("b", {"X": "1", "Y": "2"}, snapshot_dir=tmp_snapshot_dir)
    diff = compare_two("a", "b", snapshot_dir=tmp_snapshot_dir)
    assert "Y" in diff.added
    assert not diff.removed
    assert not diff.changed


def test_compare_two_removed(tmp_snapshot_dir):
    save_snapshot("a", {"X": "1", "Y": "2"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("b", {"X": "1"}, snapshot_dir=tmp_snapshot_dir)
    diff = compare_two("a", "b", snapshot_dir=tmp_snapshot_dir)
    assert "Y" in diff.removed


def test_compare_two_changed(tmp_snapshot_dir):
    save_snapshot("a", {"X": "1"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("b", {"X": "2"}, snapshot_dir=tmp_snapshot_dir)
    diff = compare_two("a", "b", snapshot_dir=tmp_snapshot_dir)
    assert "X" in diff.changed


def test_compare_with_env(tmp_snapshot_dir, monkeypatch):
    monkeypatch.setenv("FORGE_TEST_KEY", "hello")
    save_snapshot("base", {"FORGE_TEST_KEY": "world"}, snapshot_dir=tmp_snapshot_dir)
    diff = compare_with_env("base", snapshot_dir=tmp_snapshot_dir)
    assert "FORGE_TEST_KEY" in diff.changed


def test_format_diff_no_changes(tmp_snapshot_dir):
    save_snapshot("x", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("y", {"A": "1"}, snapshot_dir=tmp_snapshot_dir)
    diff = compare_two("x", "y", snapshot_dir=tmp_snapshot_dir)
    assert format_diff(diff) == "No differences found."


def test_cli_compare_snapshots(tmp_snapshot_dir):
    runner = CliRunner()
    save_snapshot("s1", {"FOO": "bar"}, snapshot_dir=tmp_snapshot_dir)
    save_snapshot("s2", {"FOO": "baz"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(compare_cmd, ["snapshots", "s1", "s2", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_cli_compare_missing_snapshot(tmp_snapshot_dir):
    runner = CliRunner()
    result = runner.invoke(compare_cmd, ["snapshots", "ghost", "also_ghost", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 1
