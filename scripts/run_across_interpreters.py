"""Cross-interpreter marshal stability experiment.

Finds Python interpreters and compares marshal results across them.
"""

import json
import os
import subprocess
import sys

EXPRESSIONS = {
    "none": "None",
    "true": "True",
    "false": "False",
    "int_small": "42",
    "int_large": "2**63",
    "float_pi": "3.141592653589793",
    "float_nan": "float('nan')",
    "float_inf": "float('inf')",
    "str_ascii": "'hello marshal'",
    "str_unicode": "'\u4e2d\u6587\u6d4b\u8bd5'",
    "bytes_data": "b'\\x00\\x01\\x02\\xff'",
    "tuple": "(1, 'two', 3.0)",
    "list": "[1, 'two', 3.0]",
    "dict": "{'a': 1, 'b': 2}",
    "set": "{1, 2, 3}",
    "frozenset": "frozenset({1, 2, 3})",
}


def find_interpreters():
    """Find Python interpreters on this machine."""
    interpreters = [sys.executable]

    # Common install locations
    for path in [
        r"C:\Python310\python.exe",
        r"C:\Python311\python.exe",
        r"C:\Python312\python.exe",
        r"C:\Python313\python.exe",
    ]:
        if path not in interpreters and os.path.isfile(path):
            interpreters.append(path)

    # Check which ones work
    result = []
    for exe in interpreters:
        try:
            code = "import sys; print(sys.version)"
            r = subprocess.run(
                [exe, "-c", code], capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0:
                result.append(exe)
        except Exception:
            pass

    return result


def digest_for(exe, expression):
    """Run expression through marshal in a subprocess."""
    code_start = "import hashlib\nimport marshal\nimport sys\n\nvalue = "
    code_end = "\ndata = marshal.dumps(value)\nprint(hashlib.sha256(data).hexdigest())"
    code = code_start + expression + code_end

    try:
        result = subprocess.run(
            [exe, "-c", code], capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return {"digest": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


def main():
    """Discover interpreters, run experiment, write results."""
    interpreters = find_interpreters()
    print("Found interpreters:", interpreters)

    results = {}
    for name, expr in EXPRESSIONS.items():
        case_data = {}
        for exe in interpreters:
            case_data[exe] = digest_for(exe, expr)
        results[name] = case_data

    # Count unique digests
    for name, case_data in results.items():
        digests = []
        for exe in interpreters:
            if "digest" in case_data.get(exe, {}):
                digests.append(case_data[exe]["digest"])
        unique = len(set(digests))
        if unique > 1:
            print("WARNING: " + name + " has " + str(unique) + " different digests!")
        else:
            print(name + ": consistent (" + str(unique) + " unique)")

    # Write results
    if not os.path.exists("results"):
        os.makedirs("results")
    with open("results/across_interpreters_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Done. Results saved to results/across_interpreters_results.json")


if __name__ == "__main__":
    main()
