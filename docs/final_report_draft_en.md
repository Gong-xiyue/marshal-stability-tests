# Marshal Module Stability Test Report

# Repository: https://github.com/Gong-xiyue/marshal-stability-tests.git

## 1. Introduction

### 1.1 Background

The `marshal` module is Python's built-in serialization module, used for reading and writing Python module's pseudo-compiled bytecode. Although its format is designed to be architecture-independent, it is not stable across different Python versions. This test suite aims to verify: **Does the same input always produce the same (serialized) output?**

We define "same" as **hash-identical**, meaning the input must produce the same marshal byte stream in all cases.

### 1.2 Test Coverage and Traceability Matrix

| Module/Requirement | Test Dimension | Test File | Test Technique | Test Objective/Expected Evidence | Result |
| --------- | ------------------------------------------------------ | -------------------------------- | ------- | ------------- | ---- |
| Basic Type Testing | None, bool, int, float, complex, str, bytes, bytearray | `test_basic_types.py` | Equivalence Partitioning | Verify serialization stability of basic types, repeated dumps produce identical bytes | ✅ |
| Boundary Value Testing | Empty/large containers, integer boundaries, string lengths | `test_boundaries.py` | Boundary Value Analysis | Verify boundary case handling, boundary containers stable | ✅ |
| Shared Reference Testing | Same object referenced multiple times | `test_basic_types.py` | White-box Reference Handling | Verify correct handling of shared references | ✅ |
| Float Special Value Testing | NaN, Infinity, -0.0, precision boundaries | `test_float_specials.py` | Special Value Testing | Verify serialization of special float values | ✅ |
| Negative Testing | Unsupported input types | `test_basic_types.py` | Negative Testing | Verify correct exception handling | ✅ |
| Collection Testing | dict, set, frozenset | `test_collections.py` | Equivalence Partitioning | Verify serialization of collection types | ✅ |
| Recursive Container Testing | Self-referencing containers, circular references, deep nesting | `test_recursive.py` | Robustness Testing | Verify correct handling of recursive structures | Failed at depth 1000 |
| Code Object Testing | Functions/Lambda/closures | `test_code_objects.py` | White-box Inspired Testing | Verify serialization of code objects, stable within same version | ✅ |
| Cross-Process Testing | Inter-process data transfer, float precision | `test_cross_process.py` | Cross-Process Testing | Verify serialization stability across processes | Float precision stable, set order unstable |
| Hash Seed Testing | Different PYTHONHASHSEED values | `scripts/run_hashseed_case.py` | Hash Seed Testing | Verify hash seed impact on serialization | String sets unstable, integer sets stable |
| Fuzzing Testing | Random nested structures | `test_fuzzing.py` | Property-based Testing | Explore random boundary cases | ✅ |
| Cross-Version Testing | Python 3.9/3.11/3.12 | `test_cross_version_enhanced.py` | Cross-Version Testing | Verify version compatibility | Different versions produce different results |
| Cross-Version Deserialization | Data migration between versions | `test_cross_version_enhanced.py` | Compatibility Testing | Verify cross-version deserialization | Different versions produce different results |
| Cross-Platform Testing | Linux vs Windows | `compare_cross_platform.py` | Cross-Platform Testing | Detect platform differences | Different platforms produce different results |
| bytearray Type Preservation | bytearray vs bytes type preservation | `test_bytearray_bytes.py` | Type Comparison Testing | Discovered BUG: bytearray becomes bytes after round-trip | ❌ |
| bytearray Boundary Values | bytearray/bytes boundary sizes | `test_bytearray_bytes.py` | Boundary Value Analysis | Verify byte types of different sizes | ❌ |
| bytearray in Nested Containers | bytearray in lists | `test_bytearray_bytes.py` | Container Testing | Type preservation in lists | ❌ |
| bytes Type Preservation | bytes round-trip type preservation | `test_bytearray_bytes.py` | Type Comparison Testing | Type remains unchanged after round-trip | ✅ |
| Garbage Data Testing | Random byte deserialization | `test_bytearray_bytes.py` | Negative Testing | Verify garbage data throws exceptions | ✅ |
| Non-ASCII Strings | Non-ASCII string handling | `test_bytearray_bytes.py` | Special Value Testing | Correct round-trip | ✅ |
| Environment Matrix Testing | Python/OS/marshal version recording | `scripts/run_matrix.py` | Environment Matrix Testing | Ensure test traceability | ✅ |
| Marshal Version Differences | Different marshal format versions | `detect_differences.py` | Comparison Testing | Version difference confirmation | Stable for NoneType, bool; unstable for other types |

### 1.3 Test Statistics


**Overall Results**: A total of 337 test cases, 309 passed (92%), 28 failed. Basic types, float special values, recursive containers, and code objects all passed; cross-platform testing had the lowest pass rate (40%), mainly affected by sets and code objects.


***

## 3. Testing Strategies

### 3.1 Equivalence Partitioning
**Location**: `test_basic_types.py`  
**Method**: Partition the input domain of `marshal.dumps` into equivalence classes, each corresponding to a basic Python type supported by marshal. Select representative values for each class to verify repeatability and round-trip correctness.  
**Coverage**: None, Ellipsis, bool, int (0, 1, -1, 42, 123456789, -987654321), float (0.0, -0.0, 1.5, -2.75, 3.141592653589793), complex (including NaN), str (empty/normal/Chinese/emoji/newline), bytes, bytearray, tuple, list, dict, set, frozenset

### 3.2 Boundary Value Analysis
**Location**: `test_boundaries.py`  
**Method**: Test boundary values of marshal's key dimensions (defects tend to cluster at input range edges).  
**Coverage**: Integer boundaries (0, 1, -1, 2^31-1, 2^31, -(2^31), -(2^31)-1, 2^63-1, 2^63, -(2^63), 10^100); container sizes (0, 1, 255, 256, 1024); string/byte lengths (0, 1, 255, 256, 1024); empty containers

### 3.3 Special Value Testing
**Location**: `test_float_specials.py`  
**Method**: Specialized testing for float special values.  
**Coverage**: NaN (custom equivalence comparator required), Inf/-Inf, -0.0 (equal to 0.0 but different bytes), float precision boundaries (1.0000000000000001, 1.0000000000000002, 2.0 ± 2^-52), maximum/minimum representable floats

### 3.4 Recursive Container Testing
**Location**: `test_recursive.py`  
**Method**: Test handling of recursive and cyclic data structures, verify system doesn't crash and handles self-referential containers correctly.  
**Coverage**: Self-referencing list `lst = []; lst.append(lst)`, self-referencing dict `dct = {}; dct['self'] = dct`, circular references between objects `a = [1]; b = [a]; a.append(b)`, deeply nested lists (2000 levels), deeply nested tuples (500 levels), indirect tuple self-reference

### 3.5 White-Box Inspired Testing
**Location**: `test_code_objects.py`, `test_basic_types.py` (shared references)  
**Method**: Design tests based on understanding of marshal source code.  
**Coverage**: Code objects (regular functions, Lambda, dynamic functions, class methods, closures), shared references (serialization handling of same object referenced multiple times)

### 3.6 Negative Testing
**Location**: `test_basic_types.py` (UNSUPPORTED_CASES)  
**Method**: Test unsupported input types to verify correct exception throwing.  
**Coverage**: object() instances, unbound lambdas, user-defined class instances, file objects, socket objects

### 3.7 Fuzzing / Property-Based Testing
**Location**: `test_fuzzing.py`  
**Method**: Use Hypothesis library to automatically generate random test cases.  
**Coverage**: Randomly generated marshal-supported objects (500), deeply nested objects (8 levels, 300), cross-marshal version tests (200), random object collections (200), extreme depth structures (1-20 levels)

### 3.8 Cross-Process Testing
**Location**: `test_cross_process.py`  
**Method**: Test stability of serialization/deserialization across processes, verify reliability of data transfer across process boundaries.  
**Coverage**: Cross-process data transfer, inter-process marshal format compatibility

### 3.9 Hash Seed Testing
**Location**: `scripts/run_hashseed_case.py`  
**Method**: Test impact of different `PYTHONHASHSEED` values on set/dict serialization.  
**Coverage**: Integer sets (hash seed insensitive), string sets (hash seed sensitive), dicts constructed from sets, nested set structures

### 3.10 Cross-Version Testing
**Location**: `test_cross_version_enhanced.py`, `run_cross_version_tests.py`, `marshal_cross_version_test.py`  
**Method**: Run tests on multiple Python versions (3.8/3.9/3.10/3.11/3.12), compare serialization hashes across versions.  
**Coverage**: Basic type cross-version stability, float special value cross-version handling, set order cross-version differences, code object cross-version compatibility, cross-version deserialization (3.9↔3.11/3.12)

### 3.11 Cross-Platform Testing
**Location**: `compare_cross_platform.py`, `test_cross_version_enhanced.py`  
**Method**: Run tests on different operating systems (Windows/Linux/macOS), compare serialization results across platforms (run test_cross_version_enhanced.py on Windows, have team members run on macOS, compare marshal_enhanced_*.json).  
**Coverage**: Basic type hash differences (int/float/str consistent), string set hash inconsistency, code object hash inconsistency

### 3.12 Type Comparison Testing
**Location**: `test_bytearray_bytes.py`  
**Method**: Compare behavioral differences of similar types in marshal serialization, verify type information preservation during round-trip.  
**Coverage**: bytearray vs bytes (serialization format and type preservation), type identity differences (bytearray type lost after round-trip), type preservation in nested containers

### 3.13 Environment Matrix Testing
**Location**: `scripts/run_matrix.py`  
**Method**: Automatically record test environment information to ensure test traceability and reproducibility.  
**Collected Information**: Python (version/implementation/architecture/compiler), OS (name/version/platform), Marshal version, Hardware (CPU cores/architecture), Environment variables (PYTHONHASHSEED/PYTHONPATH)

### 3.14 Garbage Data Testing
**Location**: `test_bytearray_bytes.py`  
**Method**: Test exception handling of invalid input data, verify robustness of marshal.loads against garbage data.  
**Coverage**: Random byte sequences, incomplete marshal data, invalid type codes, correct handling of non-ASCII strings

### 3.15 Marshal Version Difference Detection
**Location**: `detect_differences.py`  
**Method**: Test impact of different marshal format versions (0-4) on serialization output of various types.  
**Coverage**: int, str, list, dict, set, tuple, bytes, None, bool, float (including nan/inf), complex

***

## 4. Test Results and Findings

### 4.1 Equivalence Partitioning Test Results

**Member A Test Results** (macOS 26.5.1, Python 3.9.6):

All **240 tests passed** via `test_basic_types.py`.

**Equivalence Partitioning Tests**:
- All basic types supported by marshal (None, Ellipsis, bool, int, float, complex, str, bytes, tuple, list, dict, set, frozenset) were tested with multiple representative values
- Each representative value produces byte-identical output when `marshal.dumps` is called repeatedly within the same process
- Object equivalence is preserved after round-trip serialization

**Repeatability Verification**:
- Calling `marshal.dumps(obj)` repeatedly on the same object produces byte-identical output in all cases

**Conclusion**: No instability observed in this test group.

### 4.2 Boundary Value Analysis Test Results

Via `test_boundaries.py`:

**Boundary Value Analysis Tests**:
- **Integer encoding boundaries**: `2**31-1`, `2**31`, `2**63-1`, `2**63` and their negative counterparts, `10**100`
- **Container size boundaries**: 0, 1, 255, 256, 1024 elements (lists/dicts/sets)
- **String/byte length boundaries**: 0, 1, 255, 256, 1024 characters/bytes
- **Large container testing**: 10,000 element lists and nested mixed structures

**Conclusion**: All boundary value tests passed, no instability issues detected.

### 4.3 Special Value Test Results

**Special float values handled correctly**  
NaN, Inf, -0.0 round-trip correctly. 0.0 and -0.0 produce different byte outputs.

### 4.4 Recursive Container Test Results

Through detailed testing with `test_recursive.py`, Python 3.11.7's marshal (format version 4) fully supports recursive data structures:

**Recursive Support Verification Results**:
- Self-referencing list: ✅ Successfully serialized and recovered
- Self-referencing dict: ✅ Successfully serialized and recovered
- Indirect recursion: ✅ Successfully serialized and recovered
- Mixed recursion: ✅ Successfully serialized and recovered
- Deep nesting (depth ≤ 999): ✅ Successful

**Depth Limit Measurement**:
- Maximum supported recursion depth is **999 levels** (1 less than Python's default recursion limit)
- Depth 1000 throws `ValueError: object too deeply nested to marshal`

**Determinism Verification Results**:
- 10 serialization byte stream consistency: ✅ 100% identical
- SHA-256 hash consistency: ✅ 100% identical
- Post-deserialization reference relationships: ✅ Correctly recovered

### 4.5 White-Box Inspired Test Results

**Shared references handled correctly**  
Objects referenced multiple times are serialized only once, reference relationships preserved after deserialization.

**Code Object Serialization Support**

Through detailed testing with `test_code_objects.py`, marshal correctly handles various types of code objects:

**Code Object Serialization Support**:
- Regular function code: ✅ Fully supported
- Lambda code: ✅ Consistent with regular functions
- Dynamically compiled function code: ✅ No difference
- Class method code: ✅ Consistent with regular functions
- Closure code: ✅ Free variables correctly preserved
- Complex bytecode: ✅ Control flow completely preserved
- Built-in function code: ❌ No code attribute

**Stability Test Results**:
- Regular function (5 verifications): ✅ 100% consistent
- Lambda (10 verifications): ✅ 100% consistent
- Dynamic compilation (10 verifications): ✅ 100% consistent
- Closure (5 verifications): ✅ 100% consistent
**Conclusion**:
1. marshal correctly serializes all types of Python code objects
2. Multiple serializations of the same code object produce identical byte streams (determinism holds)
3. Free variables, constant tables, bytecode, etc. are completely preserved
4. Built-in functions (C implementation) don't have code attribute, raises AttributeError when accessed

### 4.6 Negative Test Results (corresponds to 3.6)

Unsupported input types (object() instances, unbound lambdas, user-defined class instances, file objects, socket objects) correctly raise exceptions when calling `marshal.dumps`.

### 4.7 Fuzzing/Property-Based Test Results (corresponds to 3.7)

Through `test_fuzzing.py`, randomly generated marshal-supported objects (500), deeply nested objects (8 levels, 300), cross-marshal version tests (200), random object collections (200), and extreme depth structures (1-20 levels) all showed stable behavior with no crashes or exceptions.

### 4.8 Cross-Process Test Results (corresponds to 3.8)

Through `test_cross_process.py`, testing stability of serialization/deserialization across processes, verifying reliability of data transfer across process boundaries.

**Test Results**:
- Set order cross-process variation: ❌ Unstable (10 processes produce 10 different outputs)
- Float precision cross-process stability: ✅ Stable (1.0, 1.0000000000000002, 1.9999999999999998, 2.0, 1.7976931348623157e+308, 2.225073858507202e-308)

**Cross-Process Stability Summary**:
- Multiple serializations within same process: ✅ Identical (hash seed unchanged, set order unchanged)
- Different processes (different seed): ❌ Different (hash seed changes, set order changes)
- Different processes (same seed): ✅ Identical (hash seed same, set order same)

**Key Conclusion**: Set serialization order is affected by `PYTHONHASHSEED`, different processes may produce different marshal outputs, but float precision remains stable across processes.

### 4.9 Hash Seed Test Results (corresponds to 3.9)

Through `scripts/run_hashseed_case.py`, starting subprocesses with different `PYTHONHASHSEED` values (0, 1, 2, 3, 42, random) and comparing SHA-256 digests of marshal serialization results.

**Test Script Description** (`scripts/run_hashseed_case.py`):
- Uses subprocess to run tests in isolated processes, ensuring hash seed isolation
- Test expressions include: integer set `{1, 2, 3, 4, 5}`, string set `{'apple', 'banana', 'cherry', 'date'}`, frozenset `frozenset({'apple', 'banana', 'cherry', 'date'})`, fixed dict `{'apple': 1, 'banana': 2, 'cherry': 3}`, dict from set `dict.fromkeys({'apple', 'banana', 'cherry'}, 1)`, nested list of sets `[{1, 2}, {3, 4}, {5, 6}]`, tuple containing sets `({1, 2, 3}, {4, 5, 6})`
- Results output to `results/hashseed_results.json`

**Actual Results** (Windows 10, Python 3.8.6, marshal version 4):
- int_set (integer set): 1 unique digest, ✅ Stable (integer hash values are fixed, not affected by PYTHONHASHSEED)
- string_set (string set): 6 unique digests, ❌ Unstable (string hash values depend on PYTHONHASHSEED)
- string_frozenset (frozenset): 5 unique digests, ❌ Unstable (frozenset also affected by hash seed)
- fixed_dict (fixed dictionary): 1 unique digest, ✅ Stable (dictionary literal key order determined at definition)
- dict_from_set (dict constructed from set): 3 unique digests, ❌ Unstable (dict.fromkeys preserves set iteration order)
- nested_list_of_sets (nested list of sets): 1 unique digest, ✅ Stable (integer sets in lists not affected by hash seed)
- tuple_containing_set (tuple containing sets): 1 unique digest, ✅ Stable (integer sets in tuples not affected by hash seed)

**Key Conclusions**:
1. **Integer sets are not affected by hash seed**: Integer hash values are fixed, independent of PYTHONHASHSEED
2. **String sets and frozensets are affected by hash seed**: String hash values depend on PYTHONHASHSEED, different processes may produce different marshal outputs
3. **dict.fromkeys(set) is unstable**: Dicts constructed from sets preserve set iteration order, thus affected by hash seed
4. **Integer sets in nested structures are stable**: When integer sets are elements of lists or tuples, overall serialization results are stable

### 4.10 Cross-Version Test Results (corresponds to 3.10)

**Cross-Version Deserialization Compatibility**

Through `run_cross_version_tests.py` testing on Python 3.8/3.9/3.10/3.11/3.12:

**Basic Type Cross-Version Consistency**:
- Python 3.9 vs 3.8: ✅ All results byte-identical
- Python 3.10 vs 3.8: ✅ All results byte-identical
- Python 3.11 vs 3.8: ✅ All results byte-identical
- Python 3.12 vs 3.8: ✅ All results byte-identical

**Code Object Cross-Version Differences**:
- Python 3.8 Hash: `6d9166882584bd5cf4cf1afc2d4f34dd38e7ddbea1ba387f2786228b224376b`
- Python 3.12 Hash: `f770f37b1257e9a2c165d2ac7010550576d7e2b2c3846e52898db0dfc9292`

**Key Conclusions**:
- Basic types (None, bool, int, float, complex, str, bytes, list, dict, set, tuple) produce identical serialization output across all tested versions
- Code objects are **completely incompatible** across versions, bytecode format differs between versions
- Data serialized from older versions can be correctly deserialized in newer versions (backward compatible)
- Data serialized from newer versions may not be deserializable in older versions (not forward compatible)

### 4.11 Cross-Platform Test Results (corresponds to 3.11)

Through `compare_cross_platform.py` testing on Windows and macOS:

**Cross-Platform Test Summary**:
- ✅ **Basic types** (int, float, str, bytes, list, dict, tuple): Consistent (marshal design goal)
- ❌ **String sets**: Inconsistent (affected by PYTHONHASHSEED)
- ❌ **Code objects**: Inconsistent (dependent on compilation environment/platform)

**Basic Type Cross-Platform Comparison** (consistent):
- int_small: macOS 3.10 and Windows 3.8.6 hashes match ✅
- int_large: macOS 3.10 and Windows 3.8.6 hashes match ✅
- float_normal: macOS 3.10 and Windows 3.8.6 hashes match ✅
- str_short: macOS 3.10 and Windows 3.8.6 hashes match ✅

**String Set Cross-Platform Comparison** (inconsistent):
- set_strings_1: macOS 3.10 and Windows 3.8.6 hashes differ ❌
- set_strings_2: macOS 3.10 and Windows 3.8.6 hashes differ ❌
- set_strings_3: macOS 3.10 and Windows 3.8.6 hashes differ ❌

**Code Object Cross-Platform Comparison** (inconsistent):
- simple_func: macOS 3.10 and Windows 3.8.6 hashes differ ❌
- complex_func: macOS 3.10 and Windows 3.8.6 hashes differ ❌
- lambda_func: macOS 3.10 and Windows 3.8.6 hashes differ ❌

**Cross-Process Set Variation Testing**:

- macOS 3.10: 10 processes produce **10 different outputs**
- Windows 3.8.6: 10 processes produce **10 different outputs**

**Key Conclusions**:
1. Within the same operating system, same input = same output (stable)
2. However, set serialization order is affected by `PYTHONHASHSEED`
3. Different Python processes may have different `PYTHONHASHSEED`
4. Therefore, set output may differ across processes/platforms!

### 4.12 Type Comparison Test Results (corresponds to 3.12)

**bytearray type lost after round-trip (Critical BUG)**

Through detailed testing with `test_bytearray_bytes.py`, discovered that `bytearray` becomes `bytes` after marshal serialization/deserialization round-trip - type information is lost!

**Testing Method**: Compare type and behavior differences between bytearray and bytes after marshal serialization-deserialization, with boundary value testing for different sizes (0, 1, 254, 255, 256, 1000 bytes).

**Test Results**:
- `bytearray(b"hello")` round-trip: Expected to remain bytearray, actually becomes bytes ❌ BUG
- `bytes(b"hello")` round-trip: Expected to remain bytes, actually remains bytes ✅ Passed
- Empty `bytearray()` round-trip: Expected to remain bytearray, actually becomes bytes ❌ BUG
- bytearray boundary values (0-1000 bytes): Expected to remain bytearray, all become bytes ❌ BUG
- bytearray in list: Expected to remain bytearray, becomes bytes ❌ BUG
- bytearray content preservation: Expected content unchanged, content unchanged ✅ Passed

**Boundary Value Test Details**:
- Size 0: `bytearray()` → becomes `bytes()` ❌
- Size 1: `bytearray(b"\x00")` → becomes `bytes` ❌
- Size 254: `bytearray(range(254))` → becomes `bytes` ❌
- Size 255: `bytearray(range(255))` → becomes `bytes` ❌
- Size 256: `bytearray(range(256))` → becomes `bytes` ❌
- Size 1000: `bytearray(b"\x00" * 1000)` → becomes `bytes` ❌

**Conclusion**:
1. marshal doesn't distinguish between bytearray and bytes - all bytearrays become bytes after deserialization
2. Content itself is correctly preserved, only type is lost
3. Any size bytearray (including empty) cannot maintain original type
4. Even when nested in containers (like lists), bytearray becomes bytes
5. All content validations passed, indicating marshal correctly handles byte content

**bytearray and bytes have identical serialization format**

Although `bytearray` and `bytes` are different types, marshal uses the same type code:
- `bytes` uses type code 'B'
- `bytearray` also uses type code 'B' (marshal version 4)
- Both produce identical byte streams when serialized

**Root Cause**: Marshal format internally uses the same type code to store both `bytes` and `bytearray`, and uniformly returns `bytes` during deserialization.

### 4.13 Environment Matrix Test Results (corresponds to 3.13)

Through `scripts/run_matrix.py`, automatically records test environment information (Python version/implementation/architecture/compiler, OS name/version/platform, Marshal version, hardware CPU cores/architecture, environment variables PYTHONHASHSEED/PYTHONPATH), ensuring test traceability and reproducibility.

### 4.14 Garbage Data Test Results (corresponds to 3.14)

**Garbage data exception handling correct**  
Random bytes passed to `marshal.loads()` correctly throw `EOFError`, `ValueError`, or `TypeError`.

### 4.15 Marshal Version Difference Test Results (corresponds to 3.15)

**Marshal version differences (Critical)**

Through version difference testing with `detect_differences.py`, discovered different marshal format versions (0-4) produce different byte outputs for multiple types:

**Version Stability Analysis**:
- **int**: Versions 0/1/2 identical (c7e5651781c3e130), versions 3/4 identical (3c3e5f0b175ca9da)
- **str**: Versions 0/1/2 identical (ac70152db1cb0fa5), version 3 different (4cc0a14c47c512d7), version 4 different (f27068260acda9a0)
- **list**: Versions 0/1/2 identical (5859fc936213695d), versions 3/4 identical (e8d78d57d1e0438a)
- **dict**: Versions 0/1/2 identical (a555159544418909b), version 3 different (0928777e78dd85a1), version 4 different (dfac25175367deb8)
- **set**: Versions 0/1/2 identical (d69c12fee12ab7ae), versions 3/4 identical (cddf0b000e7d5e4d)
- **tuple**: Versions 0/1/2 identical (3d48d2a2ad465e7f), versions 3/4 identical (55061a55af69540b)
- **float**: Versions 0/1 identical, version 2 different, versions 3/4 identical (multiple float values show this pattern)
- **complex**: Versions 0/1 identical (a5e3d56b4e703d67), version 2 different (c1164527118f4cad), versions 3/4 identical (ffb915ef625f2701)
- **NoneType**: ✅ Stable across all versions
- **bool**: ✅ Stable across all versions

**Key Conclusion**: Marshal version is an important factor affecting serialization output. Versions 0/1/2 produce identical output, versions 3/4 produce identical output, but significant differences exist between these two groups. This means special attention must be paid to version compatibility when transferring marshal data between different Python versions.

### 4.16 Stability Issues Summary

| Issue Type | Affected Scope | Severity | Root Cause |
| ---------- | -------------- | -------- | ---------- |
| bytearray type loss | bytearray | **Critical** | Marshal format design flaw |
| Marshal version differences | All types | High | By design |
| Set order cross-process variation | String sets | Medium | PYTHONHASHSEED randomization |
| Code object version sensitivity | Code objects | High | Bytecode format version-dependent |
| Cross-platform code object differences | Code objects | Medium | Platform-specific compilation differences |

***

## 6. Limitations

### 6.1 Test Scope Limitations

1. **Limited cross-platform testing**: Currently tested on Windows, Linux, macOS, but sample size is limited
2. **Limited Python version coverage**: Tested on 3.8, 3.9, 3.10, 3.11, 3.12; more versions needed
3. **Insufficient real cross-version deserialization testing**: Need more comprehensive testing of data migration between versions

### 6.2 Test Technique Limitations

1. **Limited fuzzing depth**: Current test depth limited to 8-20 levels; deeper nesting may reveal more issues
2. **Limited shared reference testing**: Complex shared reference scenarios not sufficiently tested

### 6.3 Time and Resource Limitations

1. **Test execution time**: Fuzzing tests take longer, limiting test case quantity
2. **Environmental diversity**: Cannot test on multiple hardware architectures

***

## 7. Conclusion

### 7.1 Summary

This test suite conducted comprehensive stability testing on Python's `marshal` module, covering all 13 required test dimensions. Key findings:

1. **Critical BUG discovered**: `bytearray` becomes `bytes` after marshal round-trip, type information lost! This is a marshal format design flaw.
2. **Basic type stability**: The `marshal` module shows high stability for basic types (int, float, str, bytes, list, tuple, dict) within the same process
3. **Known instability factors**: Marshal version differences, set order affected by PYTHONHASHSEED, code object cross-version incompatibility
4. **Cross-platform differences**: Basic types consistent across platforms for same Python version, but code objects and sets may differ

### 7.2 Recommendations

1. **Production Environment Considerations**:
   - **Avoid using marshal for bytearray serialization**: Type information will be lost, use `pickle` or other serialization schemes
   - Avoid using sets containing strings if deterministic serialization across processes or versions is required
   - Code objects should not be persisted across different Python versions
   - Consider setting identical `PYTHONHASHSEED` across all processes for consistency
2. **Future Work**:
   - Expand cross-platform test sample size
   - Add more Python version testing
   - Test real cross-version deserialization scenarios
   - Increase fuzzing depth and test case quantity