---
name: codex-research-workflow
description: Initialize, migrate, audit, execute, review, and resume single-root governed research projects based on AGENTS.md, docs/PROJECT_CORE.md, and docs/CURRENT_STAGE.md. Use for every research-controller-issued Codex Goal in a governed project, and for project setup, root validation, durable direction changes, decision-complete evidence, optional implementation inspection, formal promotion, state conflicts, or explicit handoff. Keep ordinary implementation, smoke, and exploration execution-first; invoke research-artifact-cleanup only for historical or batch cleanup.
---

# Codex Research Workflow

Treat the Codex-opened project root and exact Git root as the same directory.
`--repo` always names that project root. Do not support a parent workspace with a
nested project repository; stop and require a user-approved root migration.

Treat Git and checked-in evidence as authoritative. Use:

- `AGENTS.md` for stable operating, permission, Git, review, storage, and claim rules.
- `docs/PROJECT_CORE.md` for durable research direction, innovations, components,
  direction decisions, evidence position, and claim ceiling.
- `docs/CURRENT_STAGE.md` for the current Gate, reviewed identity, material
  findings, and one next action.

Conversation summaries are entry pointers, not repository authority.

A research controller or reviewer decides and issues a Goal; Codex executes an
already-issued Goal. When acting as the executor, do not adopt the controller
role, issue the next Goal, or use the controller response format.

## Restore State

At an ordinary new Goal, read the authorities and controlling material needed
for that Goal, then perform a lightweight local precheck: exact Git root,
branch, HEAD against the expected base, and conflicting index or worktree
changes. Do not repeat the controller's remote review or run a full audit merely
because a Goal started. Fetch and check the tracking ref, then run
`workflow.py audit`, before commit or push, formal promotion, authority updates,
explicit handoff, or when local state conflicts with the Goal.
Inspect protected paths only when the Goal reads or changes data, results, or
cleanup state. Do not load chronological ledgers or old reports unless current
authorities point to them, state conflicts, or historical tracing requires them.

Use the read-only SessionStart Hook only as a compact pointer. A Hook failure is
fail-open; an explicit `workflow.py audit` is fail-closed for material authority
or Git conflicts.

## Execute Research

Default to the shortest credible empirical loop:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

Prefer restartable end-to-end Goals that reach scientific metrics. Local,
recoverable, no-cost work using authorized data may combine implementation,
relevant checks, real-data execution, metrics, diagnosis, and adjustment without
a new Gate. A separate smoke is exceptional and should test only the smallest
representative case justified by a genuinely untested interface or an action
that is paid, sensitive, irreversible, externally consequential, or likely to
consume a substantial share of the experiment budget if it fails.

Within an issued Goal, reversible evidence-driven adjustments may proceed and
be recorded when they do not materially change the core method, research
objective, main baseline, final held-out boundary, paper claim, or meaningful
cost or risk. Otherwise pause, present facts, uncertainty, two or three routes,
costs and information gain, a recommendation, and one clear choice. Do not
continue until the user chooses.

Stop when the Goal acceptance criteria pass or the result is sufficient for the
next decision. Do not investigate adjacent issues merely for completeness.

## Research Reasoning And Communication

When analyzing, interpreting, deciding, reviewing, or writing, follow the
assigned task, available evidence, intended audience, and existing claim
boundary.

Lead with the best-supported judgment or recommendation, then explain the
reasoning and evidence. Add uncertainty, alternatives, limitations, and
boundaries only when they could materially change the conclusion, action,
scientific validity, reproducibility, or claim.

Do not invent objections, risks, reviewer demands, failure scenarios,
experiments, or balancing language merely to appear cautious or comprehensive.
Do not dilute an evidence-supported conclusion by giving equal weight to
unsupported possibilities. Preserve material uncertainty and negative evidence,
but do not distribute defensive qualifications across every analytical step or
paragraph.

When a genuine decision has multiple credible routes, explain their material
differences, costs, and information value and request the required choice.
Otherwise provide the clearest supported conclusion and proceed within the
assigned scope.

When reviewing research or prose, report actual factual, methodological,
evidential, logical, or material expression problems. Distinguish them from
stylistic preferences, hypothetical objections, and requirements unrelated to
the active research question or claim.

## Validate Proportionately

Default to semantic checks, declared numerical tolerances, material invariants,
and existing Git identity. Add a content hash only when exact bytes outside Git
materially affect reproducibility or a known integrity failure is not covered by
those checks. Do not duplicate commit-bound identities with file, payload, or
manifest hashes merely for completeness, and do not use floating-output hashes
as numerical acceptance criteria. Preserve an explicit frozen identity contract.

## Manage Experiments

Use one experiment root inside the project root, default `experiments/`; a project may
override it only in `AGENTS.md`. Create it and its subdirectories only when
needed. New persistent artifacts must not create ad hoc top-level output roots.

- Keep reusable method code in normal source directories.
- Keep experiment entrypoints/configuration under `scripts/` and `configs/` in
  the experiment root when they are needed.
- Keep persistent local runs under `runs/<experiment-id>/<run-id>/` with
  minimal provenance; keep raw and external datasets outside the experiment root.
- Keep dedicated decision-complete evidence under
  `evidence/<experiment-id>/<candidate-id>/` and track it in Git.
- Keep large runs, temporary files, and cleanup plans ignored by Git.
- Delete only temporary files created by the current run when they were marked
  temporary in advance, the run succeeded, and no reference remains.

Read [experiments.md](references/experiments.md) before creating a persistent
run. Read [evidence-packets.md](references/evidence-packets.md) before preparing
material for a durable controller decision or formal promotion.

## Review Code And Evidence

Routine exploratory code may continue after task-relevant tests pass. A concise
Codex result packet is normally enough for the controller. Request an optional
implementation inspection only when tests and results cannot establish the
needed correctness or the exact diff is needed to interpret evidence. It may
inspect uncommitted work and does not require commit or push unless the reviewer
needs GitHub access or the work is entering formal promotion. It creates no
formal verdict, `record-review`, or `CURRENT_STAGE.md` update.

Use formal promotion only to accept a major implementation baseline, adopt a
stable publication evaluation or key result, change the core method, or raise a
claim. Pin one exact candidate commit and obtain one qualified independent
review from a controller or reviewer with direct access to the exact candidate
and evidence. Select that reviewer by actual evidence access, not model tier or
surface, and do not duplicate a qualified review. Then create one necessary
authority update. Preserve rejected candidates and negative evidence in Git
history. Read
[formal-review.md](references/formal-review.md) for this lane.

Codex-reported local results can guide another reversible exploratory step.
Before a durable direction change, method/result adoption, or claim change,
make the evidence accessible and decision-complete. Prefer existing tracked
reports, configurations, results, or registry entries when they already answer
the decision question. Create a dedicated evidence packet only when those
materials are insufficient or a formal promotion needs a stable bundle.
Structure and accessibility validation cannot declare scientific sufficiency.

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

Cleanup inventory starts at the entire project root, including ignored local
artifacts; Git tracking is evidence metadata, not the scan boundary. Cleanup
execution is not a formal research Gate. Use a Cleanup Plan Review,
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

## Research Controller Contract

Every actionable research-controller-issued Codex Goal starts with
`$codex-research-workflow`. A cleanup Goal also invokes
`$research-artifact-cleanup`. Keep Goals short by pointing to checked-in
authorities and reports rather than copying durable detail.

Read [work-response-contract.md](references/work-response-contract.md) before
generating or evaluating a controller response. Only the user may authorize
changing that contract.

The Contract does not govern a Codex executor's final report. After executing a
Goal, report only the actual outcome, changed paths, validation or experiment
results, commit/push state, and unresolved items or blockers. Do not output the
controller headings or a `Codex 指令` section.

## Explicit Handoff

Automatic context compaction is normal and is not itself a handoff. At an
explicit handoff, finish only the safely verifiable operation, re-read current
authority and Git state, distinguish pushed facts from chat-only conclusions,
run `audit`, and generate the relevant `resume-prompt`. Never create
`CODEX_HANDOFF.md`, `LATEST_STATE.md`, or another dynamic authority.

The installed Skill governs Codex handoff only. Browser Chat and Work do not
load it; they follow their Project Instructions, visible context, and the public
Work Response Contract. Codex may generate a temporary packet for the user to
paste into a browser conversation.

A controller handoff is not a formal review or a reason to update repository
authority. A same-conversation reviewer-to-controller switch uses a compact
Controller Packet. A new controller conversation needs a temporary Handoff
Packet containing the durable strategy and claim ceiling from `PROJECT_CORE.md`,
relevant positive and negative evidence, the current Git transaction,
conversation-only decisions or rejected options, and one next decision or
action. A recipient with direct repository access reverifies mutable state and
may perform the required review. One without it requests one bounded
verification from a reviewer with the required access. Do not force a model
switch or duplicate a qualified review. Keep the packet temporary unless a
material decision independently belongs in repository authority.
