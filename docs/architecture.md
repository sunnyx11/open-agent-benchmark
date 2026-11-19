# Architecture

## Demo implementation

The CLI runs one built-in task with either a deterministic repair agent or a no-op agent. The runner creates a temporary Git repository to record the baseline and clones it into separate agent and evaluation workspaces. The evaluator applies the agent's patch in its clean workspace and executes assertions owned by the benchmark. The local storage module saves each completed run independently.

The [demo commands](../README.md#run-the-demo) use a trusted fixture bundled with the project. The Docker image runs one complete demo per container. The planned SWE-bench integration uses benchmark-specific images and official evaluation.

## Planned task lifecycle

1. The benchmark loader reads a task with its repository, base commit, and problem statement. The scheduler dispatches the task to a worker.
2. The worker starts a dedicated Docker container from a benchmark image with the repository and its dependencies. An agent adapter passes the task to the agent and provides controlled access to the workspace and commands.
3. The worker collects the final Git patch relative to the base commit, along with execution logs, elapsed time, and available token usage. It removes the task container after collecting artifacts.
4. The evaluator checks that the patch applies to a clean checkout and runs the benchmark's official verification. For SWE-bench, the official evaluation determines whether the task is resolved. The evaluator records output, exit codes, and failure details.
5. The storage layer records the outcome and metrics in PostgreSQL and stores patches, logs, and test reports in object storage. A planned dashboard reads these results.

The execution environment sets CPU, memory, time, and network limits per task. The isolation design combines Docker with additional security controls for untrusted code.

## Planned storage model

| Entity | Planned data |
| --- | --- |
| `benchmarks` | Benchmark name, version, description, and dataset source |
| `benchmark_tasks` | Benchmark, external task ID, repository, base commit, and task definition |
| `agents` | Agent name, provider, model, version, and configuration |
| `benchmark_runs` | Benchmark, agent, run status, start and completion times, and configuration |
| `task_runs` | Benchmark run, task, execution status, evaluation outcome, duration, token counts, and estimated cost |
| `task_artifacts` | Task run, artifact type, object storage URI, checksum, and metadata |

## Benchmark and agent support

Agent adapters handle provider-specific interactions. Benchmark loaders and evaluators handle dataset formats and official scoring. Terminal-Bench, WebArena, and BFCL are candidates for expansion after the SWE-bench pipeline is validated.
