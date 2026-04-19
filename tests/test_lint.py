import pytest
from envforge.snapshot import save_snapshot
from envforge.lint import lint_snapshot, has_warnings, format_lint_results
from click.testing import CliRunner
from envforge.cli_lint import lint_cmd


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def test_lint_clean_snapshot(tmp_snapshot_dir):
    save_snapshot("clean", {"PATH": "/usr/bin", "HOME": "/home/user"}, tmp_snapshot_dir)
    results = lint_snapshot("clean", tmp_snapshot_dir)
    assert not has_warnings(results)


def test_lint_empty_value(tmp_snapshot_dir):
    save_snapshot("empty", {"FOO": "", "BAR": "ok"}, tmp_snapshot_dir)
    results = lint_snapshot("empty", tmp_snapshot_dir)
    assert "FOO" in results["empty_values"]
    assert "BAR" not in results["empty_values"]


def test_lint_key_with_space(tmp_snapshot_dir):
    save_snapshot("spaced", {"MY KEY": "value"}, tmp_snapshot_dir)
    results = lint_snapshot("spaced", tmp_snapshot_dir)
    assert "MY KEY" in results["keys_with_spaces"]


def test_lint_overlong_value(tmp_snapshot_dir):
    save_snapshot("long", {"BIG": "x" * 600}, tmp_snapshot_dir)
    results = lint_snapshot("long", tmp_snapshot_dir)
    assert "BIG" in results["overlong_values"]


def test_lint_suspicious_key(tmp_snapshot_dir):
    save_snapshot("sus", {"API_SECRET": "abc123", "NORMAL": "val"}, tmp_snapshot_dir)
    results = lint_snapshot("sus", tmp_snapshot_dir)
    assert "API_SECRET" in results["suspicious_keys"]
    assert "NORMAL" not in results["suspicious_keys"]


def test_format_lint_results_no_issues(tmp_snapshot_dir):
    save_snapshot("ok", {"X": "1"}, tmp_snapshot_dir)
    results = lint_snapshot("ok", tmp_snapshot_dir)
    assert format_lint_results(results) == "No issues found."


def test_cli_lint_run(tmp_snapshot_dir):
    save_snapshot("proj", {"SECRET_KEY": "hunter2", "PORT": ""}, tmp_snapshot_dir)
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["run", "proj", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 0
    assert "suspicious_keys" in result.output or "empty_values" in result.output


def test_cli_lint_strict_exits_nonzero(tmp_snapshot_dir):
    save_snapshot("bad", {"DB_PASSWORD": "1234"}, tmp_snapshot_dir)
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["run", "bad", "--dir", tmp_snapshot_dir, "--strict"])
    assert result.exit_code == 1


def test_cli_lint_missing_snapshot(tmp_snapshot_dir):
    runner = CliRunner()
    result = runner.invoke(lint_cmd, ["run", "ghost", "--dir", tmp_snapshot_dir])
    assert result.exit_code == 1
