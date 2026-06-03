"""Tests for floating-point special values."""

from __future__ import annotations

import marshal
import math

import pytest

from marshal_stability.cases import FLOAT_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import dumps_bytes, repeated_dumps_are_identical


@pytest.mark.parametrize("value", FLOAT_CASES)
def test_float_specials_are_stable_in_same_process(value):
    """Floating-point values should be stable within the same process."""
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize("value", FLOAT_CASES)
def test_float_specials_round_trip(value):
    """NaN needs custom equivalence because NaN != NaN."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


def test_positive_and_negative_zero_have_distinct_marshal_bytes():
    """0.0 and -0.0 are equal by Python equality but may differ in bytes."""
    assert 0.0 == -0.0
    assert dumps_bytes(0.0) != dumps_bytes(-0.0)


def test_nan_round_trip_is_nan():
    """A marshalled NaN should load back as a NaN."""
    restored = marshal.loads(marshal.dumps(float("nan")))
    assert math.isnan(restored)
