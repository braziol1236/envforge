"""Tests for envforge.snapshot_share."""

from __future__ import annotations

import base64
import json
import pytest

from envforge.snapshot import save_snapshot, load_snapshot
from envforge.snapshot_share import (
    export_token,
    import_token,
    token_metadata,
    ShareError,
)


@pytest.fixture()
def tmp_snapshot_dir(tmp_path):
    return str(tmp_path)


def _save(name, vars_, tmp_dir):
    save_snapshot(name, vars_, snapshot_dir=tmp_dir)


def test_export_token_returns_string(tmp_snapshot_dir):
    _save("mysnap", {"FOO": "bar", "BAZ": "qux"}, tmp_snapshot_dir)
    token = export_token("mysnap", snapshot_dir=tmp_snapshot_dir, redact=False)
    assert isinstance(token, str)
    assert len(token) > 10


def test_export_token_is_valid_base64_json(tmp_snapshot_dir):
    _save("mysnap", {"X": "1"}, tmp_snapshot_dir)
    token = export_token("mysnap", snapshot_dir=tmp_snapshot_dir, redact=False)
    raw = base64.urlsafe_b64decode(token.encode()).decode()
    payload = json.loads(raw)
    assert payload["name"] == "mysnap"
    assert payload["vars"] == {"X": "1"}
    assert payload["version"] == 1
    assert "exported_at" in payload


def test_export_redacts_sensitive_keys(tmp_snapshot_dir):
    _save("sec", {"API_SECRET": "topsecret", "HOME": "/home/user"}, tmp_snapshot_dir)
    token = export_token("sec", snapshot_dir=tmp_snapshot_dir, redact=True)
    raw = base64.urlsafe_b64decode(token.encode()).decode()
    payload = json.loads(raw)
    assert payload["vars"]["API_SECRET"] != "topsecret"
    assert payload["vars"]["HOME"] == "/home/user"


def test_import_token_roundtrip(tmp_snapshot_dir):
    _save("orig", {"KEY": "value"}, tmp_snapshot_dir)
    token = export_token("orig", snapshot_dir=tmp_snapshot_dir, redact=False)
    saved = import_token(token, target_name="restored", snapshot_dir=tmp_snapshot_dir)
    assert saved == "restored"
    data = load_snapshot("restored", snapshot_dir=tmp_snapshot_dir)
    assert data["KEY"] == "value"


def test_import_token_uses_embedded_name_when_no_target(tmp_snapshot_dir):
    _save("autoname", {"A": "b"}, tmp_snapshot_dir)
    token = export_token("autoname", snapshot_dir=tmp_snapshot_dir, redact=False)
    saved = import_token(token, snapshot_dir=tmp_snapshot_dir)
    assert saved == "autoname"


def test_import_invalid_token_raises(tmp_snapshot_dir):
    with pytest.raises(ShareError):
        import_token("not-a-valid-token", snapshot_dir=tmp_snapshot_dir)


def test_import_wrong_version_raises(tmp_snapshot_dir):
    payload = {"name": "x", "vars": {}, "exported_at": "now", "version": 99}
    token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    with pytest.raises(ShareError, match="Unsupported"):
        import_token(token, snapshot_dir=tmp_snapshot_dir)


def test_token_metadata(tmp_snapshot_dir):
    _save("meta", {"A": "1", "B": "2"}, tmp_snapshot_dir)
    token = export_token("meta", snapshot_dir=tmp_snapshot_dir, redact=False)
    meta = token_metadata(token)
    assert meta["name"] == "meta"
    assert meta["key_count"] == 2
    assert meta["version"] == 1
    assert meta["exported_at"] is not None


def test_export_missing_snapshot_raises(tmp_snapshot_dir):
    with pytest.raises(FileNotFoundError):
        export_token("ghost", snapshot_dir=tmp_snapshot_dir)
