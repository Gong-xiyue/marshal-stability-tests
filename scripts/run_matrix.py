"""Collect environment information and run pytest for the current interpreter."""

from __future__ import annotations

import argparse
import json
import marshal
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def get_environment_metadata() -> dict[str, Any]:
    """Collect comprehensive environment metadata."""
    metadata = {
        "run_id": f"run_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel,
                "serial": sys.version_info.serial,
            },
            "implementation": platform.python_implementation(),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
        },
        "marshal": {
            "version": marshal.version,
        },
        "environment": {
            "pythonpath": os.environ.get("PYTHONPATH", ""),
            "pythonhashseed": os.environ.get("PYTHONHASHSEED", "random"),
        },
        "hardware": {
            "cpu_count": os.cpu_count(),
        },
    }
    return metadata


def parse_pytest_output(stdout: str) -> dict[str, Any]:
    """Parse pytest output to extract test statistics."""
    stats = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "error": 0,
        "total": 0,
        "duration": 0.0,
    }

    for line in stdout.split("\n"):
        if "passed" in line and "test" in line.lower():
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "passed":
                    try:
                        stats["passed"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
                elif part == "failed":
                    try:
                        stats["failed"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
                elif part == "skipped":
                    try:
                        stats["skipped"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
                elif part == "xfailed":
                    try:
                        stats["xfailed"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
                elif part == "xpassed":
                    try:
                        stats["xpassed"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
                elif part == "error":
                    try:
                        stats["error"] = int(parts[i - 1])
                    except (IndexError, ValueError):
                        pass
        if line.startswith("=") and "in" in line and "seconds" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == "in":
                    try:
                        stats["duration"] = float(parts[i + 1])
                    except (IndexError, ValueError):
                        pass

    stats["total"] = (
        stats["passed"] + stats["failed"] + stats["skipped"] + stats["xfailed"] + stats["xpassed"] + stats["error"]
    )
    return stats


def main() -> None:
    """Run the local test matrix and save environment metadata."""
    parser = argparse.ArgumentParser(description="Run marshal stability tests with environment matrix")
    parser.add_argument(
        "--result-dir",
        default="results",
        help="Directory to store results (default: results)",
    )
    parser.add_argument(
        "--test-path",
        default=None,
        help="Specific test path or pattern to run",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output",
    )
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    result_dir.mkdir(parents=True, exist_ok=True)

    metadata = get_environment_metadata()
    run_id = metadata["run_id"]

    metadata_path = result_dir / f"environment_metadata_{run_id}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    pytest_args = [sys.executable, "-m", "pytest", "-ra", "--tb=short"]
    if args.test_path:
        pytest_args.append(args.test_path)

    start_time = time.time()
    completed = subprocess.run(
        pytest_args,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    duration = time.time() - start_time

    stdout_path = result_dir / f"pytest_stdout_{run_id}.txt"
    stderr_path = result_dir / f"pytest_stderr_{run_id}.txt"

    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")

    test_stats = parse_pytest_output(completed.stdout)
    test_stats["duration_measured"] = duration
    test_stats["return_code"] = completed.returncode
    test_stats["run_id"] = run_id

    stats_path = result_dir / f"test_stats_{run_id}.json"
    stats_path.write_text(json.dumps(test_stats, indent=2), encoding="utf-8")

    summary = {
        "metadata": metadata,
        "test_stats": test_stats,
        "stdout": completed.stdout[-2000:] if len(completed.stdout) > 2000 else completed.stdout,
    }

    summary_path = result_dir / f"summary_{run_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.verbose:
        print("\n=== Environment Metadata ===")
        print(json.dumps(metadata, indent=2))

    print("\n=== Test Results Summary ===")
    print(f"Run ID: {run_id}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total tests: {test_stats['total']}")
    print(f"Passed: {test_stats['passed']}")
    print(f"Failed: {test_stats['failed']}")
    print(f"Skipped: {test_stats['skipped']}")
    print(f"Return code: {completed.returncode}")

    if completed.returncode != 0:
        print("\n=== pytest STDERR ===")
        print(completed.stderr)
        sys.exit(completed.returncode)


if __name__ == "__main__":
    main()
