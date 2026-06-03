"""Boundary value tests for marshal serialization."""

from __future__ import annotations

import marshal

import pytest

from marshal_stability.cases import BOUNDARY_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


@pytest.mark.parametrize("value", BOUNDARY_CASES)
def test_boundary_values_are_stable(value):
    """Boundary cases should be stable under repeated serialization."""
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize("value", BOUNDARY_CASES)
def test_boundary_values_round_trip(value):
    """Boundary cases should round-trip correctly."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


def test_extremely_large_list_is_stable_at_controlled_size():
    """A controlled large list should not cause unexpected instability."""
    value = list(range(10_000))
    assert repeated_dumps_are_identical(value, repeats=5)
    assert marshal.loads(marshal.dumps(value)) == value
