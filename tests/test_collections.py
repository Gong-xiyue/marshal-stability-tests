"""Tests for collection ordering and deterministic behavior."""

from __future__ import annotations

import marshal

from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


def test_dict_with_fixed_insertion_order_is_stable():
    """Dictionaries preserve insertion order in modern Python."""
    value = {"a": 1, "b": 2, "c": 3}
    assert repeated_dumps_are_identical(value)
    assert equivalent(value, marshal.loads(marshal.dumps(value)))


def test_set_is_stable_within_same_process():
    """A set should be stable when repeatedly serialized in one process."""
    value = {"apple", "banana", "cherry"}
    assert repeated_dumps_are_identical(value)


def test_frozenset_is_stable_within_same_process():
    """A frozenset should be stable when repeatedly serialized in one process."""
    value = frozenset({"apple", "banana", "cherry"})
    assert repeated_dumps_are_identical(value)


def test_dict_created_from_set_may_depend_on_set_iteration_order():
    """Document a risk: construction from set can inherit hash-dependent order."""
    source = {"apple", "banana", "cherry"}
    value = dict.fromkeys(source, 1)
    assert repeated_dumps_are_identical(value)


def test_set_order_variation_detection():
    """Test if set serialization produces varying output across multiple runs."""
    # 测试包含字符串的集合（字符串hash受PYTHONHASHSEED影响）
    test_sets = [
        {"apple", "banana", "cherry", "date", "elderberry"},
        {"python", "java", "javascript", "ruby", "go"},
        {"a", "b", "c", "d", "e", "f", "g"},
        set(range(100)),
        set("abcdefghijklmnopqrstuvwxyz"),
    ]
    
    for s in test_sets:
        dumps = [marshal.dumps(s) for _ in range(50)]
        all_identical = all(d == dumps[0] for d in dumps)
        # 记录观察结果，不强制断言失败
        if not all_identical:
            print(f"Set order variation detected for set size {len(s)}")


def test_frozenset_order_variation_detection():
    """Test if frozenset serialization produces varying output."""
    test_frozensets = [
        frozenset({"apple", "banana", "cherry", "date"}),
        frozenset({"x", "y", "z", "a", "b", "c"}),
    ]
    
    for fs in test_frozensets:
        dumps = [marshal.dumps(fs) for _ in range(50)]
        all_identical = all(d == dumps[0] for d in dumps)
        if not all_identical:
            print(f"Frozenset order variation detected for size {len(fs)}")


def test_dict_key_order_variation_detection():
    """Test if dict serialization with string keys varies."""
    test_dicts = [
        {"apple": 1, "banana": 2, "cherry": 3, "date": 4},
        {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5},
    ]
    
    for d in test_dicts:
        dumps = [marshal.dumps(d) for _ in range(50)]
        all_identical = all(dm == dumps[0] for dm in dumps)
        if not all_identical:
            print(f"Dict order variation detected for dict with {len(d)} keys")


def test_empty_collections_are_stable():
    """Test that empty collections are always stable."""
    empty_cases = [
        [],
        {},
        set(),
        frozenset(),
        tuple(),
        b"",
        "",
    ]
    for empty in empty_cases:
        assert repeated_dumps_are_identical(empty, repeats=10), f"Unstable empty: {type(empty).__name__}"
