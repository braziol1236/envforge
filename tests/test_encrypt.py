import json
import pytest

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envforge.encrypt import (
    encrypt_snapshot,
    decrypt_snapshot,
    save_encrypted_snapshot,
    load_encrypted_snapshot,
)


SAMPLE = {"API_KEY": "secret123", "DB_URL": "postgres://localhost/dev"}


def test_encrypt_decrypt_roundtrip():
    token = encrypt_snapshot(SAMPLE, "mypassphrase")
    result = decrypt_snapshot(token, "mypassphrase")
    assert result == SAMPLE


def test_wrong_passphrase_raises():
    token = encrypt_snapshot(SAMPLE, "correct")
    with pytest.raises(ValueError, match="Invalid passphrase"):
        decrypt_snapshot(token, "wrong")


def test_encrypted_token_is_string():
    token = encrypt_snapshot(SAMPLE, "pass")
    assert isinstance(token, str)
    assert len(token) > 0


def test_different_passphrases_produce_different_tokens():
    t1 = encrypt_snapshot(SAMPLE, "pass1")
    t2 = encrypt_snapshot(SAMPLE, "pass2")
    assert t1 != t2


def test_save_and_load_encrypted_snapshot(tmp_path):
    path = str(tmp_path / "snap.json")
    save_encrypted_snapshot(path, SAMPLE, "secure")
    result = load_encrypted_snapshot(path, "secure")
    assert result == SAMPLE


def test_saved_file_marks_encrypted(tmp_path):
    path = str(tmp_path / "snap.json")
    save_encrypted_snapshot(path, SAMPLE, "secure")
    with open(path) as fh:
        blob = json.load(fh)
    assert blob["encrypted"] is True
    assert "data" in blob


def test_load_non_encrypted_raises(tmp_path):
    path = str(tmp_path / "plain.json")
    with open(path, "w") as fh:
        json.dump({"encrypted": False, "data": ""}, fh)
    with pytest.raises(ValueError, match="not encrypted"):
        load_encrypted_snapshot(path, "pass")
