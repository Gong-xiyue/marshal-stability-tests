"""Property-based fuzzing tests for marshal-supported values."""

from __future__ import annotations

import marshal
from typing import Any

from hypothesis import given, settings, strategies as st

from marshal_stability.comparators import equivalent
from marshal_stability.generators import marshal_supported_values
from marshal_stability.hash_utils import repeated_dumps_are_identical, dumps_bytes


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


@given(marshal_supported_values(max_depth=8))
@settings(max_examples=300, deadline=None)
def test_fuzzed_values_deep_nesting(value):
    """Deeply nested random values should remain stable."""
    assert repeated_dumps_are_identical(value, repeats=5)


@given(marshal_supported_values())
@settings(max_examples=200, deadline=None)
def test_fuzzed_values_across_marshal_versions(value):
    """Random values should be stable across different marshal versions."""
    for version in range(0, marshal.version + 1):
        try:
            assert repeated_dumps_are_identical(value, repeats=3, version=version)
        except ValueError:
            pass  # Some types are not supported in older versions


@given(
    st.lists(
        marshal_supported_values(max_depth=2),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=200, deadline=None)
def test_fuzzed_collection_of_values(values):
    """Collections of random values should be stable."""
    for value in values:
        assert repeated_dumps_are_identical(value, repeats=3)


@given(marshal_supported_values())
@settings(max_examples=100, deadline=None)
def test_fuzzed_values_size_consistency(value):
    """Serialized bytes should have consistent size across repeated dumps."""
    first_bytes = dumps_bytes(value)
    for _ in range(10):
        assert len(dumps_bytes(value)) == len(first_bytes)


def _nested_structure(depth: int) -> Any:
    """Create a deeply nested structure for testing."""
    if depth == 0:
        return 42
    return [_nested_structure(depth - 1)]


@settings(max_examples=10, deadline=None)
@given(st.integers(min_value=1, max_value=20))
def test_extreme_depth_stability(depth):
    """Extremely deep nested structures should handle gracefully."""
    try:
        value = _nested_structure(depth)
        assert repeated_dumps_are_identical(value, repeats=3)
    except (RecursionError, ValueError):
        pass  # Expected for extremely deep structures


@given(marshal_supported_values(max_depth=3))
@settings(max_examples=100, deadline=None)
def test_version_output_differences(value):
    """Detect if different marshal versions produce different output."""
    outputs = {}
    
    for version in range(0, marshal.version + 1):
        try:
            outputs[version] = marshal.dumps(value, version)
        except ValueError:
            pass  # Some types not supported in older versions
    
    # 检查是否有不同版本产生不同输出
    if len(set(outputs.values())) > 1:
        print(f"Version differences detected for {type(value).__name__}")


@given(marshal_supported_values())
@settings(max_examples=200, deadline=None)
def test_byte_consistency_across_multiple_dumps(value):
    """Test byte-level consistency across many dumps."""
    first_dump = marshal.dumps(value)
    # 进行多次序列化，检测是否有任何差异
    for i in range(100):
        current_dump = marshal.dumps(value)
        if current_dump != first_dump:
            print(f"Byte inconsistency detected for {type(value).__name__} at iteration {i}")
            break


@given(st.lists(marshal_supported_values(max_depth=2), min_size=5, max_size=15))
@settings(max_examples=100, deadline=None)
def test_mixed_type_interactions(values):
    """Test interactions between different types in complex structures."""
    # 创建混合类型的复杂结构
    complex_structure = {
        "list": list(values),
        "tuple": tuple(values),
        "set": set(v for v in values if isinstance(v, (int, str, bool))),
        "nested": [[v] for v in values[:5]],
        "dict": {str(i): v for i, v in enumerate(values[:10])}
    }
    
    assert repeated_dumps_are_identical(complex_structure, repeats=5)


@given(
    st.tuples(
        marshal_supported_values(),
        marshal_supported_values(),
        marshal_supported_values()
    )
)
@settings(max_examples=150, deadline=None)
def test_triple_value_combinations(values):
    """Test combinations of three random values together."""
    # 测试三个值的各种组合
    combinations = [
        list(values),
        tuple(values),
        {"a": values[0], "b": values[1], "c": values[2]},
        [values[0], {"nested": values[1]}, values[2]],
    ]
    
    for combo in combinations:
        assert repeated_dumps_are_identical(combo, repeats=3)
