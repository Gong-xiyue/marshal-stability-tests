#test collection ordering and deterministic behavior

import marshal

from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import repeated_dumps_are_identical


def test_dict_insertion_order_stable():
    value = {"a": 1, "b": 2, "c": 3}
    assert repeated_dumps_are_identical(value)
    assert equivalent(value, marshal.loads(marshal.dumps(value)))


def test_set_stable_in_process():
    value = {"apple", "banana", "cherry"}
    assert repeated_dumps_are_identical(value)


def test_frozenset_stable_in_process():
    value = frozenset({"apple", "banana", "cherry"})
    assert repeated_dumps_are_identical(value)


def test_dict_equivalence_classes():
    classes = {
        "literal": {"a": 1, "b": 2},
        "fromkeys_fixed": dict.fromkeys(["x", "y", "z"], 0),
        "dict_zip": dict(zip(["a", "b"], [1, 2])),
        "dict_comprehension": {str(i): i for i in range(5)},
    }
    for name, d in classes.items():
        assert repeated_dumps_are_identical(d), f"dict '{name}' is unstable"
        assert equivalent(d, marshal.loads(marshal.dumps(d))), (
            f"dict '{name}' round-trip failed"
        )


def test_set_equivalence_classes():
    classes = {
        "int_set": {1, 2, 3},
        "str_set": {"a", "b", "c"},
        "mixed_set": {1, "a", (1, 2)},
        "empty_set": set(),
        "single_set": {42},
    }
    for name, s in classes.items():
        assert repeated_dumps_are_identical(s), f"set '{name}' is unstable"


def test_dict_from_set_depends_on_order():
    source = {"apple", "banana", "cherry"}
    value = dict.fromkeys(source, 1)
    assert repeated_dumps_are_identical(value)


def test_dict_with_nan_keys():
    # Dict with NaN keys: NaN != NaN, but marshal should still handle it.
    import math
    value = {float("nan"): 1, float("-nan"): 2}
    restored = marshal.loads(marshal.dumps(value))
    assert len(restored) == len(value)
    for k in restored:
        assert math.isnan(k)


def test_dict_mixed_key_types():
    # Dict with mixed key types should round-trip correctly.
    value = {
        None: "none",
        True: "true",
        42: "int",
        3.14: "float",
        "key": "string",
        (1, 2): "tuple",
    }
    restored = marshal.loads(marshal.dumps(value))
    assert restored == value


def test_nested_empty_containers():
    # Empty containers nested inside other containers.
    cases = [
        {"a": [], "b": {}},
        {"a": (), "b": set()},
        [[], {}, ()],
        (set(), frozenset()),
    ]
    for value in cases:
        restored = marshal.loads(marshal.dumps(value))
        assert type(restored) is type(value)
        assert restored == value
