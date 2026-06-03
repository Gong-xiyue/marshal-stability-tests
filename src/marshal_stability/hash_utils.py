"""Hashing and serialization helpers for marshal tests."""

from __future__ import annotations

import hashlib
import marshal
from typing import Any


def dumps_bytes(value: Any, version: int = marshal.version) -> bytes:
    """Serialize a value with marshal and return raw bytes."""
    return marshal.dumps(value, version)


def sha256_of_bytes(data: bytes) -> str:
    """Return the SHA-256 hexadecimal digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def marshal_digest(value: Any, version: int = marshal.version) -> str:
    """Return the SHA-256 digest of marshal.dumps(value)."""
    return sha256_of_bytes(dumps_bytes(value, version))


def repeated_dumps_are_identical(
    value: Any,
    repeats: int = 20,
    version: int = marshal.version,
) -> bool:
    """Check whether repeated marshal.dumps calls produce identical bytes."""
    first = dumps_bytes(value, version)
    return all(dumps_bytes(value, version) == first for _ in range(repeats))
