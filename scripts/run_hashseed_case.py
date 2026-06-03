"""Run cross-hash-seed marshal stability experiments.

This script is intentionally separate from pytest so that it can generate a
results JSON file for the final report.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import textwrap
from pathlib import Path


EXPRESSIONS = {
    "int_set": "{1, 2, 3, 4, 5}",
    "string_set": "{'apple', 'banana', 'cherry', 'date'}",
    "string_frozenset": "frozenset({'apple', 'banana', 'cherry', 'date'})",
    "fixed_dict": "{'apple': 1, 'banana': 2, 'cherry': 3}",
    "dict_from_set": "dict.fromkeys({'apple', 'banana', 'cherry'}, 1)",
}

SEEDS = ["0", "1", "2", "3", "42", "random"]


def digest_for(seed: str, expression: str) -> str:
    """Compute marshal SHA-256 digest in a child process."""
    code = textwrap.dedent(
        f"""
        import hashlib
        import marshal

        value = {expression}
        print(hashlib.sha256(marshal.dumps(value)).hexdigest())
        """,
    )
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = seed
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def main() -> None:
    """Run the experiment and write JSON results."""
    results = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "marshal_version": __import__("marshal").version,
        "cases": {},
    }

    for name, expression in EXPRESSIONS.items():
        results["cases"][name] = {
            seed: digest_for(seed, expression)
            for seed in SEEDS
        }

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "hashseed_results.json"
    output_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
