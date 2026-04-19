import pytest
from click.testing import CliRunner
from envforge.snapshot import save_snapshot
from envforge.cli_pin import pin_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _dir_args(d):
    return ["--dir", d]


@pytest.fixture
def preloaded(tmp_snapshot_dir):
    save_snapshot("mysnap", {"FOO": "bar"}, tmp_snapshot_dir)
    return tmp_snapshot_dir


def test_set_and_show_pin(runner, preloaded):
    r = runner.invoke(pin_cmd, ["set", "stable", "mysnap"] + _dir_args(preloaded))
    assert r.exit_code == 0
    assert "stable" in r.output

    r2 = runner.invoke(pin_cmd, ["show", "stable"] + _dir_args(preloaded))
    assert r2.exit_code == 0
    assert "mysnap" in r2.output


def test_set_missing_snapshot_fails(runner, tmp_snapshot_dir):
    r = runner.invoke(pin_cmd, ["set", "x", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert r.exit_code != 0


def test_list_pins(runner, preloaded):
    runner.invoke(pin_cmd, ["set", "stable", "mysnap"] + _dir_args(preloaded))
    r = runner.invoke(pin_cmd, ["list"] + _dir_args(preloaded))
    assert "stable" in r.output
    assert "mysnap" in r.output


def test_list_pins_empty(runner, tmp_snapshot_dir):
    r = runner.invoke(pin_cmd, ["list"] + _dir_args(tmp_snapshot_dir))
    assert "No pins" in r.output


def test_remove_pin(runner, preloaded):
    runner.invoke(pin_cmd, ["set", "stable", "mysnap"] + _dir_args(preloaded))
    r = runner.invoke(pin_cmd, ["remove", "stable"] + _dir_args(preloaded))
    assert r.exit_code == 0
    r2 = runner.invoke(pin_cmd, ["list"] + _dir_args(preloaded))
    assert "stable" not in r2.output


def test_remove_nonexistent_pin_fails(runner, tmp_snapshot_dir):
    r = runner.invoke(pin_cmd, ["remove", "ghost"] + _dir_args(tmp_snapshot_dir))
    assert r.exit_code != 0
