# Stability and Correctness Testing of Python's `marshal` Module

> Repository link: https://github.com/example/marshal-stability-tests

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

1. Basic type tests (`test_basic_types.py`)
2. Boundary value tests (`test_boundaries.py`)
3. Floating-point special value tests (`test_float_specials.py`)
4. Collection ordering and hash randomization tests (`test_collections.py`)
5. Recursive and cyclic object tests (`test_recursive.py`)
6. Code object tests (`test_code_objects.py`)
7. Fuzzing/property-based tests (`test_fuzzing.py`)
8. Cross-process tests (`test_cross_process.py`)
9. Environment matrix scripts (`scripts/run_matrix.py`)

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

### 3.6 Fuzzing / Property-Based Testing

The fuzzing tests use Hypothesis to generate nested marshal-supported objects.
The generator limits depth and container size to avoid excessive memory usage.

**Enhanced Fuzzing Coverage:**
- **Basic stability**: 500 random values tested for deterministic serialization
- **Round-trip correctness**: 500 random values tested for proper deserialization
- **Deep nesting testing**: Values with up to 8 levels of nesting (300 examples)
- **Version compatibility**: Testing across different marshal versions (200 examples)
- **Collection testing**: Multiple values tested together (200 examples)
- **Size consistency**: Verifying byte length consistency (100 examples)
- **Extreme depth**: Graceful handling of deeply recursive structures (1-20 levels)
- **Version differences detection**: Identifying output variations across versions (100 examples)
- **Byte-level consistency**: 100+ repeated dumps per value (200 examples)
- **Mixed type interactions**: Complex structures with multiple type combinations (100 examples)
- **Triple value combinations**: Testing interactions between three random values (150 examples)

Fuzzing was included because manually selected tests may miss unusual nested
combinations, especially combinations of dictionaries, lists, tuples, sets,
strings, bytes, and special floating-point values. The high number of examples
(1,400+ total fuzzing test cases) provides strong confidence in the stability
of marshal across diverse inputs.

### 3.7 Environment Matrix Testing

The `run_matrix.py` script automatically collects environment metadata and runs
the test suite. This includes:

- Python version and implementation details
- Operating system information
- Marshal version
- Environment variables (PYTHONHASHSEED, PYTHONPATH)
- Hardware information

The results are stored in a `results/` directory with unique run identifiers for
traceability and reproducibility.

### 3.8 White-Box-Inspired Testing

Although the suite treats `marshal` mostly as a black box, the selected test
groups are informed by documented marshal behavior and known internal concerns:
format versions, code objects, recursive objects, and type-specific encoding
paths. Full all-definitions/all-uses coverage of CPython's `marshal.c` was not
attempted because the project focuses on observable behavior across environments
rather than CPython implementation coverage.

## 4. Traceability Matrix

| Requirement / Risk | Test artifact | Technique | Expected evidence | Actual Result |
|---|---|---|---|---|
| Same input should produce identical bytes in one process | `test_basic_types.py` | Equivalence partitioning | Repeated dumps are identical | ✅ Passed |
| Supported values should round-trip correctly | `test_basic_types.py` | Equivalence partitioning | `loads(dumps(x))` is equivalent to `x` | ✅ Passed |
| Unsupported values should fail safely | `test_basic_types.py` | Negative testing | `ValueError` is raised | ✅ Passed |
| Integer and length boundaries should be tested | `test_boundaries.py` | Boundary value analysis | Boundary cases pass | ✅ Passed |
| Floating-point special values should be tested | `test_float_specials.py` | Special value testing | NaN, Inf, and -0.0 covered | ✅ Passed |
| NaN needs a custom oracle | `comparators.py`, `test_float_specials.py` | Oracle design | NaN round-trip checked correctly | ✅ Passed |
| Set order may depend on hash seed | `test_cross_process.py`, `run_hashseed_case.py` | Cross-process testing | Digest table across seeds | ✅ Passed |
| Recursive containers should not crash | `test_recursive.py` | Robustness testing | Safe exception or valid round-trip | ✅ Passed |
| Code objects are version-sensitive | `test_code_objects.py` | White-box/documentation-inspired | Same-version stability tested | ⚠️ 1 skipped |
| Random nested objects should be covered | `test_fuzzing.py` | Fuzzing | Hypothesis cases pass | ✅ Passed |
| Deeply nested random values should be stable | `test_fuzzing.py` | Fuzzing | Deep structures pass | ✅ Passed |
| Values should be stable across marshal versions | `test_fuzzing.py` | Fuzzing | Version compatibility verified | ✅ Passed |
| Collections of random values should be stable | `test_fuzzing.py` | Fuzzing | Multiple values tested | ✅ Passed |
| Serialized bytes should have consistent size | `test_fuzzing.py` | Fuzzing | Size consistency verified | ✅ Passed |
| Cross-environment behavior should be recorded | `run_matrix.py` | Environment matrix | Metadata and result files produced | ✅ Generated |

## 5. Findings

### 5.1 Test Results Summary

| Category | Tests | Passed | Failed | Skipped |
|---|---|---|---|---|
| Basic Types | 48 | 48 | 0 | 0 |
| Boundary Values | 41 | 41 | 0 | 0 |
| Float Specials | 21 | 21 | 0 | 0 |
| Collections | 8 | 8 | 0 | 0 |
| Cross Process | 2 | 2 | 0 | 0 |
| Recursive | 3 | 3 | 0 | 0 |
| Code Objects | 3 | 2 | 0 | 1 |
| **Fuzzing** | **11** | **11** | **0** | **0** |
| **Total** | **167** | **166** | **0** | **1** |

### 5.2 Environment Details

The test suite was executed on the following environment:

| Property | Value |
|---|---|
| Python Version | 3.8.6 (64-bit) |
| Implementation | CPython |
| OS | Windows 10 (10.0.26100) |
| Architecture | AMD64 |
| Marshal Version | 4 |
| CPU Cores | 20 |
| Duration | 19.10 seconds |

### 5.3 Key Observations

1. **Basic Stability Verified**: All basic types (None, bool, int, float, str, bytes, containers) are stable under repeated serialization within a single process.

2. **NaN Handling Correct**: The custom equivalence function correctly handles NaN comparisons, where `nan != nan` in Python but should be considered equivalent after round-trip.

3. **Boundary Values Handled**: Integer boundaries (`2**31`, `2**63`, etc.) and container size boundaries (0, 1, 255, 256, 1024, 4096, 16384 elements) are all handled correctly.

4. **Floating-Point Precision Boundaries**: Extended testing of floating-point edge cases including `sys.float_info.max/min/epsilon`, hex-represented floats, and precision boundaries (`2.0 ± 2**-52`) all demonstrated stable serialization.

5. **Complex Numbers Stable**: Complex numbers with special values (NaN, Inf) in both real and imaginary parts are handled correctly.

6. **Large Container Stability**: Containers with up to 16,384 elements (strings, bytes, lists) and mixed large containers (1000+ elements) maintain serialization stability.

7. **Fuzzing Coverage Effective**: The enhanced fuzzing tests with Hypothesis successfully explored:
   - Deeply nested structures (up to 8 levels)
   - Various type combinations
   - Multiple marshal versions
   - Collection scenarios
   - Byte-level consistency across 100+ dumps
   - Mixed type interactions in complex structures
   - Triple value combinations

8. **No Version Differences Detected**: Testing across marshal versions (0-4) did not reveal unexpected output differences for supported types.

9. **Set Order Consistency**: Within a single process, set and frozenset serialization produces consistent output, indicating that hash randomization does not affect same-process serialization.

10. **Code Object Limitation**: One test was skipped due to `allow_code` feature not being available in Python 3.8. This is a documented limitation.

11. **Environment Metadata Captured**: The `run_matrix.py` script successfully captured comprehensive environment information for reproducibility.

### 5.4 Test Environment Matrix

| Environment | Python version | OS | Failed tests | Main observation |
|---|---|---|---|---|
| Test Run 1 | 3.8.6 | Windows 10 | 0 | All tests passed except 1 skipped |

## 6. Limitations

The test suite has several limitations:

1. **Determinism Proof**: It cannot prove complete determinism for all possible marshal-supported objects.

2. **Fuzzing Boundaries**: Fuzzing is bounded by maximum depth (8 levels), maximum container size (8 elements), and the number of generated examples (500 per test).

3. **Cross-Platform Coverage**: Cross-platform conclusions depend on the actual environments available for testing. Currently tested only on Windows 10.

4. **Source-Level Coverage**: The suite does not perform full source-level coverage analysis of CPython's `marshal.c`.

5. **Memory Constraints**: Extremely large inputs are tested only up to controlled sizes to avoid memory exhaustion.

6. **CPython Focus**: The tests focus on Python's standard CPython implementation and do not fully evaluate alternative Python implementations (PyPy, Jython, etc.).

## 7. Conclusion

The test suite provides a systematic investigation of `marshal` stability and
correctness using equivalence partitioning, boundary value analysis, special
value testing, fuzzing, robustness testing, and cross-process experiments.

### Key Conclusions

1. **Stability**: Python's `marshal` module is generally stable for most common objects within a single interpreter process. Repeated `marshal.dumps()` calls produce identical byte streams.

2. **Correctness**: Round-trip serialization (`loads(dumps(x))`) correctly reconstructs values, including special cases like NaN.

3. **Fuzzing Effectiveness**: Property-based testing with Hypothesis successfully explored edge cases and nested combinations that manual testing might miss.

4. **Environment Traceability**: The environment matrix testing ensures that test results are traceable to specific Python versions, OS configurations, and marshal versions.

5. **Limitations Acknowledged**: As documented, code objects have version-specific limitations, and cross-process hash seed variations can affect set serialization order.

### Recommendations

1. **Multi-Environment Testing**: Run the test suite on multiple Python versions (3.7, 3.8, 3.9, 3.10, 3.11) and operating systems (Linux, macOS) for comprehensive coverage.

2. **Continuous Integration**: Integrate the test suite into CI/CD pipelines to catch regressions early.

3. **Performance Testing**: Add performance benchmarks to measure marshal serialization speed across different object types and sizes.

4. **Edge Case Expansion**: Continue expanding fuzzing coverage to include more complex nested scenarios and rare type combinations.
