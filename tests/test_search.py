"""Tests for envforge.search."""

import pytest
from click.testing import CliRunner

from envforge.cli_search import search_cmd
from envforge.search import format_results, search_by_key, search_by_value
from envforge.snapshot import save_snapshot


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture(autouse=True)
def _populate(tmp_snapshot_dir):
    save_snapshot(
        "dev",
        {"AWS_REGION": "us-east-1", "DB_HOST": "localhost", "DEBUG": "true"},
        snapshot_dir=tmp_snapshot_dir,
    )
    save_snapshot(
        "prod",
        {"AWS_REGION": "eu-west-1", "AWS_SECRET": "s3cr3t", "DEBUG": "false"},
        snapshot_dir=tmp_snapshot_dir,
    )


def test_search_by_key_glob_matches(tmp_snapshot_dir):
    results = search_by_key("AWS_*", snapshot_dir=tmp_snapshot_dir)
    names = {r.name for r in results}
    assert names == {"dev", "prod"}
    for r in results:
        assert all(k.startswith("AWS_") for k in r.matches)


def test_search_by_key_no_match(tmp_snapshot_dir):
    results = search_by_key("NONEXISTENT_*", snapshot_dir=tmp_snapshot_dir)
    assert results == []


def test_search_by_key_exact(tmp_snapshot_dir):
    results = search_by_key("DB_HOST", snapshot_dir=tmp_snapshot_dir)
    assert len(results) == 1
    assert results[0].name == "dev"


def test_search_by_value_regex(tmp_snapshot_dir):
    results = search_by_value(r"us-.*-\d", snapshot_dir=tmp_snapshot_dir)
    assert len(results) == 1
    assert results[0].name == "dev"
    assert "AWS_REGION" in results[0].matches


def test_search_by_value_no_match(tmp_snapshot_dir):
    results = search_by_value("zzznope", snapshot_dir=tmp_snapshot_dir)
    assert results == []


def test_format_results_empty():
    assert format_results([]) == "No matches found."


def test_format_results_shows_kv(tmp_snapshot_dir):
    results = search_by_key("DEBUG", snapshot_dir=tmp_snapshot_dir)
    output = format_results(results)
    assert "DEBUG=true" in output or "DEBUG=false" in output


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_search_key(runner, tmp_snapshot_dir):
    result = runner.invoke(search_cmd, ["key", "AWS_*", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "AWS_REGION" in result.output


def test_cli_search_value(runner, tmp_snapshot_dir):
    result = runner.invoke(search_cmd, ["value", "s3cr3t", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_search_no_results(runner, tmp_snapshot_dir):
    result = runner.invoke(search_cmd, ["key", "NOPE_*", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "No matches found" in result.output
