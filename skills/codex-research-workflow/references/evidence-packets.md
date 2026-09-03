# Decision-Complete Evidence

Codex-reported local results may support the next reversible exploratory step.
Before changing a durable direction, objective, method, baseline, data split,
metric, stopping rule, or claim, or adopting formal evidence, make the relevant
evidence accessible and decision-complete.

Prefer existing tracked reports, configurations, results, and registry entries
when they already identify the code/configuration, evidence boundary, metrics,
positive and negative results, claim limits, and decision question. Do not copy
them into a second format merely to satisfy this reference.

Create a dedicated packet only when existing materials are insufficient or a
formal promotion needs one stable bundle. Use
`evidence/<experiment-id>/<candidate-id>/`, with short stable IDs such as
`dme-four-arm-p1/c001`. Its minimum is:

```text
manifest.json
analysis_report.md
metrics.json       # only when the task produces numerical results
```

New manifests use `research-evidence-candidate/v2` and record:

- experiment and candidate IDs;
- candidate kind;
- exact code commit;
- source run IDs;
- configuration pointer;
- evidence file paths, whose committed Git identity provides byte provenance;
- task-specific validator command/status when applicable; and
- the exact question for the controller or reviewer.

`candidate_kind` is `direction_decision`, `implementation_review`, or
`formal_evidence`; this routing label does not itself promote evidence.

The report states the data boundary, run/failure status, key metrics and
statistical unit, positive/negative/mixed results, supported and unsupported
claims, local source-run reference, integrity checks, and the decision question.

Add raw outputs, tables, or figures only when the controller cannot decide
without them. Do not upload restricted data. Do not set a size ceiling; inspect
sensitivity, licensing, single-file size, total Git increment, and duplication.
If required material is unsuitable for Git, stop for a user choice among a
necessary subset, an approved accessible store, or an explicit insufficient-
evidence outcome. Never enable Git LFS automatically.

`validate-evidence` checks schema, artifact-list completeness, Git
accessibility, references, and required report sections. It does not hash
tracked packet files. Legacy `research-evidence-candidate/v1` manifests retain
their recorded SHA-256 checks for compatibility. If an active decision truly
needs the exact bytes of a Git-external immutable file, record and validate that
identity in the task-specific protocol or validator; do not add hashes to the
packet merely for completeness. Structural validation cannot determine
scientific sufficiency.

A temporary Controller or Pro Handoff Packet is not a research evidence packet
and does not need to be committed.
