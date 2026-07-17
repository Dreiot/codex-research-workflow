# PROJECT_CORE schema

`docs/PROJECT_CORE.md` starts with a heading followed by this exact comment
envelope:

```md
# Project Core

<!-- codex-project-core
{
  "schema_version": 1,
  "project": "example",
  "research_question": "What scientific question does this project answer?",
  "target_outcome": "The intended paper contribution and evaluation outcome.",
  "primary_direction": "The durable primary methodological direction.",
  "primary_innovations": ["Proposed: concise innovation hypothesis."],
  "core_components": ["component_id: concise scientific role."],
  "evidence_level": "hypothesis_only",
  "strategic_status": "active",
  "last_strategic_review": null,
  "updated_at": "2026-01-01T00:00:00+00:00"
}
-->
```

Required rules:

- The JSON object contains exactly the documented fields.
- String fields are concise, non-empty summaries; innovation and component
  fields are non-empty arrays of concise strings.
- `strategic_status` is one of `unaudited`, `active`, `paused`, `redirected`, or
  `completed`.
- `last_strategic_review` is a repository-relative report path or `null`.
- `updated_at` is a timezone-aware ISO 8601 timestamp.
- The JSON and human sections describe durable strategy. They never record the
  current branch, HEAD, Gate, review verdict, or next action.

The following human-readable sections are required after the JSON block:

1. `## Research Objective`: research question, target outcome, evaluation
   object, and intended scope.
2. `## Core Direction`: primary methodological direction and why it is central.
3. `## Innovation Hypotheses`: hypothesis, novelty relative to baselines,
   expected mechanism, maturity, and evidence link. Distinguish proposed from
   supported contributions.
4. `## Component Map`: component identifier, mathematical/scientific role,
   implementation location, interfaces/dependencies, maturity, and evidence.
5. `## Explored Directions`: active, supported, rejected, deferred, and
   superseded directions with decision reason, reusable residue, and evidence.
6. `## Evidence and Claim Position`: evidence ladder, validated facts, current
   claim ceiling, and missing evidence.
7. `## Scientific Boundaries`: data, provenance, mathematical, experimental,
   compute, and publication constraints.
8. `## Open Strategic Questions`: unresolved strategic questions and explicit
   decision criteria.
9. `## Strategic Roadmap`: dependency order and long-horizon milestones, not the
   current Gate.
10. `## Canonical Sources`: indexes to specifications, implementation entry
    points, protocols, reports, experiment registries, and paper sections.
11. `## Update Rules`: ownership, triggers, history-preservation rule, and the
    prohibition on volatile state.

Update policy:

- Browser ChatGPT Work normally synthesizes strategic updates from checked-in
  evidence; Codex may prepare the docs-only change when explicitly instructed.
- Preserve rejected and superseded directions. Never erase negative results.
- Link to detailed reports rather than copying large evidence blocks.
- If strategy changes the active Gate or next action, update
  `docs/CURRENT_STAGE.md` in the same governance change.
- A migration placeholder uses `strategic_status: unaudited` and is not evidence
  that the project strategy has been reviewed.
