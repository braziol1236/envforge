"""Integration tests for the export CLI command."""

import json
import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from envforge.cli_export import export_cmd
from envforge.snapshot import save_snapshot


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVFORGE_SNAPSHOT_DIR", str(tmp_path))
    return tmp_path


def test_export_bash(runner, tmp_snapshot_dir):
    save_snapshot("myproject", {"FOO": "bar", "BAZ": "1"})
    result = runner.invoke(export_cmd, ["myproject", "--format", "bash"])
    assert result.exit_code == 0
    assert 'export FOO="bar"' in result.output
    assert 'export BAZ="1"' in result.output


def test_export_dotenv(runner, tmp_snapshot_dir):
    save_snapshot("myproject", {"KEY": "value"})
    result = runner.invoke(export_cmd, ["myproject", "--format", "dotenv"])
    assert result.exit_code == 0
    assert 'KEY="value"' in result.output


def test_export_fish(runner, tmp_snapshot_dir):
    save_snapshot("myproject", {"SHELL": "fish"})
    result = runner.invoke(export_cmd, ["myproject", "--format", "fish"])
    assert result.exit_code == 0
    assert 'set -x SHELL "fish"' in result.output


def test_export_missing_snapshot(runner, tmp_snapshot_dir):
    result = runner.invoke(export_cmd, ["ghost"])
    assert result.exit_code == 1


def test_export_to_file(runner, tmp_snapshot_dir, tmp_path):
    save_snapshot("proj", {"A": "1"})
    out_file = str(tmp_path / "env.sh")
    result = runner.invoke(export_cmd, ["proj", "--format", "bash", "-o", out_file])
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    with open(out_file) as f:
        content = f.read()
    assert 'export A="1"' in content
