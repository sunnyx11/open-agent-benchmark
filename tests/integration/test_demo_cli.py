"""Exercise the demo CLI with real Git workspaces and a local output directory."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run_cli(output_dir: Path, agent: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "src", "--output-dir", str(output_dir), "--agent", agent],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


@pytest.mark.parametrize(("agent", "exit_code", "resolved"), [("demo", 0, True), ("noop", 1, False)])
def test_cli_persists_evaluation_outcome(tmp_path: Path, agent: str, exit_code: int, resolved: bool) -> None:
    output_dir = tmp_path / "benchmark runs"
    completed = _run_cli(output_dir, agent)

    assert completed.returncode == exit_code, completed.stderr
    (run_dir,) = output_dir.iterdir()
    assert str(run_dir) in completed.stdout
    assert {path.name for path in run_dir.iterdir()} == {"changes.patch", "agent.log", "evaluation.log", "result.json"}

    record: dict[str, str | bool | int | float] = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
    assert record["task_id"] == "demo/addition"
    assert record["agent"] == agent
    assert record["resolved"] is resolved
    assert record["test_exit_code"] == exit_code
    agent_log = (run_dir / "agent.log").read_text(encoding="utf-8")
    assert "Repair add(a, b)" in agent_log

    patch = (run_dir / "changes.patch").read_bytes()
    evaluation_log = (run_dir / "evaluation.log").read_text(encoding="utf-8")
    if resolved:
        assert b"-    return a - b" in patch
        assert b"+    return a + b" in patch
        assert "3 checks passed" in evaluation_log
    else:
        assert patch == b""
        assert "expected 5, got -1" in evaluation_log


def test_cli_preserves_previous_runs(tmp_path: Path) -> None:
    first = _run_cli(tmp_path, "demo")
    assert first.returncode == 0, first.stderr
    (previous,) = tmp_path.iterdir()
    previous_record = (previous / "result.json").read_bytes()

    second = _run_cli(tmp_path, "noop")
    assert second.returncode == 1, second.stderr
    assert len(list(tmp_path.iterdir())) == 2
    assert (previous / "result.json").read_bytes() == previous_record


def test_cli_reports_storage_errors(tmp_path: Path) -> None:
    blocked_output = tmp_path / "existing-file"
    blocked_output.write_text("keep", encoding="utf-8")

    completed = _run_cli(blocked_output, "demo")

    assert completed.returncode == 2
    assert "Benchmark error" in completed.stderr
    assert str(blocked_output) in completed.stderr
    assert blocked_output.read_text(encoding="utf-8") == "keep"
