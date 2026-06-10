"""Run cross-hash-seed marshal stability experiments."""

import json
import marshal
import os
import platform
import subprocess
import sys

CASES = {
    "int_set": "{1, 2, 3, 4, 5}",
    "string_set": "{'apple', 'banana', 'cherry', 'date'}",
    "string_frozenset": "frozenset({'apple', 'banana', 'cherry', 'date'})",
    "fixed_dict": "{'apple': 1, 'banana': 2, 'cherry': 3}",
    "dict_from_set": "dict.fromkeys({'apple', 'banana', 'cherry'}, 1)",
    "nested_list_of_sets": "[{1, 2}, {3, 4}, {5, 6}]",
    "tuple_containing_set": "({1, 2, 3}, {4, 5, 6})",
}

SEEDS = ["0", "1", "2", "3", "42", "random"]


def digest(seed, expr):
    code = "import hashlib\nimport marshal\nvalue = " + expr + "\nprint(hashlib.sha256(marshal.dumps(value)).hexdigest())"
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = seed
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    return res.stdout.strip()


def main():
    results = {"py": sys.version, "plat": platform.platform(), "mver": marshal.version, "cases": {}}
    for name, expr in CASES.items():
        results["cases"][name] = {seed: digest(seed, expr) for seed in SEEDS}
    os.makedirs("results", exist_ok=True)
    with open("results/hashseed_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


main()
