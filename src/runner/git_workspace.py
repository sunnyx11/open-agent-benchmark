"""Execute Git operations in temporary benchmark workspaces."""

import subprocess
from pathlib import Path


def git(workspace: Path, *args: str, input_data: bytes | None = None) -> bytes:
    """Run Git in a workspace and return stdout as raw bytes for patch fidelity.

    Args:
        workspace: Working directory for the command.
        *args: Git subcommand and arguments.
        input_data: Optional bytes to pass to Git on stdin.

    Raises:
        OSError: Git could not be started.
        RuntimeError: Git returned an error, with its stderr included.
        subprocess.TimeoutExpired: Git exceeded the 30-second timeout.
    """
    completed = subprocess.run(
        ["git", "-c", "core.autocrlf=false", *args],
        cwd=workspace,
        input=input_data,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if completed.returncode:
        details = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Git command {' '.join(args)} failed in {workspace}: {details}")
    return completed.stdout


def checkout(repository: Path, destination: Path, base_commit: str) -> None:
    """Clone a local repository into a fresh directory and check out its baseline.

    Git errors propagate to the caller.
    """
    git(repository.parent, "clone", "--quiet", "--no-local", "--template=", str(repository), str(destination))
    git(destination, "checkout", "--quiet", "--detach", base_commit)


def collect_patch(workspace: Path, base_commit: str) -> bytes:
    """Stage workspace changes and return a binary-capable patch from the baseline.

    Git errors propagate to the caller. Staging includes unignored new files.
    """
    git(workspace, "add", "--all")
    return git(workspace, "diff", "--cached", "--binary", "--no-ext-diff", base_commit, "--")
