# Result Submission Template for Each Member

Each member should create one text file under `results/`, for example:

- `A_basic_boundary_result.txt`
- `B_float_hashseed_result.txt`
- `C_recursive_code_result.txt`
- `D_fuzzing_matrix_result.txt`

Use this format:

```text
Member:
Responsible test group:
Operating system:
Python version:
marshal.version:

Commands:
1.
2.

Pytest result:
Example: 62 passed, 0 failed, 0 skipped

Generated files:
Example:
- results/hashseed_results.json
- results/environment_metadata.json
- results/pytest_stdout.txt

Main observations:
1.
2.
3.

Unexpected failures or warnings:
None / describe here
```

Screenshots are optional. Prefer copying terminal output into `.txt` files and
keeping generated `.json` files because they are easier to reproduce and quote
in the report.
