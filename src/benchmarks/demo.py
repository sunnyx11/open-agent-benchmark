"""A self-contained benchmark task with a defective addition function."""

from pathlib import Path

from src.runner.git_workspace import git

TASK_ID = "demo/addition"
PROBLEM_STATEMENT = "Repair add(a, b) so that it returns the sum of its arguments."


def create_repository(directory: Path) -> str:
    """Create the demo Git repository and return its baseline commit.

    Args:
        directory: New directory under the temporary run workspace.

    Raises:
        OSError: The directory or fixture could not be written.
        RuntimeError: A Git command failed.
    """
    directory.mkdir()
    git(directory, "init", "--quiet", "--template=")
    (directory / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a - b\n", encoding="utf-8", newline="\n"
    )
    git(directory, "add", "--", "calculator.py")
    git(
        directory,
        "-c",
        "user.name=Open Agent Benchmark",
        "-c",
        "user.email=demo@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "--quiet",
        "-m",
        "Create demo baseline",
    )
    return git(directory, "rev-parse", "HEAD").decode("ascii").strip()
