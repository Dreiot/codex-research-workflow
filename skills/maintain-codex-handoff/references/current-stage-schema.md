# CURRENT_STAGE schema

`docs/CURRENT_STAGE.md` starts with a heading followed by this exact comment
envelope:

```md
# Current Stage

<!-- codex-handoff-state
{
  "schema_version": 1,
  "project": "example",
  "branch": "main",
  "research_phase": "exploratory_iteration",
  "current_gate": "First decision-complete empirical result",
  "last_reviewed_candidate": null,
  "accepted_code_commit": null,
  "review_verdict": "NO_REVIEW",
  "review_report": null,
  "open_findings": [],
  "next_gate": "Direction decision from measured results",
  "next_action": "Implement and run the smallest experiment that answers the current research question.",
  "updated_at": "2026-01-01T00:00:00+00:00"
}
-->
```

Required rules:

- SHA fields are full 40-character lowercase Git SHAs or `null`.
- `review_verdict` is `NO_REVIEW` when no formal promotion review applies, or
  one of `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, `BLOCKED` after such a review.
- `open_findings` is a JSON array of concise strings.
- `review_report` is a repository-relative path or `null`.
- `updated_at` is an ISO 8601 timestamp with a timezone.
- The file never records the SHA of the commit that contains itself.

Ordinary exploratory commits do not require an update to this file and do not
imply pending review. Update it only after a material milestone, formal
promotion review, material blocker, or next-action change.

Human-readable sections follow the comment. Keep them synchronized with the
JSON block. Use `scripts/handoff.py record-review` only for an explicit formal
promotion review.

## Formal Review Input

New `record-review` inputs declare `candidate_kind` as either:

- `implementation`: a formally promoted implementation baseline. `ACCEPT` or
  `ACCEPT_WITH_P2` sets `accepted_code_commit` to the candidate SHA.
- `docs_only`: a formally promoted protocol or governance baseline. Acceptance
  updates `last_reviewed_candidate` and preserves the prior accepted code.

`ACCEPT` requires no open findings. `ACCEPT_WITH_P2` requires one or more
P2-only findings. Any P0 or P1 requires `REJECT`. `BLOCKED` means required
evidence or environment is unavailable.

`REJECT` and `BLOCKED` preserve prior accepted code. A review-state commit is
not a reviewed candidate and must not be passed to `record-review`. The command
fails closed when findings, verdict, candidate kind, or accepted code conflict.

Legacy accepted inputs without `candidate_kind` remain supported when their
accepted-code semantics are unambiguous.

## Authority Boundary

- This file is the sole authority for volatile branch, milestone, formal review,
  material blocker, and next-action state.
- Durable strategy, innovations, component architecture, explored directions,
  and claim position belong in `docs/PROJECT_CORE.md`.
- Do not turn this file into a per-commit log or a second project history.
- A resumed task reads the three authorities and verifies necessary Git facts.
