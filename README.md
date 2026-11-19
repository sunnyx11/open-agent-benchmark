# open-agent-benchmark

Open Agent Benchmark is a project for evaluating coding agents on tasks with reproducible, benchmark-defined results. The initial milestone is to run SWE-bench tasks in isolated Docker environments, evaluate the resulting patches using the official SWE-bench methodology, and record results and execution metrics.

## Run the demo

From the repository root, run the built-in addition repair task with Python 3.10+ and Git.

```bash
python -m src
python -m src --agent noop
```

The default agent applies a deterministic repair. The `noop` agent leaves the defect in place so the evaluator reports an unresolved task. The CLI prints the verdict and the saved run directory. Exit codes are `0` for resolved, `1` for unresolved, and `2` for command or runner errors.

Each completed run creates its own directory under `runs/`. Set `--output-dir` to save it elsewhere.

| Artifact | Content |
| --- | --- |
| `changes.patch` | Final Git patch relative to the baseline commit |
| `agent.log` | Task prompt and agent action |
| `evaluation.log` | Verification output from the patched checkout |
| `result.json` | Task and agent IDs, baseline commit, verdict, verification exit code, and elapsed time |

### Run in Docker

From the repository root in PowerShell, build the demo image and run it with network access disabled and CPU and memory limits. The bind mount keeps the artifacts on the host.

```powershell
docker build -t open-agent-benchmark-demo -f docker/Dockerfile .
New-Item -ItemType Directory -Force runs | Out-Null
docker run --rm --network none --cpus 1 --memory 256m --mount "type=bind,source=$($PWD.Path)/runs,target=/benchmark/runs" open-agent-benchmark-demo
```

### Run the tests

With pytest installed, run `python -m pytest -q` from the repository root.

## Repository layout

```text
.
├── docs/               # Architecture documentation
├── docker/             # Benchmark worker images
├── src/
│   ├── benchmarks/     # Dataset loaders and task definitions
│   ├── agents/         # Agent adapters
│   ├── scheduler/      # Task dispatch and run coordination
│   ├── runner/         # Container execution and artifact collection
│   ├── evaluation/     # Benchmark-specific evaluators
│   └── storage/        # Run records and artifact persistence
└── tests/
    ├── unit/           # Tests for individual modules
    └── integration/    # Tests for interactions between modules
```

See the [architecture overview](docs/architecture.md) for the planned task lifecycle and storage model.
