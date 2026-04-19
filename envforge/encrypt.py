"""Optional encryption for snapshot values using a passphrase."""
import base64
import hashlib
import json
import os
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _derive_key(passphrase: str) -> bytes:
    digest = hashlib.sha256(passphrase.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_snapshot(env: Dict[str, str], passphrase: str) -> str:
    """Encrypt env dict to a base64 string."""
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography package is required for encryption")
    key = _derive_key(passphrase)
    f = Fernet(key)
    payload = json.dumps(env).encode()
    token = f.encrypt(payload)
    return token.decode()


def decrypt_snapshot(token: str, passphrase: str) -> Dict[str, str]:
    """Decrypt a base64 token back to env dict."""
    if not HAS_CRYPTO:
        raise RuntimeError("cryptography package is required for encryption")
    key = _derive_key(passphrase)
    f = Fernet(key)
    try:
        payload = f.decrypt(token.encode())
    except InvalidToken:
        raise ValueError("Invalid passphrase or corrupted data")
    return json.loads(payload.decode())


def save_encrypted_snapshot(snapshot_path: str, env: Dict[str, str], passphrase: str) -> None:
    token = encrypt_snapshot(env, passphrase)
    with open(snapshot_path, "w") as fh:
        json.dump({"encrypted": True, "data": token}, fh)


def load_encrypted_snapshot(snapshot_path: str, passphrase: str) -> Dict[str, str]:
    with open(snapshot_path) as fh:
        blob = json.load(fh)
    if not blob.get("encrypted"):
        raise ValueError("Snapshot is not encrypted")
    return decrypt_snapshot(blob["data"], passphrase)
