"""Coordinate one complete run of the local benchmark task."""

from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from src.agents.demo import leave_unchanged, repair_addition
from src.benchmarks.demo import PROBLEM_STATEMENT, TASK_ID, create_repository
from src.evaluation.demo import evaluate
from src.runner.git_workspace import checkout, collect_patch
from src.storage.local import RunResult, save_run

AGENTS = {"demo": repair_addition, "noop": leave_unchanged}


def run_demo(agent_name: str, output_dir: Path) -> tuple[RunResult, Path]:
    """Run the selected demo agent and persist the outcome and its artifacts.

    Args:
        agent_name: Key in the demo agent registry.
        output_dir: Parent directory for completed run artifacts.

    Returns:
        Evaluation result and the directory containing its saved artifacts.

    Raises:
        KeyError: The agent name is unknown.
        OSError: A workspace or output failed to open or write.
        RuntimeError: A runner command failed.
        subprocess.TimeoutExpired: A runner command timed out.
    """
    agent = AGENTS[agent_name]
    started = perf_counter()
    with TemporaryDirectory(prefix="open-agent-benchmark-") as temporary:
        workspace = Path(temporary)
        baseline = workspace / "baseline"
        base_commit = create_repository(baseline)

        agent_workspace = workspace / "agent"
        checkout(baseline, agent_workspace, base_commit)
        agent_log = agent(agent_workspace, PROBLEM_STATEMENT)
        patch = collect_patch(agent_workspace, base_commit)

        evaluation_workspace = workspace / "evaluation"
        checkout(baseline, evaluation_workspace, base_commit)
        verification = evaluate(evaluation_workspace, patch)

    result = RunResult(
        task_id=TASK_ID,
        agent=agent_name,
        base_commit=base_commit,
        resolved=verification.returncode == 0,
        test_exit_code=verification.returncode,
        elapsed_seconds=perf_counter() - started,
    )
    return result, save_run(output_dir, result, patch, agent_log, verification.stdout)
