---
name: maintain-codex-handoff
description: Create, audit, update, and resume canonical research-project handoffs based on AGENTS.md, docs/PROJECT_CORE.md, and docs/CURRENT_STAGE.md. Use at explicit handoffs, formal evidence or promotion reviews, durable strategy changes, state conflicts, or when stale CODEX_HANDOFF.md or LATEST_STATE.md files exist. Do not turn ordinary implementation, debugging, real-data smoke, or exploratory experiments into review gates.
---

# Maintain Codex Handoff

Use three repository authorities:

- `AGENTS.md`: stable operating, permission, validation, Git, and claim rules.
- `docs/PROJECT_CORE.md`: durable research direction, innovations, components,
  explored directions, evidence position, and scientific boundaries.
- `docs/CURRENT_STAGE.md`: current branch, milestone, formal review state,
  material blockers, and next action.

Git and checked-in evidence are authoritative. Conversation summaries are only
entry pointers.

## Commands

Use the smallest applicable command:

```powershell
py -3 scripts/handoff.py audit --repo <repo>
py -3 scripts/handoff.py initialize --repo <repo>
py -3 scripts/handoff.py record-review --repo <repo> --input <review.json>
py -3 scripts/handoff.py resume-prompt --repo <repo> --surface codex
py -3 scripts/handoff.py resume-prompt --repo <repo> --surface work
```

- `audit` validates canonical files, Git identity, report pointers, and legacy
  handoff files. It never writes.
- `initialize` creates missing authorities without overwriting existing files.
- `record-review` records an explicitly requested formal promotion review. It
  does not decide whether a candidate deserves promotion.
- `resume-prompt` produces a compact entry prompt that reloads repository truth.

Read the schema references before manually editing `PROJECT_CORE.md` or
`CURRENT_STAGE.md`. Read
[work-response-contract.md](references/work-response-contract.md) before
generating or evaluating a Browser Work response. Do not modify that contract
without explicit user authorization.

## Research Priority

Optimize for the shortest credible path to publishable experimental evidence:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

Default to execution, not governance. When current repository and user
boundaries permit it, Codex may continuously implement, test, run local
recoverable real-data smoke or exploratory experiments, diagnose results, and
adjust the method without creating design-only Gates, independent reviews, or
review-state commits between iterations.

Use the simplest correct and testable implementation. Prefer existing
components, small diffs, early end-to-end runs, and measurable results. Do not
expand into speculative abstractions, broad refactors, exhaustive
generalization, defensive infrastructure, cryptographic evidence chains, or
adjacent improvements unless they directly block the current research
decision.

Stop when the Goal's acceptance criteria pass or the produced metrics are
sufficient to decide the next direction. Record unrelated issues without
investigating or fixing them.

Never trade away data integrity, statistical validity, fair comparison,
reproducibility, material failure handling, or honest claim boundaries.

## Permission Boundary

Local, recoverable, no-cost work using project-authorized data is allowed by
default, including real-data smoke and exploratory experiments. Do not ask for
per-run permission when repository authorities already permit that class of
work.

Ask before:

- paid services or material resource charges;
- sensitive-data exposure or credential use not already authorized;
- external live services or hardware with side effects;
- destructive or irreversible actions.

For a formal publication evaluation, require a frozen data boundary,
configuration, metrics, statistical unit, comparators, stopping conditions,
and provenance. If those are already authorized and frozen, do not request
duplicate execution permission.

## Two Execution Lanes

### Exploratory iteration

This is the default. It includes ordinary implementation, tests, debugging,
data processing, local smoke, exploratory experiments, parameter adjustment,
and metric generation.

- Keep naturally coupled implementation, critical tests, and bounded runs
  together.
- Multiple commits and iterations are allowed.
- No independent review or review-state commit is required.
- Do not update `CURRENT_STAGE.md` for every commit or local result.
- Non-blocking findings are ordinary backlog items and do not block execution.

### Formal promotion

Use this lane only when the user, Goal, or `CURRENT_STAGE.md` explicitly intends
to:

- accept a major implementation as the formal project baseline;
- freeze a publication evaluation;
- adopt a key result or statistical conclusion;
- change the core method; or
- raise the paper claim boundary.

Create one natural candidate, pin its base and candidate SHAs, and obtain
exactly one qualified independent review. Browser Work is preferred when it
has inspected the actual GitHub diff and evidence. Use `research-reviewer` only
when no qualifying Work review exists, evidence conflicts, or the user asks
for a second opinion.

Record a completed formal promotion review once:

1. write the detailed report;
2. run `record-review`;
3. run `audit`;
4. create and push one governance-docs-only review-state commit.

Mechanical verification of that commit creates no new review or commit. If
verification passes, Browser Work may issue the next Goal in the same response.
A rejected or blocked formal promotion remains recorded before remediation so
the decision and candidate identity are not lost.

## Evidence And Claims

Exploratory smoke is diagnostic evidence, not automatic paper evidence. After
using exploratory results to adjust a method, evaluate the formal claim on an
independent held-out set or a newly frozen evaluation procedure. Do not tune
repeatedly on the final test set.

Formal evidence should preserve predefined metrics, all valid runs, failures,
variation, uncertainty, resource cost, and material negative results. It may
emphasize supported strengths, but it must not hide evidence that would change
the conclusion.

Engineering hashes, schemas, counters, manifests, and logs support
reproducibility only when materially needed. They are not scientific evidence
by themselves and must not become an unrelated research Gate.

## Canonical State

Update `PROJECT_CORE.md` only after a durable change to strategy, innovation
status, component identity, explored-direction decision, evidence level, or
claim boundary. Preserve rejected and negative directions rather than
rewriting history.

Update `CURRENT_STAGE.md` only after a material milestone, formal review,
material blocker, or next-action change. Ordinary exploratory commits do not
imply that review closure is pending.

Keep branch, HEAD, current milestone, verdict, and next action out of
`PROJECT_CORE.md`. Detailed proofs and results belong in reports referenced by
the canonical files.

For an accepted formal review:

- `candidate_kind=implementation` updates both `last_reviewed_candidate` and
  `accepted_code_commit`;
- `candidate_kind=docs_only` updates only `last_reviewed_candidate`;
- rejected, blocked, and review-state commits never replace accepted code.

## Browser Work Contract

Browser Work uses four concise visible sections: `审查结果`, `设计目标`,
`验收目标`, and `Codex 指令`. The last section contains at most one fenced
`markdown` block with one Codex Goal.

This is an output format, not a mandatory review state machine. A state check
may contain no Goal. A clean review-state verification may be followed by the
next Goal in the same response. Exploratory work does not acquire a review
requirement merely because it produced a commit.

Keep Goals as short as correctness allows. Invoke this skill and reference
checked-in authorities instead of copying protocols, formulas, test matrices,
findings, hashes, history, or generic safety rules. Include only the unique
Goal, necessary Git identity, authority pointers, allowed scope, task-specific
delta, validation, delivery, and stop condition.

## Hooks

Hooks may inject compact canonical context and warn about malformed authorities
or an explicitly staged formal review that is not synchronized with
`CURRENT_STAGE.md`. They must not infer that every commit needs review, decide
scientific claims, edit files, or block exploratory execution.

## Handoff

Automatic context compaction is normal and does not require a handoff. Use an
explicit handoff only when opening a new Codex or Browser Work conversation,
when critical constraints were demonstrably lost, or at a useful milestone.

Before handoff:

1. finish only the current safely verifiable operation;
2. read the three authorities and inspect actual Git state;
3. distinguish pushed facts from chat-only conclusions, uncommitted work, and
   unrun validation;
4. run `audit`;
5. generate the relevant `resume-prompt`.

Do not commit an unfinished candidate merely to make a handoff look clean.
Do not create `CODEX_HANDOFF.md`, `LATEST_STATE.md`, or another dynamic source
of truth.

Browser Work cannot load local hooks, skills, or memory. It must use repository
authorities, Project Instructions, the public Work contract, and a generated
resume prompt. If it cannot read GitHub, attach current authorities for that
conversation only; do not preserve stale copies as Project Files.
