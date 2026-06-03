# Stability and Correctness Testing of Python's `marshal` Module

This repository contains a test suite for investigating the stability and correctness
of Python's internal `marshal` serialization module.

The main research question is:

> Does the same input always produce the same hash-identical marshal byte stream?

The project tests repeated serialization, round-trip correctness, floating-point
special values, recursive objects, hash randomization, boundary cases, fuzzing,
and cross-environment behavior.

## Repository structure

```text
marshal-stability-tests/
├── src/marshal_stability/
│   ├── __init__.py
│   ├── comparators.py
│   ├── generators.py
│   ├── hash_utils.py
│   └── cases.py
├── tests/
│   ├── test_basic_types.py
│   ├── test_boundaries.py
│   ├── test_float_specials.py
│   ├── test_collections.py
│   ├── test_recursive.py
│   ├── test_code_objects.py
│   ├── test_fuzzing.py
│   └── test_cross_process.py
├── scripts/
│   ├── run_matrix.py
│   └── run_hashseed_case.py
├── docs/
│   ├── final_report_draft.md
│   └── traceability_matrix.md
└── results/
```

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Git Bash / Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run tests

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src --cov=tests
```

Run style check:

```bash
ruff check .
```

## Cross-process hash seed experiment

```bash
python scripts/run_hashseed_case.py
```

This script starts child Python processes with different `PYTHONHASHSEED` values
and compares the SHA-256 digest of `marshal.dumps(obj)`.

## Cross-version / cross-platform experiment

Run the test suite on each target environment, for example:

- Windows + Python 3.11
- Linux + Python 3.11
- macOS + Python 3.11
- Python 3.8 / 3.9 / 3.10 / 3.11 / 3.12 / 3.13 / 3.14 if available

Then store the output files under `results/`.

## Notes

The official Python documentation says that `marshal` is not a general
persistence module. It exists mainly for `.pyc` files, and the format may change
between Python versions. Therefore, cross-version byte differences should be
classified as documented limitations rather than necessarily as bugs.
