---
name: codex-research-workflow
description: Initialize, migrate, audit, execute, review, and resume governed research projects based on AGENTS.md, docs/PROJECT_CORE.md, and docs/CURRENT_STAGE.md. Use for every Browser Work-issued Codex Goal in a governed project, and for project setup, durable direction changes, decision-complete evidence, natural implementation-candidate review, formal promotion, state conflicts, or explicit handoff. Keep ordinary implementation, smoke, and exploration execution-first; invoke research-artifact-cleanup only for historical or batch cleanup.
---

# Codex Research Workflow

Treat Git and checked-in evidence as authoritative. Use:

- `AGENTS.md` for stable operating, permission, Git, review, storage, and claim rules.
- `docs/PROJECT_CORE.md` for durable research direction, innovations, components,
  direction decisions, evidence position, and claim ceiling.
- `docs/CURRENT_STAGE.md` for the current Gate, reviewed identity, material
  findings, and one next action.

Conversation summaries are entry pointers. Browser Work Project Instructions
are an independent user-supplied control surface: never shorten, replace, or
declare them redundant.

## Restore State

At a new Goal, resume, or explicit handoff, read the three authorities and the
currently controlling report, then verify the repository root, branch, HEAD,
remote tracking ref, index, worktree, and relevant protected paths. Do not load
chronological ledgers or old reports unless current authorities point to them,
state conflicts, or historical tracing requires them.

Use the read-only SessionStart Hook only as a compact pointer. A Hook failure is
fail-open; an explicit `workflow.py audit` is fail-closed for material authority
or Git conflicts.

## Execute Research

Default to the shortest credible empirical loop:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

Local, recoverable, no-cost work using authorized data may proceed without a
new Gate: implementation, tests, smoke, exploratory runs, parameter adjustment,
metrics, and diagnosis. Ask before paid, sensitive, external side-effecting,
destructive, irreversible, or final held-out actions.

Pause for a decision checkpoint when new evidence creates multiple materially
different routes or could change the core method, objective, baseline, data
split, metric, formal budget, stopping condition, or paper claim. Present facts,
uncertainty, two or three routes, costs/information gain, a recommendation, and
one clear choice. Do not continue until the user chooses.

Stop when the Goal acceptance criteria pass or the result is sufficient for the
next decision. Do not investigate adjacent issues merely for completeness.

## Manage Experiments

Use one repository experiment root, default `experiments/`; a project may
override it only in `AGENTS.md`. Create it and its subdirectories only when
needed. New persistent artifacts must not create ad hoc top-level output roots.

- Keep reusable method code in normal source directories.
- Keep experiment entrypoints/configuration under `scripts/` and `configs/` in
  the experiment root when they are needed.
- Keep persistent local runs under `runs/<experiment-id>/<run-id>/` with a
  minimal manifest; keep raw and external datasets outside the experiment root.
- Keep decision-complete Work evidence under
  `evidence/<experiment-id>/<candidate-id>/` and track it in Git.
- Keep large runs, temporary files, and cleanup plans ignored by Git.
- Delete only temporary files created by the current run when they were marked
  temporary in advance, the run succeeded, and no reference remains.

Read [experiments.md](references/experiments.md) before creating a persistent
run. Read [evidence-packets.md](references/evidence-packets.md) before preparing
material for Browser Work.

## Review Code And Evidence

Review natural candidate batches, not every edit or commit. Before new code
becomes a stable dependency for later research, push a candidate to `main` and
have Browser Work inspect the exact diff, tests, and relevant results. An
ordinary implementation-candidate review may guide repair or the next Goal
without `record-review` or a `CURRENT_STAGE.md` update.

Use formal promotion only to accept a major implementation baseline, freeze a
publication evaluation, adopt a key result, change the core method, or raise a
claim. Pin exact base/candidate SHAs, obtain one qualified independent review,
then record it once. Preserve rejected candidates and negative evidence in Git
history. Read [formal-review.md](references/formal-review.md) for this lane.

Codex chat output can guide another reversible exploratory step. Any result
used by Work to change direction, adopt a method/result, or alter a claim must
be represented by a Git-accessible, decision-complete evidence packet. Structure
and accessibility validation cannot declare scientific sufficiency; Work may
still return `BLOCKED`.

## Maintain Canonical State

Update `PROJECT_CORE.md` only after a durable strategy, innovation, component,
direction, evidence-level, or claim-boundary change. Keep one synthesized entry
per core direction, including important superseded or rejected objectives and
their evidence pointers. Do not append run-by-run narratives. Detailed results
belong in reports, evidence packets, registries, and Git.

Update `CURRENT_STAGE.md` only after a material milestone, formal review,
material blocker, or next-action change. Keep only current effective state;
historical detail belongs in reports and Git. Do not enforce byte, line, or
token budgets on either authority. Historical accumulation is a warning;
conflicting current authorities are an error.

Existing `codex-project-core` and `codex-handoff-state` markers remain the
compatible internal schema. A brand rename does not create a data migration.

## Coordinate Cleanup

Invoke `$research-artifact-cleanup` only for historical or batch cleanup, not
for normal run creation or current-run temporary cleanup. In governed projects,
always invoke it together with this Skill.

After a committed `PROJECT_CORE.md` change that replaces/retires a direction or
changes core components enough to obsolete prior experiments, generate a
read-only cleanup plan in the same Goal and stop for user review. Text-only
edits, evidence additions, and claim narrowing do not trigger cleanup.

Cleanup execution is not a formal research Gate. Use a Cleanup Plan Review,
explicit user approval, and a Cleanup Execution Verification. Read
[cleanup-integration.md](references/cleanup-integration.md) when triggered.

## Commands

Use the smallest command and read its conditional reference:

```powershell
py -3 scripts/workflow.py init --repo <repo>
py -3 scripts/workflow.py migrate --repo <repo>
py -3 scripts/workflow.py audit --repo <repo>
py -3 scripts/workflow.py prepare-experiment --repo <repo> ...
py -3 scripts/workflow.py prepare-evidence --repo <repo> ...
py -3 scripts/workflow.py validate-evidence --repo <repo> --path <candidate>
py -3 scripts/workflow.py record-review --repo <repo> --input <review.json>
py -3 scripts/workflow.py resume-prompt --repo <repo> --surface codex|work
```

Read [initialization.md](references/initialization.md) for `init` or `migrate`.
`initialize` remains a compatibility alias for the former missing-file-only
operation and is not used in new documentation.

## Browser Work Contract

Every actionable Browser Work Codex Goal starts with
`$codex-research-workflow`. A cleanup Goal also invokes
`$research-artifact-cleanup`. Keep Goals short by pointing to checked-in
authorities and reports rather than copying durable detail.

Read [work-response-contract.md](references/work-response-contract.md) before
generating or evaluating a Work response. Only the user may authorize changing
that contract.

## Explicit Handoff

Automatic context compaction is normal and is not itself a handoff. At an
explicit handoff, finish only the safely verifiable operation, re-read current
authority and Git state, distinguish pushed facts from chat-only conclusions,
run `audit`, and generate the relevant `resume-prompt`. Never create
`CODEX_HANDOFF.md`, `LATEST_STATE.md`, or another dynamic authority.
