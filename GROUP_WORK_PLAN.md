# Four-Person Work Plan

## Member A: Basic types and boundary values

Responsible files:

- `tests/test_basic_types.py`
- `tests/test_boundaries.py`

Report sections:

- Equivalence partitioning
- Boundary value analysis
- Basic and boundary test results

## Member B: Floats, sets, and hash seed behavior

Responsible files:

- `tests/test_float_specials.py`
- `tests/test_collections.py`
- `tests/test_cross_process.py`
- `scripts/run_hashseed_case.py`

Report sections:

- Floating-point special values
- NaN oracle
- Hash randomization findings

## Member C: Recursive structures and code objects

Responsible files:

- `tests/test_recursive.py`
- `tests/test_code_objects.py`

Report sections:

- Recursive/cyclic data structures
- Code object compatibility
- Robustness and exception behavior

## Member D: Fuzzing, automation, and report integration

Responsible files:

- `tests/test_fuzzing.py`
- `scripts/run_matrix.py`
- `docs/final_report_draft.md`
- `docs/traceability_matrix.md`

Report sections:

- Fuzzing
- Traceability matrix
- Environment result table
- Final formatting and GitHub link

## What the group must submit

1. Public GitHub/GitLab repository link
2. Final report, maximum 8 pages
3. Source code and test suite in the repository
4. Test result evidence, preferably under `results/`
5. Clear instructions for running the test suite
