"""Boundary value analysis tests for marshal serialization.

Testing theory: Boundary Value Analysis (BVA)
----------------------------------------------
Defects cluster at the edges of input ranges, so this module probes the
boundaries of the dimensions marshal cares about:

* integer encoding boundaries -- the 32-bit and 64-bit signed limits where
  marshal switches its internal representation, plus an arbitrary-precision
  big integer (10**100);
* container size boundaries -- empty (0), single element (1), and the
  255 / 256 transition where a length field would roll over a byte, scaled up
  to controlled large sizes;
* string / bytes length boundaries -- 0, 1, 255, 256, 1024 characters.

For each boundary value we assert byte-level repeatability and, where
meaningful, round-trip correctness.
"""

from __future__ import annotations

import marshal

import pytest

from marshal_stability.cases import BOUNDARY_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


# --- Boundary dimensions, declared explicitly for traceability ---------------

# Integer encoding boundaries: just inside / on / just outside the signed
# 32-bit and 64-bit limits, plus an arbitrary-precision value.
INTEGER_BOUNDARIES: list[int] = [
    0,
    1,
    -1,
    2**31 - 2,
    2**31 - 1,  # int32 max
    2**31,  # int32 max + 1
    -(2**31),  # int32 min
    -(2**31) - 1,  # int32 min - 1
    2**63 - 1,  # int64 max
    2**63,  # int64 max + 1
    -(2**63),  # int64 min
    10**100,  # arbitrary-precision big integer
]

# Container size boundaries shared by list / dict / set.
CONTAINER_SIZES: list[int] = [0, 1, 255, 256, 1024]

# String / bytes length boundaries.
SEQUENCE_LENGTHS: list[int] = [0, 1, 255, 256, 1024]


# --- Manually curated boundary cases from the shared catalogue ---------------


@pytest.mark.parametrize("value", BOUNDARY_CASES)
def test_boundary_values_are_stable(value):
    """Boundary cases should be stable under repeated serialization."""
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize("value", BOUNDARY_CASES)
def test_boundary_values_round_trip(value):
    """Boundary cases should round-trip correctly."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


# --- Integer encoding boundaries ---------------------------------------------


@pytest.mark.parametrize("value", INTEGER_BOUNDARIES, ids=[str(v) for v in INTEGER_BOUNDARIES])
def test_integer_encoding_boundaries_are_stable(value):
    """Integers at 32/64-bit limits and beyond must serialize identically."""
    assert repeated_dumps_are_identical(value, repeats=5)


@pytest.mark.parametrize("value", INTEGER_BOUNDARIES, ids=[str(v) for v in INTEGER_BOUNDARIES])
def test_integer_encoding_boundaries_round_trip(value):
    """Integers at encoding boundaries must round-trip without loss."""
    assert marshal.loads(marshal.dumps(value)) == value


# --- Container size boundaries -----------------------------------------------


@pytest.mark.parametrize("size", CONTAINER_SIZES)
def test_list_size_boundaries(size):
    """Lists at size boundaries are stable and round-trip correctly."""
    value = list(range(size))
    assert repeated_dumps_are_identical(value, repeats=3), f"Unstable list size {size}"
    assert marshal.loads(marshal.dumps(value)) == value


@pytest.mark.parametrize("size", CONTAINER_SIZES)
def test_dict_size_boundaries(size):
    """Dicts at size boundaries are stable and round-trip correctly."""
    value = {str(i): i for i in range(size)}
    assert repeated_dumps_are_identical(value, repeats=3), f"Unstable dict size {size}"
    assert marshal.loads(marshal.dumps(value)) == value


@pytest.mark.parametrize("size", CONTAINER_SIZES)
def test_set_size_boundaries(size):
    """Sets at size boundaries are stable under repeated serialization."""
    value = set(range(size))
    assert repeated_dumps_are_identical(value, repeats=3), f"Unstable set size {size}"


# --- String / bytes length boundaries ----------------------------------------


@pytest.mark.parametrize("length", SEQUENCE_LENGTHS)
def test_string_length_boundaries(length):
    """Strings at length boundaries are stable and round-trip correctly."""
    value = "a" * length
    assert repeated_dumps_are_identical(value, repeats=3), f"Unstable string len {length}"
    assert marshal.loads(marshal.dumps(value)) == value


@pytest.mark.parametrize("length", SEQUENCE_LENGTHS)
def test_bytes_length_boundaries(length):
    """Bytes at length boundaries are stable and round-trip correctly."""
    value = b"x" * length
    assert repeated_dumps_are_identical(value, repeats=3), f"Unstable bytes len {length}"
    assert marshal.loads(marshal.dumps(value)) == value


# --- Controlled "super large" containers -------------------------------------


def test_extremely_large_list_is_stable_at_controlled_size():
    """A controlled large list should not cause unexpected instability."""
    value = list(range(10_000))
    assert repeated_dumps_are_identical(value, repeats=5)
    assert marshal.loads(marshal.dumps(value)) == value


def test_mixed_large_containers():
    """A nested mix of large containers stays stable under repeated dumps."""
    mixed = {
        "list": list(range(1000)),
        "dict": {str(i): i for i in range(500)},
        "set": set(range(500)),
        "string": "test" * 1000,
        "bytes": b"data" * 1000,
    }
    assert repeated_dumps_are_identical(mixed, repeats=3)
