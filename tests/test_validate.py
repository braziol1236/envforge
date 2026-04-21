"""Tests for envforge.validate."""

from __future__ import annotations

import pytest
from pathlib import Path

from envforge.snapshot import save_snapshot
from envforge.schema import Schema, KeyRule
from envforge.validate import validate, validate_many, format_validate_report


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return tmp_path


@pytest.fixture()
def _dir(tmp_snapshot_dir):
    return {"snapshot_dir": tmp_snapshot_dir}


def _save(name, vars_, tmp_snapshot_dir):
    save_snapshot(name, vars_, snapshot_dir=tmp_snapshot_dir)


def test_validate_passes_when_all_rules_met(tmp_snapshot_dir, _dir):
    _save("prod", {"PORT": "8080", "HOST": "localhost"}, tmp_snapshot_dir)
    schema = Schema(rules={"PORT": KeyRule(required=True)})
    result = validate("prod", schema, **_dir)
    assert result["passed"] is True
    assert result["snapshot"] == "prod"


def test_validate_fails_missing_required_key(tmp_snapshot_dir, _dir):
    _save("staging", {"HOST": "example.com"}, tmp_snapshot_dir)
    schema = Schema(rules={"PORT": KeyRule(required=True)})
    result = validate("staging", schema, **_dir)
    assert result["passed"] is False
    assert any(r.key == "PORT" for r in result["results"])


def test_validate_fails_pattern_mismatch(tmp_snapshot_dir, _dir):
    _save("dev", {"PORT": "not-a-number"}, tmp_snapshot_dir)
    schema = Schema(rules={"PORT": KeyRule(required=True, pattern=r"^\d+$")})
    result = validate("dev", schema, **_dir)
    assert result["passed"] is False


def test_validate_many_all_pass(tmp_snapshot_dir, _dir):
    for name in ("a", "b", "c"):
        _save(name, {"KEY": "val"}, tmp_snapshot_dir)
    schema = Schema(rules={"KEY": KeyRule(required=True)})
    results = validate_many(["a", "b", "c"], schema, **_dir)
    assert all(r["passed"] for r in results)
    assert [r["snapshot"] for r in results] == ["a", "b", "c"]


def test_validate_many_partial_failure(tmp_snapshot_dir, _dir):
    _save("ok", {"PORT": "9000"}, tmp_snapshot_dir)
    _save("bad", {"OTHER": "x"}, tmp_snapshot_dir)
    schema = Schema(rules={"PORT": KeyRule(required=True)})
    results = validate_many(["ok", "bad"], schema, **_dir)
    passed = {r["snapshot"]: r["passed"] for r in results}
    assert passed["ok"] is True
    assert passed["bad"] is False


def test_format_validate_report_passed(tmp_snapshot_dir, _dir):
    _save("clean", {"X": "1"}, tmp_snapshot_dir)
    schema = Schema(rules={})
    result = validate("clean", schema, **_dir)
    report = format_validate_report(result)
    assert "PASSED" in report
    assert "clean" in report


def test_format_validate_report_failed(tmp_snapshot_dir, _dir):
    _save("broken", {}, tmp_snapshot_dir)
    schema = Schema(rules={"MUST_HAVE": KeyRule(required=True)})
    result = validate("broken", schema, **_dir)
    report = format_validate_report(result)
    assert "FAILED" in report
    assert "MUST_HAVE" in report
