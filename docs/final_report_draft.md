# Stability and Correctness Testing of Python's `marshal` Module

> Repository link: TODO: insert GitHub/GitLab link here.

## 1. Introduction

This project investigates the stability and correctness of Python's internal
`marshal` serialization module. The central question is whether the same input
always produces the same hash-identical byte stream when serialized with
`marshal.dumps`.

We define stability as byte-level identity: for a value `x`, repeated calls to
`marshal.dumps(x)` should produce exactly the same bytes. Logical equivalence is
not sufficient. For example, two values may compare equal in Python while still
having different binary representations.

We define correctness mainly as round-trip preservation:
`marshal.loads(marshal.dumps(x))` should reconstruct a value equivalent to `x`
for supported marshal types. Some values, such as `float("nan")`, require a
custom equivalence oracle because normal equality is not suitable.

The official Python documentation states that `marshal` exists mainly to support
`.pyc` files, that its format is intentionally undocumented, and that it may
change between Python versions. Therefore, cross-version differences are treated
as documented limitations unless they cause unexpected crashes or violate
same-version behavior.

## 2. Test Suite Overview

The test suite is organized into the following groups:

1. Basic type tests
2. Boundary value tests
3. Floating-point special value tests
4. Collection ordering and hash randomization tests
5. Recursive and cyclic object tests
6. Code object tests
7. Fuzzing/property-based tests
8. Cross-process and cross-environment scripts

The tests are implemented with `pytest`. Fuzzing uses `hypothesis`. The helper
modules under `src/marshal_stability` provide hashing utilities, test data,
custom comparison logic, and random value generators.

## 3. Testing Strategies

### 3.1 Equivalence Partitioning

We divided marshal inputs into major supported equivalence classes:

- singleton values: `None`, `True`, `False`, `Ellipsis`, `StopIteration`
- numeric values: integers, floats, complex numbers
- text and binary values: `str`, `bytes`
- sequence values: `tuple`, `list`
- mapping values: `dict`
- set-like values: `set`, `frozenset`
- code objects
- unsupported objects such as ordinary instances and functions

This technique was chosen because marshal supports only a limited set of Python
internal object types. Testing at least one representative from each class gives
broad functional coverage without relying only on random inputs.

### 3.2 Boundary Value Analysis

Boundary value analysis was used for values likely to trigger different internal
encoding paths:

- `0`, `1`, `-1`
- `2**31 - 1`, `2**31`, `-2**31`
- `2**63 - 1`, `2**63`, `-2**63`
- very large integers such as `10**100`
- empty strings, one-character strings, 255-character strings, 256-character strings
- empty containers, one-element containers, and controlled large containers

We used this technique because serialization formats often have different
branches for small and large lengths or small and large integers.

### 3.3 Special Value Testing

Floating-point values received separate tests because they can behave differently
from ordinary values. The suite includes `0.0`, `-0.0`, infinities, NaN, and
extreme values from `sys.float_info`.

NaN cannot be checked with normal equality because `nan != nan`. Therefore, the
test suite implements a custom equivalence function that treats two NaN values
as equivalent if both are NaN.

### 3.4 Cross-Process Testing

The suite includes a script that runs child Python processes with different
`PYTHONHASHSEED` values. This is important because set iteration order can depend
on hash randomization. If a set is serialized by iteration order, the resulting
marshal byte stream may differ across processes even if the logical set contents
are the same.

This technique was chosen because repeated serialization inside a single process
is not enough to detect hash-seed-related instability.

### 3.5 Recursive and Robustness Testing

The test suite includes recursive lists and dictionaries. These tests do not
require every interpreter version to successfully serialize recursive objects.
Instead, they check that the behavior is safe: either the object is serialized
and restored correctly, or Python raises a normal exception such as `ValueError`,
`TypeError`, or `RecursionError`.

### 3.6 Fuzzing

The fuzzing tests use Hypothesis to generate nested marshal-supported objects.
The generator limits depth and container size to avoid excessive memory usage.

Fuzzing was included because manually selected tests may miss unusual nested
combinations, especially combinations of dictionaries, lists, tuples, sets,
strings, bytes, and special floating-point values.

### 3.7 White-Box-Inspired Testing

Although the suite treats `marshal` mostly as a black box, the selected test
groups are informed by documented marshal behavior and known internal concerns:
format versions, code objects, recursive objects, and type-specific encoding
paths. Full all-definitions/all-uses coverage of CPython's `marshal.c` was not
attempted because the project focuses on observable behavior across environments
rather than CPython implementation coverage.

## 4. Traceability Matrix

| Requirement / Risk | Test artifact | Technique | Expected evidence |
|---|---|---|---|
| Same input should produce identical bytes in one process | `test_basic_types.py` | Equivalence partitioning | Repeated dumps are identical |
| Supported values should round-trip correctly | `test_basic_types.py` | Equivalence partitioning | `loads(dumps(x))` is equivalent to `x` |
| Unsupported values should fail safely | `test_basic_types.py` | Negative testing | `ValueError` is raised |
| Integer and length boundaries should be tested | `test_boundaries.py` | Boundary value analysis | Boundary cases pass |
| Floating-point special values should be tested | `test_float_specials.py` | Special value testing | NaN, Inf, and -0.0 covered |
| NaN needs a custom oracle | `comparators.py` | Oracle design | NaN round-trip checked correctly |
| Set order may depend on hash seed | `test_cross_process.py`, `run_hashseed_case.py` | Cross-process testing | Digest table across seeds |
| Recursive containers should not crash | `test_recursive.py` | Robustness testing | Safe exception or valid round-trip |
| Code objects are version-sensitive | `test_code_objects.py` | White-box/documentation-inspired | Same-version stability tested |
| Random nested objects should be covered | `test_fuzzing.py` | Fuzzing | Hypothesis cases pass |
| Cross-environment behavior should be recorded | `run_matrix.py` | Environment matrix | Metadata and result files produced |

## 5. Findings

> Replace this section with your actual results after running the suite.

Preliminary expected observations:

1. Most basic objects are stable under repeated serialization in the same Python
   process.
2. Floating-point NaN requires custom equality checking for round-trip tests.
3. `0.0` and `-0.0` compare equal in Python but may serialize to different byte
   streams, showing why logical equality is not enough for this assignment.
4. Sets and frozensets containing strings may produce different bytes across
   processes with different `PYTHONHASHSEED` values.
5. Dictionaries created with fixed insertion order are expected to be stable,
   while dictionaries created from sets may inherit hash-dependent insertion
   order.
6. Code objects should be treated as same-interpreter-only test subjects because
   Python documents them as incompatible across Python versions.
7. Cross-version marshal output differences should be classified as documented
   instability, not necessarily as bugs.

After running the test suite, fill in a table like this:

| Environment | Python version | OS | Failed tests | Main observation |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |
| TODO | TODO | TODO | TODO | TODO |

## 6. Limitations

The test suite has several limitations:

1. It cannot prove complete determinism for all possible marshal-supported
   objects.
2. Fuzzing is bounded by maximum depth, maximum container size, and the number of
   generated examples.
3. Cross-platform conclusions depend on the actual environments available to the
   group.
4. The suite does not perform full source-level coverage analysis of CPython's
   `marshal.c`.
5. Extremely large inputs are tested only up to controlled sizes to avoid memory
   exhaustion.
6. The tests focus on Python's standard CPython implementation and do not fully
   evaluate alternative Python implementations.

## 7. Conclusion

The test suite provides a systematic investigation of `marshal` stability and
correctness using equivalence partitioning, boundary value analysis, special
value testing, fuzzing, robustness testing, and cross-process experiments. The
main expected conclusion is that `marshal` is generally stable for many ordinary
objects within a single interpreter process, but it should not be treated as a
general-purpose deterministic serialization format across Python versions,
process hash seeds, or code object formats.
