"""Property-based fuzzing tests for marshal-supported values."""

from __future__ import annotations

import marshal

from hypothesis import given, settings

from marshal_stability.comparators import equivalent
from marshal_stability.generators import marshal_supported_values
from marshal_stability.hash_utils import repeated_dumps_are_identical


@given(marshal_supported_values())
@settings(max_examples=500, deadline=None)
def test_fuzzed_values_are_stable(value):
    """Random supported values should serialize deterministically in-process."""
    assert repeated_dumps_are_identical(value, repeats=3)


@given(marshal_supported_values())
@settings(max_examples=500, deadline=None)
def test_fuzzed_values_round_trip(value):
    """Random supported values should survive marshal round-trip."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)
