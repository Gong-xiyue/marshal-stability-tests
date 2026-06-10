"""Collect environment information and run pytest for the current interpreter."""

from __future__ import annotations

import json
import marshal
import platform
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Run the local test matrix and save environment metadata."""
    result_dir = Path("results")
    result_dir.mkdir(exist_ok=True)

    metadata = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "marshal_version": marshal.version,
    }

    metadata_path = result_dir / "environment_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-ra"],
        text=True,
        capture_output=True,
        check=False,
    )

    (result_dir / "pytest_stdout.txt").write_text(
        completed.stdout,
        encoding="utf-8",
    )
    (result_dir / "pytest_stderr.txt").write_text(
        completed.stderr,
        encoding="utf-8",
    )

    print(json.dumps(metadata, indent=2))
    print(completed.stdout)
    if completed.returncode != 0:
        sys.exit(completed.returncode)


if __name__ == "__main__":
    main()
