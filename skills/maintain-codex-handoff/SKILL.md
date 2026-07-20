---
name: maintain-codex-handoff
description: Create, audit, update, and resume canonical research-project handoffs based on AGENTS.md, docs/PROJECT_CORE.md, and docs/CURRENT_STAGE.md. Use after implementation or review gates, before cross-task handoff, when a Codex task is resumed or compacted, when project strategy or innovation history must be preserved, when stale CODEX_HANDOFF.md or LATEST_STATE.md files exist, or when generating a browser ChatGPT Work resume prompt.
---

# Maintain Codex Handoff

Use three authorities with non-overlapping responsibilities:

- `AGENTS.md`: stable operating rules, permissions, validation, Git, review, and
  claim boundaries.
- `docs/PROJECT_CORE.md`: durable research strategy, target contribution,
  innovation hypotheses, component map, explored-direction decision ledger,
  evidence position, and scientific boundaries.
- `docs/CURRENT_STAGE.md`: volatile branch, current Gate, exact review state,
  open findings, and next single action.

Treat Git and checked-in project evidence as the source of truth. A conversation
summary is only an entry pointer, never an authority.

## Modes

Use the bundled script with the smallest mode that fits:

```powershell
py -3 scripts/handoff.py audit --repo <repo>
py -3 scripts/handoff.py initialize --repo <repo>
py -3 scripts/handoff.py record-review --repo <repo> --input <review.json>
py -3 scripts/handoff.py resume-prompt --repo <repo> --surface codex
py -3 scripts/handoff.py resume-prompt --repo <repo> --surface work
```

- `audit`: validate all canonical files, both JSON schemas, Git ancestry, report
  pointers, authority alignment, and legacy handoff files. It never writes.
- `initialize`: create missing canonical files with conservative placeholders.
  Never overwrite an existing canonical file.
- `record-review`: update only `CURRENT_STAGE.md` from a structured review
  result. Write the detailed review report first; this command invents neither
  evidence nor scientific conclusions.
- `resume-prompt`: print a compact prompt that forces the next Codex or browser
  Work conversation to reload strategy and volatile state from the repository.

Read [project-core-schema.md](references/project-core-schema.md) before changing
the strategic core, and [current-stage-schema.md](references/current-stage-schema.md)
before manually changing volatile state.

## Strategic Core

`PROJECT_CORE.md` preserves knowledge that should survive many Goals and
conversations:

- research question, intended paper contribution, and primary direction;
- innovation hypotheses, each marked as proposed, supported, rejected, or
  superseded rather than silently promoted to a contribution;
- core mathematical/software components, their roles, interfaces, dependencies,
  implementation locations, maturity, and evidence;
- explored directions, including negative results, decision reason, reusable
  residue, and the report or experiment that supports the decision;
- current evidence tier and the strongest claim presently supportable;
- data, provenance, mathematical, experimental, and publication boundaries;
- open strategic questions, decision criteria, dependency roadmap, and canonical
  source index.

Update it only after a strategic decision, architecture change, material
evidence change, or explicit project-core audit. Preserve prior decisions in the
ledger; do not rewrite history. If a strategic change alters the active Gate,
synchronize `CURRENT_STAGE.md` in the same governance change.

Never put branch, current HEAD, current Gate, latest verdict, or next action in
`PROJECT_CORE.md`. Those belong only in `CURRENT_STAGE.md`. Detailed proofs,
reviews, and experiment results stay in their own reports; the core links to
them instead of copying them.

## Research Delivery Economy

Optimize method development for the shortest credible path from a research
question to reproducible evidence and a defensible paper claim. Work should
define the smallest decision-complete Goal and experiment matrix sufficient to
test the current hypothesis; Codex should implement the simplest bounded
solution that is correct, testable, reproducible, and robust at material
failure boundaries. Prefer existing components, small diffs, early end-to-end
experiments, and measurable results over speculative abstractions, duplicate
mechanisms, broad refactors, exhaustive generalization, or unnecessary
design-only Gates. Expand scope only when evidence, independent review, or the
target publication claim requires it. Never trade away data integrity,
statistical validity, reproducibility, fail-closed safeguards, or claim
boundaries for speed or smaller code.

## Gate Workflow

1. Read `AGENTS.md`, `docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`, the current
   Gate specification, and relevant reports.
2. Verify branch, `HEAD`, remote tracking ref, and worktree status. Stop on a
   conflict between Git, strategy, and stage state.
3. Implement one bounded Goal and push one candidate commit.
4. Obtain exactly one qualified independent review pinned to the base and
   candidate SHAs. Prefer a browser ChatGPT Work review when the user supplies
   its complete evidence and verdict; otherwise spawn a fresh
   `research-reviewer` subagent. Do not pass implementation rationale as
   evidence.
5. Require the reviewer to inspect the actual diff, tests, and repository
   evidence and return `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, or `BLOCKED`, plus
   P0/P1/P2 findings. Record the review source in the detailed report.
6. Write the review report, run `record-review`, validate with `audit`, and
   create a separate governance-docs-only review-state commit.
7. Push the review-state commit before ending or handing off the task.

## Reviewer Selection

- A candidate needs one qualified independent review, not duplicate reviews
  from both browser Work and a Codex subagent.
- A browser Work review qualifies when it is independent of implementation,
  names exact base/candidate SHAs, inspects the actual GitHub diff and relevant
  evidence, and returns the fixed verdict and severity format.
- Use `research-reviewer` only when no qualifying Work review exists, the Work
  evidence is incomplete or unverifiable, conclusions conflict, or the user
  explicitly requests a second opinion.
- When recording an external Work review, preserve its evidence and normalized
  verdict in a repository report; never infer acceptance from a chat summary.

P0 or P1 findings require `REJECT`. Use `ACCEPT_WITH_P2` only when every P2 is
explicitly non-blocking. Use `BLOCKED` when evidence or environment is
insufficient.

## Safety

- Do not let hooks or this skill decide scientific claims.
- Do not auto-commit or auto-push from bundled scripts.
- Do not record secrets, raw private data, large logs, or generated artifacts.
- Do not rewrite historical reports or explored-direction decisions to make the
  project look cleaner.
- Do not keep a second dynamic handoff file. Mark old `CODEX_HANDOFF.md` and
  `LATEST_STATE.md` as legacy or remove them when they are untracked and stale.
- Hooks may warn and inject compact context, but they must not edit repository
  files.

## Compaction and Explicit Handoff

Automatic context compaction is normal continuity inside the same Codex task;
it is not a reason to stop, commit, or open a new task. On `compact`, the
`SessionStart` Hook reloads the canonical strategy and Gate summary. Persist
state when an evidence-backed event occurs, not when a context meter becomes
large:

- update `PROJECT_CORE.md` after a durable strategy, component identity,
  explored-direction status, evidence level, or claim boundary changes;
- update `CURRENT_STAGE.md` after an authorized Gate, review, finding, or next
  action changes;
- keep detailed evidence in its report at the time it becomes authoritative.

Use an explicit handoff only when opening a new Codex task or browser Work
conversation, when compaction has demonstrably lost a critical constraint or
created a conflict, or at a natural Gate boundary where a clean context is
useful. Before that handoff:

1. Finish only the current atomic operation that can be completed and verified
   safely. Handoff pressure is not authorization to accept a candidate, weaken a
   Gate, edit outside the whitelist, or commit incomplete work.
2. Re-read the three authorities and verify actual branch, `HEAD`, remote ref,
   index, worktree, and the reports needed by the current Gate.
3. Separate facts already committed and pushed from chat-only conclusions,
   uncommitted changes, unrun validation, and unauthorized future work.
4. Run `audit`. If the repository is intentionally dirty or closure is blocked,
   report the exact state without disguising it as a completed handoff.
5. Generate the appropriate `resume-prompt`; the next conversation must reload
   repository authorities and verify Git rather than inherit a long narrative.

For browser Work, distinguish an independent review completed in chat from a
review-state commit already recorded in GitHub. If recording is still pending,
issue a bounded docs-only Codex Goal and do not advance the research Gate. Never
store a stale `CURRENT_STAGE.md` copy as a permanent Project File.

## Browser Work

Browser ChatGPT Work does not load local Codex hooks, skills, or local memory.
Use repository `AGENTS.md`, `docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`,
static Project Instructions, and the generated Work resume prompt. Work should
own strategic synthesis and candidate-independent review; Codex should own
bounded implementation and repository verification.

If Work cannot read the repository, attach the latest `PROJECT_CORE.md` and
`CURRENT_STAGE.md` for that conversation only. Do not keep stale copies in
Project Files. When intentionally opening a new conversation, hand off with the
generated short prompt; the next conversation must reload the three authorities
rather than trusting pasted narrative.
