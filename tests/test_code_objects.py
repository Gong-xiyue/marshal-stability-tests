"""Tests for code objects and version-dependent marshal behavior."""

from __future__ import annotations

import inspect
import marshal

import pytest

from marshal_stability.cases import code_object
from marshal_stability.hash_utils import repeated_dumps_are_identical


def test_code_object_is_stable_in_same_process():
    """A fixed code object should serialize stably in the same interpreter."""
    value = code_object()
    assert repeated_dumps_are_identical(value, repeats=5)


def test_code_object_round_trip_type():
    """Code object round-trip should produce a code object in same interpreter."""
    value = code_object()
    restored = marshal.loads(marshal.dumps(value))
    assert type(restored) is type(value)


def test_allow_code_false_if_available():
    """Python 3.13+ supports allow_code=False for rejecting code objects."""
    signature = inspect.signature(marshal.dumps)
    if "allow_code" not in signature.parameters:
        pytest.skip("allow_code is not available in this Python version")

    with pytest.raises(ValueError):
        marshal.dumps(code_object(), allow_code=False)
