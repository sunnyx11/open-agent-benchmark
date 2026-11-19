"""Run the demo's benchmark-owned assertions against the patched checkout."""

import subprocess
import sys
from pathlib import Path

from src.runner.git_workspace import git

_CHECKS = """
import runpy
import sys

add = runpy.run_path(sys.argv[1])["add"]
cases = ((2, 3, 5), (-2, 2, 0), (4, 0, 4))
for a, b, expected in cases:
    actual = add(a, b)
    if actual != expected:
        raise SystemExit(f"add({a}, {b}): expected {expected}, got {actual}")
print(f"{len(cases)} checks passed")
"""


def evaluate(workspace: Path, patch: bytes) -> subprocess.CompletedProcess[str]:
    """Apply the patch to a clean checkout and return verification output and status.

    Args:
        workspace: Disposable checkout at the benchmark baseline.
        patch: Patch to verify and apply. Empty bytes evaluate the baseline directly.

    Raises:
        OSError: A verification command could not be started.
        RuntimeError: Git rejected the patch.
        subprocess.TimeoutExpired: A command exceeded its timeout.
    """
    if patch:
        git(workspace, "apply", "--check", "-", input_data=patch)
        git(workspace, "apply", "-", input_data=patch)
    return subprocess.run(
        [sys.executable, "-I", "-c", _CHECKS, "calculator.py"],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
    )
