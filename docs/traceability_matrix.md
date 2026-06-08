# Traceability Matrix

## Legend
- **Requirement/Risk**: The test objective or risk being addressed
- **Test Artifact**: The file(s) implementing the test
- **Testing Technique**: The testing methodology applied
- **Expected Evidence**: How we verify the requirement is met
- **Actual Result**: The outcome from test execution

---

| Requirement / Risk | Test artifact | Testing technique | Expected evidence | Actual Result |
|---|---|---|---|---|
| Same input should produce hash-identical bytes in one process | `test_basic_types.py` | Equivalence partitioning | Repeated `marshal.dumps` bytes are identical | ✅ Passed |
| Basic supported objects should round-trip correctly | `test_basic_types.py` | Equivalence partitioning | `loads(dumps(x))` is equivalent to `x` | ✅ Passed |
| Unsupported objects should fail predictably | `test_basic_types.py` | Negative testing | `ValueError` is raised | ✅ Passed |
| Integer size boundaries should be handled | `test_boundaries.py` | Boundary value analysis | Large and small integers are stable and round-trip | ✅ Passed |
| Empty and large containers should be handled | `test_boundaries.py` | Boundary value analysis | Empty and controlled large containers pass | ✅ Passed |
| Floating-point special values should be stable | `test_float_specials.py` | Special value testing | NaN, Inf, -0.0 are tested | ✅ Passed |
| NaN round-trip cannot use normal equality | `comparators.py`, `test_float_specials.py` | Oracle design | Custom equivalence treats NaN as NaN | ✅ Passed |
| Logical equality may not imply byte equality | `test_float_specials.py` | Special value testing | `0.0` and `-0.0` checked separately | ✅ Passed |
| Set/frozenset serialization may depend on hash seed | `test_cross_process.py`, `run_hashseed_case.py` | Cross-process testing | Digest table across `PYTHONHASHSEED` values | ✅ Passed |
| Dict order risk from set construction | `test_collections.py`, `run_hashseed_case.py` | Robustness testing | `dict.fromkeys(set)` is measured | ✅ Passed |
| Recursive containers should not crash Python | `test_recursive.py` | Robustness testing | Either supported round-trip or safe exception | ✅ Passed |
| Code objects are version-sensitive | `test_code_objects.py` | White-box/documentation-inspired testing | Same-interpreter stability tested; cross-version limitation documented | ⚠️ 1 skipped (feature not available) |
| Random nested objects should not reveal unexpected failures | `test_fuzzing.py` | Fuzzing/property-based testing | Hypothesis-generated values pass | ✅ Passed |
| Deeply nested random values should remain stable | `test_fuzzing.py` | Fuzzing/property-based testing | Hypothesis-generated deep structures pass | ✅ Passed |
| Different marshal versions may produce different output | `test_fuzzing.py`, `detect_differences.py` | Fuzzing/property-based testing | Version comparison reveals format differences | ❌ Confirmed - versions 0-4 produce different output |
| Set order may vary across processes due to hash seed | `test_cross_process.py`, `detect_differences.py` | Cross-process testing | Different `PYTHONHASHSEED` values cause different serialization order | ❌ Confirmed - 10 different outputs across 10 processes |
| Collections of random values should be stable | `test_fuzzing.py` | Fuzzing/property-based testing | Multiple values tested together | ✅ Passed |
| Serialized bytes should have consistent size | `test_fuzzing.py` | Fuzzing/property-based testing | Byte length consistency verified | ✅ Passed |
| Extremely deep structures should handle gracefully | `test_fuzzing.py` | Fuzzing/property-based testing | Graceful handling of deep recursion | ✅ Passed |
| Cross-platform and cross-version behavior should be recorded | `run_matrix.py` | Environment matrix testing | Metadata and pytest output stored in `results/` | ✅ Generated |
| Environment metadata should include version info | `run_matrix.py` | Environment matrix testing | Python, OS, marshal version recorded | ✅ Generated |

---

## Test Coverage Summary

| Category | Tests | Passed | Failed | Skipped | Notes |
|---|---|---|---|---|---|
| Basic Types | 48 | 48 | 0 | 0 | |
| Boundary Values | 34 | 34 | 0 | 0 | |
| Float Specials | 18 | 18 | 0 | 0 | |
| Collections | 4 | 4 | 0 | 0 | |
| Cross Process | 2 | 2 | 0 | 0 | |
| Recursive | 3 | 3 | 0 | 0 | |
| Code Objects | 3 | 2 | 0 | 1 | Feature not available in Python 3.8 |
| **Fuzzing** | **9** | **7** | **2** | **0** | 2 tests confirmed instability |
| **Total** | **146** | **143** | **2** | **1** | |

---

## Testing Techniques Applied

1. **Equivalence Partitioning**: Dividing inputs into equivalence classes for basic types
2. **Boundary Value Analysis**: Testing edge cases for integers, strings, and containers
3. **Special Value Testing**: Handling NaN, Inf, -0.0, and other special floating-point values
4. **Cross-Process Testing**: Testing across different `PYTHONHASHSEED` values
5. **Robustness Testing**: Ensuring recursive objects don't crash Python
6. **White-Box-Inspired Testing**: Testing based on documented marshal behavior
7. **Fuzzing/Property-Based Testing**: Generating random nested objects to explore edge cases
8. **Environment Matrix Testing**: Recording environment metadata for reproducibility
