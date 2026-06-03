"""Equivalence partitioning tests for basic marshal-supported types."""

from __future__ import annotations

import marshal

import pytest

from marshal_stability.cases import BASIC_CASES, UNSUPPORTED_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


@pytest.mark.parametrize("value", BASIC_CASES)
def test_basic_values_are_stable_in_same_process(value):
    """The same object should produce identical bytes in the same process."""
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize("value", BASIC_CASES)
def test_basic_values_round_trip(value):
    """marshal.loads(marshal.dumps(value)) should preserve supported values."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


@pytest.mark.parametrize("value", UNSUPPORTED_CASES)
def test_unsupported_values_raise_value_error(value):
    """Unsupported objects should fail predictably instead of silently corrupting."""
    with pytest.raises(ValueError):
        marshal.dumps(value)
