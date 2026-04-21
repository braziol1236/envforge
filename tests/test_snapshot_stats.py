"""Tests for envforge.snapshot_stats."""

import pytest

from envforge.snapshot import save_snapshot
from envforge.snapshot_stats import (
    SnapshotStats,
    compute_all_stats,
    compute_stats,
    format_stats,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name, vars_, snapshot_dir, tags=None):
    data = {"vars": vars_}
    if tags:
        data["tags"] = tags
    save_snapshot(name, data, snapshot_dir=snapshot_dir)


def test_stats_basic(tmp_snapshot_dir):
    _save("mysnap", {"HOME": "/home/user", "PATH": "/usr/bin"}, tmp_snapshot_dir)
    stats = compute_stats("mysnap", snapshot_dir=tmp_snapshot_dir)

    assert isinstance(stats, SnapshotStats)
    assert stats.name == "mysnap"
    assert stats.total_keys == 2
    assert stats.empty_values == 0
    assert stats.avg_value_length == pytest.approx((len("/home/user") + len("/usr/bin")) / 2, 0.01)


def test_stats_empty_values(tmp_snapshot_dir):
    _save("snap2", {"A": "", "B": "", "C": "hello"}, tmp_snapshot_dir)
    stats = compute_stats("snap2", snapshot_dir=tmp_snapshot_dir)

    assert stats.total_keys == 3
    assert stats.empty_values == 2


def test_stats_empty_snapshot(tmp_snapshot_dir):
    _save("empty", {}, tmp_snapshot_dir)
    stats = compute_stats("empty", snapshot_dir=tmp_snapshot_dir)

    assert stats.total_keys == 0
    assert stats.empty_values == 0
    assert stats.avg_value_length == 0.0
    assert stats.longest_key == ""
    assert stats.longest_value_key == ""


def test_stats_longest_key(tmp_snapshot_dir):
    _save("snap3", {"SHORT": "x", "MUCH_LONGER_KEY_NAME": "y"}, tmp_snapshot_dir)
    stats = compute_stats("snap3", snapshot_dir=tmp_snapshot_dir)

    assert stats.longest_key == "MUCH_LONGER_KEY_NAME"


def test_stats_tags_included(tmp_snapshot_dir):
    _save("tagged", {"X": "1"}, tmp_snapshot_dir, tags=["prod", "infra"])
    stats = compute_stats("tagged", snapshot_dir=tmp_snapshot_dir)

    assert "prod" in stats.tags
    assert "infra" in stats.tags


def test_compute_all_stats(tmp_snapshot_dir):
    _save("s1", {"A": "1"}, tmp_snapshot_dir)
    _save("s2", {"B": "2", "C": "3"}, tmp_snapshot_dir)
    all_stats = compute_all_stats(snapshot_dir=tmp_snapshot_dir)

    assert len(all_stats) == 2
    names = {s.name for s in all_stats}
    assert names == {"s1", "s2"}


def test_format_stats_output(tmp_snapshot_dir):
    _save("fmt", {"KEY": "value"}, tmp_snapshot_dir)
    stats = compute_stats("fmt", snapshot_dir=tmp_snapshot_dir)
    output = format_stats(stats)

    assert "fmt" in output
    assert "Total keys" in output
    assert "Empty values" in output
    assert "Avg value length" in output
    assert "(none)" in output  # no tags
