import pytest
from envforge.schema import (
    KeyRule, Schema, validate_snapshot, has_errors, format_results
)


BASE_SCHEMA = Schema(
    name="test",
    rules=[
        KeyRule(key="APP_ENV", required=True, pattern="production|staging|development"),
        KeyRule(key="PORT", required=True, pattern=r"\d+"),
        KeyRule(key="LOG_LEVEL", required=False, pattern="DEBUG|INFO|WARNING|ERROR"),
    ],
)


def test_valid_snapshot_passes():
    env = {"APP_ENV": "production", "PORT": "8080", "LOG_LEVEL": "INFO"}
    results = validate_snapshot(env, BASE_SCHEMA)
    assert results == []
    assert not has_errors(results)


def test_missing_required_key():
    env = {"PORT": "8080"}
    results = validate_snapshot(env, BASE_SCHEMA)
    keys = [r.key for r in results]
    assert "APP_ENV" in keys
    assert has_errors(results)


def test_pattern_mismatch():
    env = {"APP_ENV": "local", "PORT": "8080"}
    results = validate_snapshot(env, BASE_SCHEMA)
    assert any(r.key == "APP_ENV" and r.rule == "pattern" for r in results)


def test_optional_key_absent_no_error():
    env = {"APP_ENV": "staging", "PORT": "3000"}
    results = validate_snapshot(env, BASE_SCHEMA)
    assert all(r.key != "LOG_LEVEL" for r in results)


def test_optional_key_present_bad_pattern():
    env = {"APP_ENV": "development", "PORT": "3000", "LOG_LEVEL": "VERBOSE"}
    results = validate_snapshot(env, BASE_SCHEMA)
    assert any(r.key == "LOG_LEVEL" for r in results)


def test_format_results_empty():
    assert format_results([]) == "Schema validation passed."


def test_format_results_shows_errors():
    env = {"PORT": "abc"}
    results = validate_snapshot(env, BASE_SCHEMA)
    output = format_results(results)
    assert "ERROR" in output
    assert "APP_ENV" in output or "PORT" in output


def test_no_rules_always_passes():
    schema = Schema(name="empty")
    results = validate_snapshot({"ANYTHING": "value"}, schema)
    assert results == []
