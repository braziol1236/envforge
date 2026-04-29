"""CLI integration tests for the share command group."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.cli_share import share_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir_args(d):
    return ["--dir", d]


def _save(name, vars_, d):
    save_snapshot(name, vars_, snapshot_dir=d)


def test_export_prints_token(runner, tmp_snapshot_dir):
    _save("proj", {"ENV": "prod"}, tmp_snapshot_dir)
    result = runner.invoke(share_cmd, ["export", "proj", "--no-redact"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code == 0
    token = result.output.strip()
    assert len(token) > 20


def test_import_saves_snapshot(runner, tmp_snapshot_dir):
    _save("source", {"DB": "localhost"}, tmp_snapshot_dir)
    export_result = runner.invoke(
        share_cmd, ["export", "source", "--no-redact"] + _dir_args(tmp_snapshot_dir)
    )
    token = export_result.output.strip()

    result = runner.invoke(
        share_cmd, ["import", token, "--as", "imported"] + _dir_args(tmp_snapshot_dir)
    )
    assert result.exit_code == 0
    assert "imported" in result.output


def test_inspect_shows_metadata(runner, tmp_snapshot_dir):
    _save("info", {"A": "1", "B": "2"}, tmp_snapshot_dir)
    export_result = runner.invoke(
        share_cmd, ["export", "info", "--no-redact"] + _dir_args(tmp_snapshot_dir)
    )
    token = export_result.output.strip()

    result = runner.invoke(share_cmd, ["inspect", token])
    assert result.exit_code == 0
    assert "info" in result.output
    assert "Keys" in result.output


def test_export_missing_snapshot_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(share_cmd, ["export", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0


def test_import_invalid_token_fails(runner, tmp_snapshot_dir):
    result = runner.invoke(share_cmd, ["import", "bad-token"] + _dir_args(tmp_snapshot_dir))
    assert result.exit_code != 0
