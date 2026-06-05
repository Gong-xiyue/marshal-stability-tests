"""Equivalence partitioning tests for basic marshal-supported types.

Testing theory: Equivalence Partitioning
-----------------------------------------
The input domain of ``marshal.dumps`` is divided into equivalence classes,
one per fundamental Python type that marshal supports (``int``, ``float``,
``bool``, ``str``, ``bytes``, ``tuple``, ``list``, ``dict``, ``set``,
``frozenset``, plus the singletons ``None``/``Ellipsis``). For every class we
pick representative values and assert two properties:

* repeated ``marshal.dumps`` of the same object yields byte-identical output
  inside one process (repeatability / stability), and
* ``marshal.loads(marshal.dumps(value))`` round-trips back to an equivalent
  object (correctness).

The ``EQUIVALENCE_CLASSES`` table below documents, per class, exactly which
representatives are exercised so the coverage of marshal's supported object
types is auditable at a glance.
"""

from __future__ import annotations

import marshal

import pytest

from marshal_stability.cases import BASIC_CASES, UNSUPPORTED_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


# One equivalence class per marshal-supported fundamental type. Each entry maps
# a class name to a list of representative values drawn from that partition.
EQUIVALENCE_CLASSES: dict[str, list[object]] = {
    "none": [None],
    "ellipsis": [Ellipsis],
    "bool": [True, False],
    "int": [0, 1, -1, 42, 123456789, -987654321],
    "float": [0.0, -0.0, 1.5, -2.75, 3.141592653589793],
    "complex": [complex(1.0, 2.0), complex(-1.0, 0.0)],
    "str": ["", "abc", "中文", "emoji-😀", "line\nbreak"],
    "bytes": [b"", b"abc", b"\x00\x01\x02", bytes(range(16))],
    "tuple": [(), (1,), (1, "a", None), (1, (2, 3), 4)],
    "list": [[], [1], [1, "a", None], [[1], [2], [3]]],
    "dict": [{}, {"a": 1}, {"a": 1, "b": 2}, {1: "x", 2: "y"}],
    "set": [set(), {1}, {1, 2, 3}, {"a", "b"}],
    "frozenset": [frozenset(), frozenset({1}), frozenset({1, 2, 3})],
}


def _labeled_representatives() -> list[tuple[str, object]]:
    """Flatten EQUIVALENCE_CLASSES into (class_name, value) pairs for ids."""
    pairs: list[tuple[str, object]] = []
    for class_name, values in EQUIVALENCE_CLASSES.items():
        for index, value in enumerate(values):
            pairs.append((f"{class_name}[{index}]", value))
    return pairs


REPRESENTATIVES = _labeled_representatives()


@pytest.mark.parametrize(
    "value",
    [value for _, value in REPRESENTATIVES],
    ids=[label for label, _ in REPRESENTATIVES],
)
def test_equivalence_class_representative_is_stable(value):
    """Each equivalence-class representative serializes to identical bytes.

    Repeatability theory: within one process, ``marshal.dumps`` must be a pure
    function of its input, so calling it many times on the same object must
    return byte-for-byte identical output.
    """
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize(
    "value",
    [value for _, value in REPRESENTATIVES],
    ids=[label for label, _ in REPRESENTATIVES],
)
def test_equivalence_class_representative_round_trips(value):
    """Each equivalence-class representative round-trips back to itself."""
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


def test_every_supported_type_class_is_covered():
    """Guard: the equivalence table covers all targeted fundamental types.

    This keeps the partitioning honest -- if someone deletes a class the suite
    fails loudly instead of silently dropping coverage.
    """
    expected = {
        "none",
        "ellipsis",
        "bool",
        "int",
        "float",
        "complex",
        "str",
        "bytes",
        "tuple",
        "list",
        "dict",
        "set",
        "frozenset",
    }
    assert expected.issubset(EQUIVALENCE_CLASSES.keys())


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
    """Unsupported objects should fail predictably instead of silently corrupting.

    This exercises the *invalid* equivalence class: inputs outside marshal's
    supported domain must raise ``ValueError`` rather than emit unstable bytes.
    """
    with pytest.raises(ValueError):
        marshal.dumps(value)
