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


def test_large_list_boundaries():
    """Test large list boundaries for stability."""
    # 测试不同大小的列表
    sizes = [0, 1, 255, 256, 1024, 4096, 16384]
    for size in sizes:
        large_list = list(range(size))
        assert repeated_dumps_are_identical(large_list, repeats=3), f"Unstable list size {size}"


def test_large_dict_boundaries():
    """Test large dictionary boundaries for stability."""
    sizes = [0, 1, 255, 256, 1024, 4096]
    for size in sizes:
        large_dict = {str(i): i for i in range(size)}
        assert repeated_dumps_are_identical(large_dict, repeats=3), f"Unstable dict size {size}"


def test_large_set_boundaries():
    """Test large set boundaries for stability."""
    sizes = [0, 1, 255, 256, 1024]
    for size in sizes:
        large_set = set(range(size))
        assert repeated_dumps_are_identical(large_set, repeats=3), f"Unstable set size {size}"


def test_large_string_boundaries():
    """Test large string boundaries for stability."""
    sizes = [0, 1, 255, 256, 1024, 4096, 16384]
    for size in sizes:
        large_string = "a" * size
        assert repeated_dumps_are_identical(large_string, repeats=3), f"Unstable string size {size}"


def test_large_bytes_boundaries():
    """Test large bytes boundaries for stability."""
    sizes = [0, 1, 255, 256, 1024, 4096, 16384]
    for size in sizes:
        large_bytes = b"x" * size
        assert repeated_dumps_are_identical(large_bytes, repeats=3), f"Unstable bytes size {size}"


def test_mixed_large_containers():
    """Test mixed large containers for stability."""
    # 混合类型的大容器
    mixed = {
        "list": list(range(1000)),
        "dict": {str(i): i for i in range(500)},
        "set": set(range(500)),
        "string": "test" * 1000,
        "bytes": b"data" * 1000,
    }
    assert repeated_dumps_are_identical(mixed, repeats=3)
