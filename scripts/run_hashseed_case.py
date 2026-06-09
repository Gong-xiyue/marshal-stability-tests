"""Run cross-hash-seed marshal stability experiments.

Generates a JSON results file for the final report.
"""

import json
import marshal
import os
import platform
import subprocess
import sys

EXPRESSIONS = {
    "int_set": "{1, 2, 3, 4, 5}",
    "string_set": "{'apple', 'banana', 'cherry', 'date'}",
    "string_frozenset": "frozenset({'apple', 'banana', 'cherry', 'date'})",
    "fixed_dict": "{'apple': 1, 'banana': 2, 'cherry': 3}",
    "dict_from_set": "dict.fromkeys({'apple', 'banana', 'cherry'}, 1)",
    "nested_list_of_sets": "[{1, 2}, {3, 4}, {5, 6}]",
    "tuple_containing_set": "({1, 2, 3}, {4, 5, 6})",
}

SEEDS = ["0", "1", "2", "3", "42", "random"]


def digest_for(seed, expression):
    """Compute marshal SHA-256 digest in a child process."""
    code_start = "import hashlib\nimport marshal\nvalue = "
    code_end = "\nprint(hashlib.sha256(marshal.dumps(value)).hexdigest())"
    code = code_start + expression + code_end
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = seed
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def main():
    """Run the experiment and write JSON results."""
    results = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "marshal_version": marshal.version,
        "cases": {},
    }

    for name, expression in EXPRESSIONS.items():
        results["cases"][name] = {}
        for seed in SEEDS:
            results["cases"][name][seed] = digest_for(seed, expression)

    if not os.path.exists("results"):
        os.makedirs("results")
    with open("results/hashseed_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
