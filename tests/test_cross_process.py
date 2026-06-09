"""Cross-process tests for hash randomization effects."""

import json
import os
import subprocess
import sys


def digest_in_child(seed, expression):
    """Return marshal digest for expression in a child process."""
    code = "import hashlib\nimport marshal\n"
    code = code + "value = " + expression + "\n"
    code = code + "print(hashlib.sha256(marshal.dumps(value)).hexdigest())"
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = seed
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def test_int_set_cross_hashseed_is_measured():
    """Integer sets are generally less sensitive to hash seed."""
    digests = {}
    for seed in ["1", "2", "3"]:
        digests[seed] = digest_in_child(seed, "{1, 2, 3, 4, 5}")
    assert len(set(digests.values())) >= 1


def test_string_set_cross_hashseed_is_recorded():
    """Record whether string set digests differ across hash seeds."""
    seeds = ["0", "1", "2", "3", "42", "random"]
    digests = {}
    for seed in seeds:
        digests[seed] = digest_in_child(
            seed, "{'apple', 'banana', 'cherry', 'date'}"
        )
    unique_count = len(set(digests.values()))
    txt = "string_set across %d seeds: %d unique digest(s)"
    print(txt % (len(seeds), unique_count))
    print(json.dumps(digests, indent=2, sort_keys=True))
    for d in digests.values():
        assert d


def test_frozenset_cross_hashseed_is_measured():
    """Record whether frozenset digests differ across hash seeds."""
    seeds = ["0", "1", "2", "3", "42", "random"]
    digests = {}
    for seed in seeds:
        digests[seed] = digest_in_child(
            seed, "frozenset({'apple', 'banana', 'cherry', 'date'})"
        )
    unique_count = len(set(digests.values()))
    txt = "frozenset across %d seeds: %d unique digest(s)"
    print(txt % (len(seeds), unique_count))
    print(json.dumps(digests, indent=2, sort_keys=True))
    for d in digests.values():
        assert d


def test_dict_from_set_cross_hashseed_is_measured():
    """BUG: dict.fromkeys(set) produces different bytes under different hash seeds."""
    seeds = ["0", "1", "2", "3", "42", "random"]
    digests = {}
    for seed in seeds:
        expr = "dict.fromkeys({'apple', 'banana', 'cherry', 'date'}, 1)"
        digests[seed] = digest_in_child(seed, expr)
    unique_count = len(set(digests.values()))
    txt = "dict_from_set across %d seeds: %d unique digest(s)"
    print(txt % (len(seeds), unique_count))
    print(json.dumps(digests, indent=2, sort_keys=True))
    # All seeds should produce the same result for stability
    assert unique_count == 1
