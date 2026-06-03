"""Tests for collection ordering and deterministic behavior."""

from __future__ import annotations

import marshal

from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


def test_dict_with_fixed_insertion_order_is_stable():
    """Dictionaries preserve insertion order in modern Python."""
    value = {"a": 1, "b": 2, "c": 3}
    assert repeated_dumps_are_identical(value)
    assert equivalent(value, marshal.loads(marshal.dumps(value)))


def test_set_is_stable_within_same_process():
    """A set should be stable when repeatedly serialized in one process."""
    value = {"apple", "banana", "cherry"}
    assert repeated_dumps_are_identical(value)


def test_frozenset_is_stable_within_same_process():
    """A frozenset should be stable when repeatedly serialized in one process."""
    value = frozenset({"apple", "banana", "cherry"})
    assert repeated_dumps_are_identical(value)


def test_dict_created_from_set_may_depend_on_set_iteration_order():
    """Document a risk: construction from set can inherit hash-dependent order."""
    source = {"apple", "banana", "cherry"}
    value = dict.fromkeys(source, 1)
    assert repeated_dumps_are_identical(value)
