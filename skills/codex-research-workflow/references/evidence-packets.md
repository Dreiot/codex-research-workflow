# Browser Work Evidence Packets

Create a packet whenever a result will be used by Browser Work to change a
direction, objective, method, baseline, data split, metric, stopping rule, or
claim, or to adopt formal evidence. A reversible exploratory next step may use
the Codex result summary without a packet.

Use `evidence/<experiment-id>/<candidate-id>/`, with short stable IDs such as
`dme-four-arm-p1/c001`. The fixed minimum is:

```text
manifest.json
analysis_report.md
metrics.json       # only when the task produces numerical results
```

The manifest uses `research-evidence-candidate/v1` and records:

- experiment and candidate IDs;
- candidate kind;
- exact code commit;
- source run IDs;
- configuration pointer;
- evidence file paths and SHA-256 values;
- task-specific validator command/status when applicable; and
- the exact question for Work.

`candidate_kind` is `direction_decision`, `implementation_review`, or
`formal_evidence`; this routing label does not itself promote evidence.

The report states the data boundary, run/failure status, key metrics and
statistical unit, positive/negative/mixed results, supported and unsupported
claims, local source-run reference, integrity checks, and the decision question.

Add raw outputs, tables, or figures only when Work cannot decide independently
without them. Do not upload restricted data. Do not set a size ceiling; inspect
sensitivity, licensing, single-file size, total Git increment, and duplication.
If required material is unsuitable for Git, stop for a user choice among a
necessary subset, an approved accessible store, or an explicit insufficient-
evidence outcome. Never enable Git LFS automatically.

`validate-evidence` checks schema, hashes, Git accessibility, references, and
required report sections. It cannot determine scientific sufficiency.
