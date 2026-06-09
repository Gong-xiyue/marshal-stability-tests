#test float specials,include nan,inf,-inf,0.0,-0.0,denormalized floats

import marshal
import math

import pytest

from marshal_stability.cases import FLOAT_CASES
from marshal_stability.comparators import equivalent
from marshal_stability.hash_utils import dumps_bytes, repeated_dumps_are_identical


@pytest.mark.parametrize("value", FLOAT_CASES)
def test_float_stable_in_process(value):
    assert repeated_dumps_are_identical(value)


@pytest.mark.parametrize("value", FLOAT_CASES)
def test_float_round_trip(value):
    restored = marshal.loads(marshal.dumps(value))
    assert equivalent(value, restored)


def test_zero_bytes_differ():
    assert 0.0 == -0.0
    assert dumps_bytes(0.0) != dumps_bytes(-0.0)


def test_nan_round_trip_is_nan():
    restored = marshal.loads(marshal.dumps(float("nan")))
    assert math.isnan(restored)


def test_multi_nan_round_trip():
    nan_values = [
        float("nan"),
        float("-nan"),
        float("inf") - float("inf"),
    ]
    for val in nan_values:
        restored = marshal.loads(marshal.dumps(val))
        assert math.isnan(restored)


def test_float_extremes():
    import sys
    values = [sys.float_info.max, sys.float_info.min, sys.float_info.epsilon]
    for val in values:
        restored = marshal.loads(marshal.dumps(val))
        assert restored == val


def test_denormalized_floats():
    import sys
    tiny = sys.float_info.min / 2.0 ** 52
    values = [tiny, tiny * 2, sys.float_info.min / 2.0]
    for val in values:
        restored = marshal.loads(marshal.dumps(val))
        assert restored == val


def test_nan_as_dict_key():
    value = {float("nan"): "hello"}
    data = marshal.dumps(value)
    restored = marshal.loads(data)
    assert len(restored) == 1
    for k in restored:
        assert math.isnan(k)
    assert list(restored.values())[0] == "hello"


def test_nan_in_set():
    value = {float("nan")}
    restored = marshal.loads(marshal.dumps(value))
    assert len(restored) == 1
    for v in restored:
        assert math.isnan(v)


def test_zero_as_dict_keys():
    value = {0.0: "zero", -0.0: "neg_zero"}
    # Python treats them as the same dict key
    assert len(value) == 1
    restored = marshal.loads(marshal.dumps(value))
    assert len(restored) == 1


def test_infinity_in_dict():
    value = {float("inf"): "inf", float("-inf"): "neg_inf"}
    restored = marshal.loads(marshal.dumps(value))
    assert len(restored) == 2
    for k in restored:
        assert k == float("inf") or k == float("-inf")
