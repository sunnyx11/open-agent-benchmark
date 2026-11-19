"""Run the demonstration benchmark from the repository root."""

import argparse
from pathlib import Path
from subprocess import TimeoutExpired

from src.scheduler.demo import AGENTS, run_demo


def main() -> int:
    """Run one benchmark task and print its verdict and artifact directory.

    Returns:
        Zero for a resolved task and one for an unresolved task. Argument and
        execution errors exit via argparse with status two.
    """
    parser = argparse.ArgumentParser(description="Run the built-in benchmark task.")
    parser.add_argument("--agent", choices=AGENTS, default="demo", help="Agent to run (default: demo).")
    parser.add_argument("--output-dir", type=Path, default=Path("runs"), help="Artifact directory (default: runs).")
    args = parser.parse_args()
    try:
        result, run_dir = run_demo(args.agent, args.output_dir)
    except (OSError, RuntimeError, TimeoutExpired) as exc:
        parser.exit(2, f"Benchmark error: {exc}\n")

    print(f"{'Resolved' if result.resolved else 'Unresolved'}  {run_dir}")
    return 0 if result.resolved else 1


if __name__ == "__main__":
    raise SystemExit(main())
