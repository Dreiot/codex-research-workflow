---
name: codex-research-workflow
description: Initialize, migrate, audit, execute, review, and resume single-root governed research projects based on AGENTS.md, docs/PROJECT_CORE.md, and docs/CURRENT_STAGE.md. Use for every research-controller-issued Codex Goal in a governed project, and for project setup, root validation, durable direction changes, decision-complete evidence, optional implementation inspection, formal promotion, state conflicts, or explicit handoff. Keep ordinary implementation, smoke, and exploration execution-first; invoke research-artifact-cleanup only for historical or batch cleanup.
---

# Codex Research Workflow

`--repo` always names the Codex-opened project root. Git and GitHub are optional:
create a local Git repository or a GitHub repository only when the user explicitly
requests that creation, with the local repository rooted in this project.
When Git already exists, its exact root must be this same directory. Do not
support a parent workspace with a nested project repository; stop and require a
user-approved root migration.

Treat existing Git history and checked-in evidence as authoritative where
available; otherwise use the local authority files and retained evidence. Use:

- `AGENTS.md` for stable operating, permission, Git, review, storage, and claim rules.
- `docs/PROJECT_CORE.md` for durable research direction, innovations, components,
  direction decisions, evidence position, and claim ceiling.
- `docs/CURRENT_STAGE.md` for the current Gate, reviewed identity, material
  findings, and one next action.

Conversation summaries are entry pointers, not repository authority.

A research controller or reviewer decides and issues a Goal; Codex executes an
already-issued Goal. When acting as the executor, do not adopt the controller
role, issue the next Goal, or use the controller response format.

An issued Goal authorizes the named work and its necessary consequences, not
adjacent improvements. A consequence is necessary when omitting it would make
the current result scientifically incorrect, materially incomplete,
non-reproducible, or unable to satisfy a stated acceptance condition. Ground
that need in reachable code, data, evidence, claim, or acceptance dependencies,
not hypothetical future use. Include affected callers, configurations, focused
tests, and evidence artifacts when such a dependency requires them. Discussion,
inspection, audit, and review-only Goals are read-only unless they explicitly
authorize a change.

## Restore State

At an ordinary new Goal, read the authorities and controlling material needed
for that Goal, then perform a lightweight local precheck: exact Git root,
branch, HEAD against the expected base, and conflicting index or worktree
changes when Git exists; without Git, verify the project root, relevant authority
files and source/evidence versions without inventing branch or commit identities.
Git-specific commands and formal commit-identity checks retain their existing
prerequisites; never create a repository to satisfy them implicitly.
Do not repeat the controller's remote review or run a full audit merely
because a Goal started. Fetch and check the tracking ref when a remote is
configured, then run
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

Follow the protocol or bounded exploration scope supplied or referenced by the
issued Goal. For formal evaluation, use the agreed data roles, model-selection
procedure, comparators, primary metrics, repetitions, and statistical unit.
Interpret results used for method or hyperparameter selection according to that
role. An issued Goal or frozen protocol authorizes the runs,
batches, safe resumes, and named held-out execution within its scope. Briefly
state the purpose, scope, material cost, and stop condition, then proceed
without per-run approval.

For each planned experiment, connect the scientific question or claim to the
comparison, observations, and decisions that different outcomes would inform.
Main comparisons assess the overall contribution. Ablations or replacement
controls assess a key design choice, and mechanism checks distinguish competing
explanations. Choose quantitative, qualitative, or visual evidence by its
purpose. When the plan includes an additional utility claim, test it against
its own question and criteria. Reuse equivalent evidence. Report actual results,
what each comparison supports, and material gaps. Keep deliverables decision-complete
rather than exhaustive. Do not generate a Cartesian product of scenario sets,
metrics, display choices, registries, and file formats, or prepare future audit
plans, unless the current decision needs them. Preserve reusable source data
and generation code, then render additional variants after the user selects them.

Reversible evidence-driven adjustments within the issued Goal may proceed and
be recorded while preserving the agreed boundaries. Refer unconfirmed material
choices about the research question, core method, main comparisons, data splits,
primary metrics, the final held-out boundary or other evaluation boundaries, claim, stopping
rules, or meaningful cost or risk to the controller or user under the
established roles. Use the same decision path for work outside existing
authorization that introduces paid or material external quota, new sensitive
data or credentials, or destructive or irreversible external effects. Report
the evidence, impact, uncertainty, and recommendation, with tradeoffs when
there are credible alternatives. Wait for the required decision only on
dependent work, and continue authorized exploration, diagnostics, and
verification within scope.

During exploration, actively identify and rank mechanism-matched datasets,
subgroups, regimes, parameter ranges, metrics, and comparisons that show the
method's clearest positive value. Report their mechanism rationale, positive
evidence, supportable claim, exploratory origin, material counterevidence, and
smallest useful follow-up to the controller or user. Do not let
mechanism-mismatched settings dominate the method assessment.

Stop when the Goal acceptance criteria pass or the result is sufficient for the
next decision. Do not investigate adjacent issues merely for completeness.

## Research Reasoning And Communication

Follow the assigned task, evidence, audience, and approved claim scope. In
research discussions and assessments, lead with the best-supported judgment
and develop clear, connected reasoning. Use accurate objects and inferential
wording, and carry established conditions forward.
Preserve material counterevidence with the finding it affects; concentrate
common limitations where they explain interpretation. Avoid routine
claim–withdrawal–validation cycles and imagined reviewer objections.

Match analytical depth to the research stage and material impact. During
ideation, prioritize the research question, mechanism, feasibility, potential
contribution, and a testable formulation. During implementation and evaluation,
examine details that affect correctness, reproducibility, comparison fairness,
or conclusions. Briefly flag minor issues when useful; investigate defects that
could invalidate the method, derivation, or main finding.

Assess research value by whether the overall design addresses a worthwhile,
specific problem through a coherent mechanism, supported by direct evidence
matching the core claims. Do not treat originality of every component,
independently statistically significant gains from every module, significant
superiority over every baseline, or wins in every setting as universal
prerequisites for research value or publication potential. Claims of a module's
independent gain or superiority over a specified baseline require corresponding
evidence.

For important issues requiring action, explain their consequences and, when
supported, recommend a concrete remedy or the most informative focused check.
Among scientifically adequate remedies, prefer proportionate changes and cost
that preserve evidence-supported research value. An independent reviewer need
not devise a remedy for a valid finding to stand.

When multiple meaningful evaluations of the same core objective remain below
expectations, or successive local changes repeat similar conclusions with
neither substantive progress nor new discriminating evidence, reassess the research
question, core assumptions, overall design, and relevant prior experiments
together. Organize variants, actual changes, results, and supported judgments
by scientific question, integrating material positive, negative, and mixed
evidence. Reassessment does not automatically stop valuable exploration.
Information gain also includes ruling out explanations, clarifying
applicability, confirming stability, and reducing uncertainty. An isolated
fluctuation, execution failure, or lack of wins over every baseline does not by
itself establish design failure.

Recommend whether the design should continue, narrow, be redesigned, stop, or
redirect, and identify remaining research value. Assess continuation at the
level of the validation question or experiment group. Additional local
variants need a specific rationale, possible outcomes that change the judgment
or reduce uncertainty, and a stopping condition. Stop extra attempts that lack
such a rationale and offer neither substantive progress nor information gain.
Keep required validation under its existing protocol and stopping rules; weak
interim trends alone do not justify truncating necessary repeats or changing
comparison boundaries. If explanations remain unresolved, prefer the smallest
useful diagnostic; if the core premise is contradicted or repair loses its
research value, recommend stopping or redirecting. Sunk effort and more
available parameters, modules, or combinations do not justify continuation.
Reuse relevant reports and results; reassessment alone does not require
historical reruns, an audit, or a new formal-review gate.

Reassessment does not revoke existing authorization. As executor, continue
justified diagnostics, required validation, and reversible adjustments within
the issued Goal without renewed approval, and explain the basis in the result
report. Refer work requiring a new Goal or crossing an existing material
decision boundary to the controller or user under the established roles and
approval rules; reporting a diagnosis alone does not create a waiting point.

Carry resolved issues and explicitly accepted limitations forward. Reopen them
only for new evidence, changed conditions, a material contradiction, or a
user-requested reassessment. An accepted limitation is not eliminated; retain
its material effect on interpretation. Recommendations do not authorize new
execution or promotion.

When a decision is needed, give a clear recommendation, its material evidence,
and the highest-priority next action. Distinguish confirmed problems, the
best-supported explanation, and unresolved uncertainty without forcing
certainty or inventing work. If a genuine decision has multiple credible
routes, explain their material differences, costs, and information value and
request the required choice; otherwise proceed within the assigned scope.

When reviewing research or prose, report actual factual, methodological,
evidential, logical, or material expression problems. Distinguish them from
stylistic preferences, hypothetical objections, and requirements unrelated to
the active research question or claim.

For authorized manuscript work, use `$academic-paper-writing` as the primary
writing specification for drafting, revision, translation, journal adaptation,
reviewer responses, and deliverables. This workflow governs research scope,
evidence, execution permissions, and project state; its general communication
rules supplement rather than override the writing Skill's genre, argument
order, revision workflow, or delivery requirements. Reuse that Skill's single
manuscript basis as a pointer to direct evidence and current author/research
decisions. Maintaining it alone neither changes research scope or claims nor
triggers an audit, Gate, formal review, or authority update.
Polishing prompts for Gemini or another editor remain optional, generated only
on user request under that Skill; manuscript work does not authorize external
transfer.

## Validate Proportionately

Do not calculate or require a content hash by default. Prefer Git commit/blob
identity or another stable dataset, model, or artifact version, together with
semantic checks, material-field checks, declared numerical tolerances, and
material invariants.

Use SHA-256 only for one specifically identified Git-external immutable file
whose exact bytes must be frozen for the active decision or run and for which no
stable identifier is sufficient. State the file and why byte identity matters.
Do not hash a Git-tracked file again, a complete environment, directory, cache,
report, registry, manifest, or dynamic output. Never use byte equality for
floating or stochastic results or as evidence of scientific validity.

An approved project-level frozen contract remains authoritative, but it does
not justify adding redundant hashes or exact matching of immaterial fields. If
relaxing an existing contract would change a formal evaluation boundary, stop
and request that scoped project amendment rather than bypassing it.

Target independent recomputation at the active defect or decision-critical
transformation. Do not revalidate unrelated accepted candidates or require byte
preservation when Git identity, a focused diff, or semantic invariants already
establish the needed fact.

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
  `evidence/<experiment-id>/<candidate-id>/`; track it when Git is in use.
- Keep large runs, temporary files, and cleanup plans separate from decision
  evidence and ignored by Git when Git is in use.
- Delete only temporary files created by the current run when they were marked
  temporary in advance, the run succeeded, and no reference remains.

When an authorization manifest, runtime guard, and result registry coexist,
give each a distinct role and keep one authority for each mutable fact. Other
artifacts reference that authority instead of maintaining duplicate state.

Read [experiments.md](references/experiments.md) before creating a persistent
run. Read [evidence-packets.md](references/evidence-packets.md) before preparing
material for a durable controller decision or formal promotion.

## Review Code And Evidence

Routine exploratory code may continue after task-relevant tests pass. A
decision-complete Codex result packet is normally enough for the controller;
make it concise only after retaining the scientific substance needed for the
next decision. Request an optional
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

Do not carry superseded or candidate-specific P2 findings into a later Goal or
current finding list unless they still materially apply. Preserve them in their
original review report or Git history.

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
Default `init` creates local authority files only. Use `--create-git` only for an
explicit local-repository request; `--github-repo OWNER/NAME --visibility ...`
is an explicit GitHub-creation request and also enables local Git creation.
`initialize` remains a compatibility alias for the former missing-file-only
operation and is not used in new documentation.

## Research Controller Contract

Every actionable research-controller-issued Codex Goal starts with
`$codex-research-workflow`. A cleanup Goal also invokes
`$research-artifact-cleanup`. Before issuing a Goal, compress it: point to
checked-in authorities and reports, remove clauses already implied by them,
merge repeated validation, stop, and return requirements, and retain only the
current task's necessary scope, exceptions, and acceptance evidence. State a
negative boundary only for a plausible adjacent action that would materially
change the result or permission boundary. Do not repeat the executor's default
final-report fields or replace a decision-complete report with a
commit/path/validation-only `Return` checklist. Omit a return schema unless the
task has a nonstandard reporting requirement. A complex Goal may remain long
when the required detail is not already authoritative; length itself is not
evidence of rigor.

Read [work-response-contract.md](references/work-response-contract.md) before
generating or evaluating a controller response. Only the user may authorize
changing that contract.

The Contract does not govern a Codex executor's final report. For ordinary
mechanical implementation, report the actual outcome, changed paths,
task-relevant validation, commit/push state, and unresolved items or blockers.

When execution produces or records decision-relevant scientific evidence,
closes a formal review or authority transaction, or performs an explicit
handoff, make the final report self-contained enough for the controller to
understand the substantive result and evaluate the next decision. Include the
best-supported conclusion and, as applicable, key quantitative comparisons,
material positive, negative, or mixed evidence, scientific interpretation and
claim boundary, unresolved blockers, and a supported next action or exact
decision when one remains. For a docs-only authority update, summarize the
recorded substantive verdict or finding and its operative consequence, not only
the commit and changed paths. Repository artifacts remain authoritative when
fresh verification is required; their paths are verification pointers, not
substitutes for this core information.

Scale detail to the decision. Do not reproduce complete authorities, raw logs,
exhaustive tables, or unrelated file inventories. Do not output the controller
headings or a `Codex 指令` section, and do not issue the next Goal.

## Explicit Handoff

Context compaction and larger context windows are continuation aids, not
authority, permission, or handoff triggers. After compaction, do not replay the
full history; before a state-sensitive action, re-ground only from the active
Goal and the minimum current authority needed for that action.

At an explicit handoff, finish only the safely verifiable operation, re-read
current authority and Git state, distinguish pushed facts from chat-only
conclusions, run `audit`, and use the relevant `resume-prompt` as the
deterministic base. If a complete controller-issued Goal already exists and no
local-only state remains, reuse that Goal unchanged in the new task; no extra
handoff packet is needed. Otherwise append only a short Handoff Delta containing
conversation-only decisions, unfinished authorized work or local state,
unrecorded decision-relevant evidence or blockers, and one unresolved decision
or action. Do not ask the old task to reconstruct authority content or rewrite
an issued Goal. Never create `CODEX_HANDOFF.md`, `LATEST_STATE.md`, or another
dynamic authority.

The installed Skill governs Codex handoff only. Browser Chat and Work do not
load it; they follow their Project Instructions, visible context, and the public
Work Response Contract. Codex may generate a temporary packet for the user to
paste into a browser conversation.

A controller handoff is not a formal review or a reason to update repository
authority. A same-conversation reviewer-to-controller switch uses a compact
Controller Packet.

A new browser controller conversation uses the Work `resume-prompt` plus a
compact Context Primer and the current Chat-Codex transaction. The Context
Primer briefly explains the user's controller-executor workflow, the project's
research question, target contribution, core method chain, intended paper or
deliverable, current phase, and claim ceiling. It may summarize repository
authority for orientation but does not replace it; detailed methods, metrics,
protocols, findings, and history remain in current authorities and reports.

The current transaction identifies the relevant Codex task, its one-sentence
Goal, status, input baseline, expected deliverables, and whether the controller
should wait, inspect, review, or resolve a blocker. Distinguish verified
repository state from Codex-reported local state. Append the Handoff Delta
described above only when one exists, then end with one next action and the
material work that must not be duplicated. Do not copy Project Instructions or
the full Codex Goal into the handoff.

A recipient with direct repository access reverifies mutable state and may
perform the required review. One without it requests one bounded verification
from a reviewer with the required access. Do not force a model switch or
duplicate a qualified review. Keep the primer and delta temporary unless a
material decision independently belongs in repository authority.

If a generated handoff is malformed, incomplete, contains placeholders, or
leaks drafting text, discard that packet. Prefer a new task based on the
deterministic `resume-prompt`, repository authority, and the original Goal over
repeated regeneration in the same long context. An invalid packet does not
invalidate previously verified repository state or a qualified review.
