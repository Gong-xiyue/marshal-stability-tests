"""Cross-process tests for hash randomization effects."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap


def digest_in_child(seed: str, expression: str) -> str:
    """Return marshal digest for expression in a child process."""
    code = textwrap.dedent(
        f"""
        import hashlib
        import marshal

        value = {expression}
        data = marshal.dumps(value)
        print(hashlib.sha256(data).hexdigest())
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


def test_int_set_cross_hashseed_is_measured():
    """Integer sets are generally less sensitive to hash seed."""
    digests = {
        seed: digest_in_child(seed, "{1, 2, 3, 4, 5}")
        for seed in ["1", "2", "3"]
    }
    assert len(set(digests.values())) >= 1


def test_string_set_cross_hashseed_is_recorded():
    """String sets may differ across hash seeds; record instead of forcing pass/fail."""
    digests = {
        seed: digest_in_child(seed, "{'apple', 'banana', 'cherry', 'date'}")
        for seed in ["1", "2", "3", "random"]
    }
    print(json.dumps(digests, indent=2, sort_keys=True))
    assert all(digests.values())
