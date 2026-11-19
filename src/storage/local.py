"""Persist demo run metadata and artifacts in the local filesystem."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class RunResult:
    """Record the task, agent, verdict, verification exit code, and wall time."""

    task_id: str
    agent: str
    base_commit: str
    resolved: bool
    test_exit_code: int
    elapsed_seconds: float


def save_run(output_dir: Path, result: RunResult, patch: bytes, agent_log: str, evaluation_log: str) -> Path:
    """Write the result and artifacts, then publish the complete run by directory rename.

    Returns:
        Path of the new run directory. Each run uses a unique name.

    Raises:
        OSError: The output directory or artifacts could not be written.
    """
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Could not create output directory {output_dir}: {exc.strerror}") from exc
    run_dir = output_dir / f"run-{uuid4().hex}"
    with TemporaryDirectory(prefix=".staging-", dir=output_dir) as temporary:
        staging = Path(temporary)
        (staging / "changes.patch").write_bytes(patch)
        (staging / "agent.log").write_text(agent_log, encoding="utf-8")
        (staging / "evaluation.log").write_text(evaluation_log, encoding="utf-8")
        (staging / "result.json").write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
        staging.rename(run_dir)
    return run_dir
