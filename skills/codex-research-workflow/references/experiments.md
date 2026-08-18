# Experiment Layout and Run Manifest

Resolve the single experiment root inside the exact project/Git root from `AGENTS.md`; otherwise use
`experiments/`. Do not pre-create unused directories.

```text
experiments/
├── scripts/       # tracked experiment entrypoints and analysis scripts
├── configs/       # tracked experiment configurations
├── registry/      # tracked important decision-chain entries
├── evidence/      # tracked decision evidence when a dedicated packet is needed
├── runs/          # ignored persistent local results
├── .tmp/          # ignored current-run temporary files
└── quarantine/    # ignored, only when the user requests it
```

Core method code remains in normal source directories. Raw and external data
remain in the project's data locations, outside this root.

Only create a persistent run when results must survive for comparison,
diagnosis, reproduction, continuation, or evidence. Preserve the following
minimal provenance in the project's existing equivalent metadata when one is
already authoritative; otherwise use
`runs/<experiment-id>/<run-id>/manifest.json` with:

```json
{
  "schema": "research-experiment-run/v1",
  "experiment_id": "dme-four-arm-p1",
  "run_id": "r001",
  "created_at": "2026-01-01T00:00:00+00:00",
  "entrypoint": "experiments/scripts/run_dme.py",
  "config": "experiments/configs/dme-four-arm-p1.yaml",
  "data_ids": ["dataset-a"],
  "git_head": "<40-character SHA>",
  "worktree_dirty": false,
  "diff_hash": null,
  "status": "running"
}
```

Allowed statuses are `running`, `completed`, `failed`, and `interrupted`.
Exploratory runs may start from a dirty worktree, but record a deterministic
diff hash. Formal runs use a clean frozen commit. A run later used for a durable
controller decision must be reproducible from a commit or a bound source
snapshot.

The tracked registry includes only experiments that enter controller decisions,
formal evidence, or important negative evidence. It is not a run-by-run log.
Directory IDs are short, stable ASCII identifiers; do not rename paths merely
because a direction changes status.
