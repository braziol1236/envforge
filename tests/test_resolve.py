"""Tests for envforge.resolve."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envforge.resolve import resolve_value, resolve_snapshot, resolve_and_save
from envforge.snapshot import save_snapshot, load_snapshot
from envforge.cli_resolve import resolve_cmd


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


# --- unit tests ---

def test_resolve_value_curly():
    assert resolve_value("${HOME}/bin", {"HOME": "/root"}) == "/root/bin"


def test_resolve_value_bare():
    assert resolve_value("$USER name", {"USER": "alice"}) == "alice name"


def test_resolve_value_unknown_ref_unchanged():
    result = resolve_value("${MISSING}", {})
    assert result == "${MISSING}"


def test_resolve_value_no_refs():
    assert resolve_value("hello world", {"X": "y"}) == "hello world"


def test_resolve_value_circular_raises():
    with pytest.raises(ValueError, match="circular"):
        resolve_value("${A}", {"A": "${B}", "B": "${A}"}, max_depth=5)


def test_resolve_snapshot_expands_all():
    vars = {"BASE": "/opt", "BIN": "${BASE}/bin", "LIB": "${BASE}/lib"}
    result = resolve_snapshot(vars)
    assert result["BIN"] == "/opt/bin"
    assert result["LIB"] == "/opt/lib"


def test_resolve_snapshot_uses_extra_env():
    vars = {"FULL": "${PREFIX}_suffix"}
    result = resolve_snapshot(vars, extra_env={"PREFIX": "hello"})
    assert result["FULL"] == "hello_suffix"


def test_resolve_snapshot_snapshot_key_overrides_extra():
    vars = {"X": "snap", "Y": "${X}"}
    result = resolve_snapshot(vars, extra_env={"X": "extra"})
    assert result["Y"] == "snap"


# --- integration: resolve_and_save ---

def test_resolve_and_save(tmp_snapshot_dir):
    save_snapshot("src", {"ROOT": "/app", "DATA": "${ROOT}/data"}, snapshot_dir=tmp_snapshot_dir)
    resolved = resolve_and_save("src", "dst", snapshot_dir=tmp_snapshot_dir)
    assert resolved["DATA"] == "/app/data"
    saved = load_snapshot("dst", snapshot_dir=tmp_snapshot_dir)
    assert saved["vars"]["DATA"] == "/app/data"


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_show_resolved(runner, tmp_snapshot_dir):
    save_snapshot("mysnap", {"A": "hello", "B": "${A}_world"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(resolve_cmd, ["show", "mysnap", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "B=hello_world" in result.output


def test_cli_show_missing_snapshot(runner, tmp_snapshot_dir):
    result = runner.invoke(resolve_cmd, ["show", "ghost", "--dir", tmp_snapshot_dir])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_cli_save_resolved(runner, tmp_snapshot_dir):
    save_snapshot("base", {"DIR": "/var", "LOG": "${DIR}/log"}, snapshot_dir=tmp_snapshot_dir)
    result = runner.invoke(resolve_cmd, ["save", "base", "resolved_base", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "resolved_base" in result.output
    data = load_snapshot("resolved_base", snapshot_dir=tmp_snapshot_dir)
    assert data["vars"]["LOG"] == "/var/log"
