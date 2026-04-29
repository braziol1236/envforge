"""Snapshot sharing: export a snapshot as a shareable token (base64-encoded JSON) and import it back."""

from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any

from envforge.snapshot import save_snapshot, load_snapshot
from envforge.redact import redact_snapshot


class ShareError(Exception):
    pass


def export_token(snapshot_name: str, *, snapshot_dir: str | None = None, redact: bool = True) -> str:
    """Encode a snapshot as a portable base64 token string."""
    data = load_snapshot(snapshot_name, snapshot_dir=snapshot_dir)
    if redact:
        data = redact_snapshot(data)
    payload: dict[str, Any] = {
        "name": snapshot_name,
        "vars": data,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }
    raw = json.dumps(payload, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode()


def import_token(token: str, *, target_name: str | None = None, snapshot_dir: str | None = None) -> str:
    """Decode a share token and save it as a snapshot. Returns the saved snapshot name."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        payload = json.loads(raw)
    except Exception as exc:
        raise ShareError(f"Invalid share token: {exc}") from exc

    if payload.get("version") != 1:
        raise ShareError("Unsupported token version")

    name = target_name or payload.get("name")
    if not name:
        raise ShareError("Cannot determine snapshot name from token")

    vars_data: dict[str, str] = payload.get("vars", {})
    if not isinstance(vars_data, dict):
        raise ShareError("Token vars field is not a mapping")

    save_snapshot(name, vars_data, snapshot_dir=snapshot_dir)
    return name


def token_metadata(token: str) -> dict[str, Any]:
    """Return metadata from a token without saving anything."""
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        payload = json.loads(raw)
    except Exception as exc:
        raise ShareError(f"Invalid share token: {exc}") from exc
    return {
        "name": payload.get("name"),
        "exported_at": payload.get("exported_at"),
        "version": payload.get("version"),
        "key_count": len(payload.get("vars", {})),
    }
