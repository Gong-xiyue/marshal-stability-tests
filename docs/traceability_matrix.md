# Traceability Matrix

| Requirement / Risk | Test artifact | Testing technique | Expected evidence |
|---|---|---|---|
| Same input should produce hash-identical bytes in one process | `test_basic_types.py` | Equivalence partitioning | Repeated `marshal.dumps` bytes are identical |
| Basic supported objects should round-trip correctly | `test_basic_types.py` | Equivalence partitioning | `loads(dumps(x))` is equivalent to `x` |
| Unsupported objects should fail predictably | `test_basic_types.py` | Negative testing | `ValueError` is raised |
| Integer size boundaries should be handled | `test_boundaries.py` | Boundary value analysis | Large and small integers are stable and round-trip |
| Empty and large containers should be handled | `test_boundaries.py` | Boundary value analysis | Empty and controlled large containers pass |
| Floating-point special values should be stable | `test_float_specials.py` | Special value testing | NaN, Inf, -0.0 are tested |
| NaN round-trip cannot use normal equality | `comparators.py`, `test_float_specials.py` | Oracle design | Custom equivalence treats NaN as NaN |
| Logical equality may not imply byte equality | `test_float_specials.py` | Special value testing | `0.0` and `-0.0` checked separately |
| Set/frozenset serialization may depend on hash seed | `test_cross_process.py`, `run_hashseed_case.py` | Cross-process testing | Digest table across `PYTHONHASHSEED` values |
| Dict order risk from set construction | `test_collections.py`, `run_hashseed_case.py` | Robustness testing | `dict.fromkeys(set)` is measured |
| Recursive containers should not crash Python | `test_recursive.py` | Robustness testing | Either supported round-trip or safe exception |
| Code objects are version-sensitive | `test_code_objects.py` | White-box/documentation-inspired testing | Same-interpreter stability tested; cross-version limitation documented |
| Random nested objects should not reveal unexpected failures | `test_fuzzing.py` | Fuzzing/property-based testing | Hypothesis-generated values pass |
| Cross-platform and cross-version behavior should be recorded | `run_matrix.py` | Environment matrix testing | Metadata and pytest output stored in `results/` |
