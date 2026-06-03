"""Tests for recursive and cyclic containers."""

from __future__ import annotations

import marshal

from marshal_stability.cases import recursive_dict, recursive_list
from marshal_stability.hash_utils import repeated_dumps_are_identical


def test_recursive_list_does_not_crash():
    """Recursive lists should either serialize or raise a Python exception."""
    value = recursive_list()
    try:
        data = marshal.dumps(value)
    except (ValueError, TypeError, RecursionError):
        return

    restored = marshal.loads(data)
    assert isinstance(restored, list)
    assert restored[0] is restored


def test_recursive_dict_does_not_crash():
    """Recursive dictionaries should either serialize or raise a Python exception."""
    value = recursive_dict()
    try:
        data = marshal.dumps(value)
    except (ValueError, TypeError, RecursionError):
        return

    restored = marshal.loads(data)
    assert isinstance(restored, dict)
    assert restored["self"] is restored


def test_recursive_list_repeated_serialization_if_supported():
    """If the interpreter supports recursive lists, output should be stable."""
    value = recursive_list()
    try:
        assert repeated_dumps_are_identical(value, repeats=5)
    except (ValueError, TypeError, RecursionError):
        return
