"""Custom equivalence checks for marshal round-trip tests."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence, Set
from typing import Any


def float_equivalent(left: float, right: float) -> bool:
    """Compare floats while treating NaN values as equivalent."""
    if math.isnan(left) and math.isnan(right):
        return True
    return left == right


def complex_equivalent(left: complex, right: complex) -> bool:
    """Compare complex numbers while treating NaN components as equivalent."""
    return float_equivalent(left.real, right.real) and float_equivalent(
        left.imag,
        right.imag,
    )


def equivalent(left: Any, right: Any, seen: set[tuple[int, int]] | None = None) -> bool:
    """Return whether two objects are equivalent after marshal round trip.

    This is intentionally stricter than normal equality for most objects, but
    handles special cases such as NaN and recursive containers.
    """
    if seen is None:
        seen = set()

    pair = (id(left), id(right))
    if pair in seen:
        return True
    seen.add(pair)

    if isinstance(left, float) and isinstance(right, float):
        return float_equivalent(left, right)

    if isinstance(left, complex) and isinstance(right, complex):
        return complex_equivalent(left, right)

    if type(left) is not type(right):
        return False

    if isinstance(left, Mapping):
        if len(left) != len(right):
            return False
        for key in left:
            if key not in right:
                return False
            if not equivalent(left[key], right[key], seen):
                return False
        return True

    if isinstance(left, (list, tuple)):
        if len(left) != len(right):
            return False
        return all(equivalent(a, b, seen) for a, b in zip(left, right))

    if isinstance(left, (set, frozenset)):
        # Sets containing NaN cannot be reliably compared by normal equality.
        # For this test suite we use repr-based matching for simple generated sets.
        return sorted(map(repr, left)) == sorted(map(repr, right))

    return left == right
