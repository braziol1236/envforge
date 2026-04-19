import pytest
from click.testing import CliRunner
from pathlib import Path
from envforge.cli_template import template_cmd
from envforge.snapshot import load_snapshot


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_template_dir(tmp_path):
    return tmp_path / "templates"


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def _tdir(tmp_template_dir):
    return ["--dir", str(tmp_template_dir)]


def test_create_and_list(runner, tmp_template_dir):
    result = runner.invoke(template_cmd, ["create", "myapp", "-v", "PORT=8080", "-v", "ENV=prod"] + _tdir(tmp_template_dir))
    assert result.exit_code == 0
    assert "myapp" in result.output

    result = runner.invoke(template_cmd, ["list"] + _tdir(tmp_template_dir))
    assert "myapp" in result.output


def test_show_template(runner, tmp_template_dir):
    runner.invoke(template_cmd, ["create", "svc", "-v", "HOST=localhost"] + _tdir(tmp_template_dir))
    result = runner.invoke(template_cmd, ["show", "svc"] + _tdir(tmp_template_dir))
    assert "HOST=localhost" in result.output


def test_delete_template(runner, tmp_template_dir):
    runner.invoke(template_cmd, ["create", "tmp", "-v", "A=1"] + _tdir(tmp_template_dir))
    result = runner.invoke(template_cmd, ["delete", "tmp"] + _tdir(tmp_template_dir))
    assert result.exit_code == 0
    result = runner.invoke(template_cmd, ["list"] + _tdir(tmp_template_dir))
    assert "tmp" not in result.output


def test_apply_creates_snapshot(runner, tmp_template_dir, tmp_snapshot_dir):
    runner.invoke(template_cmd, ["create", "base", "-v", "PORT=3000", "-v", "HOST=localhost"] + _tdir(tmp_template_dir))
    result = runner.invoke(template_cmd, [
        "apply", "base", "mysnap",
        "--dir", str(tmp_template_dir),
        "--snapshot-dir", str(tmp_snapshot_dir)
    ])
    assert result.exit_code == 0
    snap = load_snapshot("mysnap", tmp_snapshot_dir)
    assert snap["variables"]["PORT"] == "3000"


def test_apply_with_override(runner, tmp_template_dir, tmp_snapshot_dir):
    runner.invoke(template_cmd, ["create", "base", "-v", "PORT=3000"] + _tdir(tmp_template_dir))
    runner.invoke(template_cmd, [
        "apply", "base", "snap2", "-v", "PORT=9999",
        "--dir", str(tmp_template_dir),
        "--snapshot-dir", str(tmp_snapshot_dir)
    ])
    snap = load_snapshot("snap2", tmp_snapshot_dir)
    assert snap["variables"]["PORT"] == "9999"
