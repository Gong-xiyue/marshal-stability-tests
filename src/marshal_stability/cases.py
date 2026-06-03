"""Manually designed marshal test cases."""

from __future__ import annotations

import sys
from typing import Any


BASIC_CASES: list[Any] = [
    None,
    True,
    False,
    StopIteration,
    Ellipsis,
    0,
    1,
    -1,
    123456789,
    "",
    "abc",
    "中文",
    b"",
    b"abc",
    (),
    [],
    {},
    set(),
    frozenset(),
    (1, "a", None),
    [1, "a", None],
    {"a": 1, "b": 2},
    {1, 2, 3},
    frozenset({1, 2, 3}),
]

BOUNDARY_CASES: list[Any] = [
    0,
    1,
    -1,
    2**31 - 1,
    2**31,
    -(2**31),
    2**63 - 1,
    2**63,
    -(2**63),
    10**100,
    "",
    "a",
    "a" * 255,
    "a" * 256,
    "a" * 1024,
    b"",
    b"a",
    b"a" * 255,
    b"a" * 256,
    [],
    [0],
    list(range(1000)),
    {},
    {str(i): i for i in range(1000)},
]

FLOAT_CASES: list[Any] = [
    0.0,
    -0.0,
    1.0,
    -1.5,
    float("inf"),
    float("-inf"),
    float("nan"),
    sys.float_info.max,
    sys.float_info.min,
    complex(1.0, 2.0),
    complex(float("nan"), 1.0),
    complex(1.0, float("nan")),
]

UNSUPPORTED_CASES: list[Any] = [
    object(),
    lambda x: x,
]


def recursive_list() -> list[Any]:
    """Create a list that contains itself."""
    value: list[Any] = []
    value.append(value)
    return value


def recursive_dict() -> dict[str, Any]:
    """Create a dictionary that contains itself."""
    value: dict[str, Any] = {}
    value["self"] = value
    return value


def recursive_set() -> set[Any]:
    """Create a set-like recursive object if possible.

    Plain set cannot directly contain itself because it is unhashable, so this
    function returns a set containing a frozenset as a related robustness case.
    """
    return {frozenset({1, 2, 3})}


def code_object() -> Any:
    """Return a simple compiled code object."""
    return compile("x = 1\nprint(x)\n", "<marshal-test>", "exec")
