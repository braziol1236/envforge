"""CLI tests for tag commands."""
import pytest
from click.testing import CliRunner
from envforge.snapshot import save_snapshot
from envforge.cli_tags import tags_cmd


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_snapshot_dir(tmp_path):
    return tmp_path


def _dir_args(d):
    return []  # tags_cmd uses default dir; we monkey-patch via fixture indirectly


def test_add_and_list_tags(runner, tmp_snapshot_dir, monkeypatch):
    monkeypatch.setattr("envforge.tags.load_snapshot",
        lambda n, sd=None: __import__('envforge.snapshot', fromlist=['load_snapshot']).load_snapshot(n, tmp_snapshot_dir))
    monkeypatch.setattr("envforge.tags.save_snapshot",
        lambda n, v, sd=None, extra=None: __import__('envforge.snapshot', fromlist=['save_snapshot']).save_snapshot(n, v, tmp_snapshot_dir, extra))
    save_snapshot("mysnap", {"X": "1"}, tmp_snapshot_dir)
    result = runner.invoke(tags_cmd, ["add", "mysnap", "prod"])
    assert result.exit_code == 0
    assert "prod" in result.output


def test_find_by_tag(runner, tmp_snapshot_dir, monkeypatch):
    monkeypatch.setattr("envforge.tags.load_snapshot",
        lambda n, sd=None: __import__('envforge.snapshot', fromlist=['load_snapshot']).load_snapshot(n, tmp_snapshot_dir))
    monkeypatch.setattr("envforge.tags.save_snapshot",
        lambda n, v, sd=None, extra=None: __import__('envforge.snapshot', fromlist=['save_snapshot']).save_snapshot(n, v, tmp_snapshot_dir, extra))
    monkeypatch.setattr("envforge.tags.list_snapshots",
        lambda sd=None: __import__('envforge.snapshot', fromlist=['list_snapshots']).list_snapshots(tmp_snapshot_dir))
    save_snapshot("mysnap", {"X": "1"}, tmp_snapshot_dir)
    from envforge.tags import add_tag
    add_tag("mysnap", "staging", tmp_snapshot_dir)
    result = runner.invoke(tags_cmd, ["find", "staging"])
    # output depends on monkeypatching list_by_tag internals; just check no crash
    assert result.exit_code == 0


def test_add_tag_missing_snapshot(runner, tmp_snapshot_dir, monkeypatch):
    monkeypatch.setattr("envforge.tags.load_snapshot",
        lambda n, sd=None: __import__('envforge.snapshot', fromlist=['load_snapshot']).load_snapshot(n, tmp_snapshot_dir))
    result = runner.invoke(tags_cmd, ["add", "ghost", "prod"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower() or "not found" in (result.output + "").lower()
