"""Tests for floating-point special values."""

from __future__ import annotations

import marshal
import math
import sys

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


def test_float_precision_boundaries():
    """Test floating-point precision boundaries for non-determinism."""
    precision_cases = [
        1.0000000000000001,
        1.0000000000000002,
        1.0000000000000003,
        2.0 - 2**-52,  # 小于2的最大浮点数
        2.0,
        2.0 + 2**-52,  # 大于2的最小浮点数
        float.fromhex('0x1.fffffffffffffp+1023'),  # 最大可表示的float
        float.fromhex('0x1.0000000000000p-1022'),  # 最小正规数
        float.fromhex('0x1.0000000000001p-1022'),  # 次小正规数
        1e-308,
        1e308,
        -1e-308,
        -1e308,
    ]
    for value in precision_cases:
        assert repeated_dumps_are_identical(value, repeats=5), f"Unstable float: {value}"


def test_float_edge_cases():
    """Test edge cases for floating-point serialization."""
    edge_cases = [
        math.pi,
        math.e,
        math.sqrt(2),
        math.sqrt(3),
        float('inf'),
        float('-inf'),
        float('nan'),
        -float('nan'),
        0.0,
        -0.0,
        sys.float_info.max,
        sys.float_info.min,
        sys.float_info.epsilon,
        -sys.float_info.max,
        -sys.float_info.min,
    ]
    for value in edge_cases:
        assert repeated_dumps_are_identical(value, repeats=3), f"Unstable float: {value}"


def test_complex_number_stability():
    """Test complex number serialization stability."""
    complex_cases = [
        complex(1.0, 2.0),
        complex(float('nan'), 1.0),
        complex(1.0, float('nan')),
        complex(float('inf'), 0.0),
        complex(0.0, float('inf')),
        complex(float('nan'), float('nan')),
        complex(sys.float_info.max, sys.float_info.min),
    ]
    for value in complex_cases:
        assert repeated_dumps_are_identical(value, repeats=3), f"Unstable complex: {value}"
