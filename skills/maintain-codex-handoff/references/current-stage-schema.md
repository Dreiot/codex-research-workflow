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
  "research_phase": "implementation_review_loop",
  "current_gate": "G1 independent review",
  "last_reviewed_candidate": null,
  "accepted_code_commit": null,
  "review_verdict": "BLOCKED",
  "review_report": null,
  "open_findings": ["Candidate has not been independently reviewed."],
  "next_gate": "G1.1 independent review",
  "next_action": "Review the exact candidate SHA before further work.",
  "updated_at": "2026-01-01T00:00:00+00:00"
}
-->
```

Required rules:

- SHA fields are full 40-character lowercase Git SHAs or `null`.
- `review_verdict` is one of `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, `BLOCKED`.
- `open_findings` is a JSON array of concise strings.
- `review_report` is a repository-relative path or `null`.
- `updated_at` is an ISO 8601 timestamp with a timezone.
- The file never records the SHA of the commit that contains itself.

Human-readable sections follow the comment. Keep them synchronized by using
`scripts/handoff.py record-review`; hooks parse only the JSON block.

Authority boundary:

- This file is the sole authority for volatile branch/Gate/review/next-action
  state.
- Durable research direction, innovation hypotheses, component architecture,
  explored-direction decisions, and claim position belong in
  `docs/PROJECT_CORE.md`.
- Do not copy volatile state into `PROJECT_CORE.md`, and do not expand this file
  into a second project-history or strategy document.
- A resumed task reads `AGENTS.md`, `docs/PROJECT_CORE.md`, and this file, then
  verifies all Git facts directly.
