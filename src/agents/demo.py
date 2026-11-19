"""Deterministic agents for demonstrating passing and failing benchmark runs."""

from pathlib import Path


def repair_addition(workspace: Path, problem_statement: str) -> str:
    """Apply the known fixture repair in the workspace and return the agent log.

    Raises:
        OSError: The fixture could not be read or written.
        RuntimeError: The workspace did not contain the expected demo defect.
    """
    path = workspace / "calculator.py"
    source = path.read_text(encoding="utf-8")
    if "return a - b" not in source:
        raise RuntimeError(f"Expected the demo defect in {path}")
    path.write_text(source.replace("return a - b", "return a + b"), encoding="utf-8", newline="\n")
    return f"{problem_statement}\nApplied the demo repair.\n"


def leave_unchanged(_workspace: Path, problem_statement: str) -> str:
    """Acknowledge the task and return a log while leaving its workspace intact."""
    return f"{problem_statement}\nMade zero edits.\n"
