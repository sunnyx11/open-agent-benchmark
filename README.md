# open-agent-benchmark
Absolutely. Here is the proposed technical architecture. To clarify, this is the planned design; implementation has not started yet.

### 1. Isolated Agent Execution with Docker

Each benchmark task will run inside an independent Docker container.

- A task scheduler assigns benchmark instances to isolated workers.
- Each container starts from a predefined benchmark image containing the required repository, dependencies, and test environment.
- The agent receives the task description and controlled access to the repository through a standardized adapter.
- The agent can inspect files, execute commands, modify code, and run tests within the container.
- Containers will have configurable CPU, memory, execution-time, and network restrictions.
- After execution, the system collects the final Git diff, execution logs, test results, token usage, and timing information.
- Containers are destroyed after artifacts are collected, preventing state leakage between tasks.

Docker isolation will be supplemented with appropriate security restrictions, since containers alone are not a complete security boundary for untrusted code.

### 2. Diff Collection and Automated Evaluation

The agent's final changes will be captured using Git.

The evaluation pipeline will:

1. Extract the final patch using `git diff`.
2. Verify that the patch applies cleanly to the original repository state.
3. Apply the patch to a clean evaluation environment.
4. Run the benchmark's official test and verification scripts.
5. Record whether the issue is successfully resolved.
6. Store test output, exit codes, failure details, and execution metrics.

For SWE-bench, I will follow its official evaluation methodology rather than relying on LLM-based subjective scoring. Other benchmarks will use their respective official scoring mechanisms.

### 3. Database Schema

I plan to use PostgreSQL with the following core entities:

**benchmarks**
- id, name, version, description, dataset_source

**benchmark_tasks**
- id, benchmark_id, task_external_id, repository, base_commit, task_definition

**agents**
- id, name, provider, model, version, configuration

**benchmark_runs**
- id, benchmark_id, agent_id, status, started_at, completed_at, configuration

**task_runs**
- id, run_id, task_id, status, success, execution_time, input_tokens, output_tokens, estimated_cost

**task_artifacts**
- id, task_run_id, artifact_type, storage_uri, checksum, metadata

Artifacts will include Git patches, execution logs, test reports, and other debugging information. Large artifacts will be stored in object storage rather than directly in PostgreSQL.

### 4. Overall Architecture

The main workflow will be:

Benchmark Dataset → Task Scheduler → Docker Worker → Agent Adapter → Git Diff Collection → Official Evaluator → PostgreSQL / Object Storage → Results Dashboard

The architecture will be modular so that new benchmarks and agent providers can be added without redesigning the entire platform.

My initial milestone is to implement the SWE-bench pipeline end to end, validate reproducible task execution, and then progressively introduce additional benchmarks such as Terminal-Bench, WebArena, and BFCL.

This is the concrete engineering plan I intend to build with Devin's assistance.
