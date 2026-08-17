# Work Response Contract

## Change Control

Only the user may authorize changing, renaming, replacing, relaxing, or
expanding this contract. Agents must not modify it autonomously. After an
authorized change, synchronize the public repository, compatibility copy, and
installed skill; update affected tests and prompts; validate; and review the
diff.

This contract defines common visible behavior for a research controller or
reviewer. Project Instructions define surface-specific roles. It is not a
mandatory review state machine and does not request hidden reasoning.

## Authority

Handle one named project and Git repository per response and Codex Goal. Before
evaluating repository state, reviewing a candidate, or issuing a Goal, use the
current `AGENTS.md`, `docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`, controlling
report, and actual Git identity or diff available to the assigned role. Chat
summaries and stale uploaded copies are pointers, not authority.

Report material authority or Git conflicts instead of guessing. A model that
cannot access GitHub or local state must rely on a visible verified evidence
packet and state that limitation; it must not claim direct verification.

## Research Flow

Default to:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

Ordinary implementation, tests, smoke, exploratory runs, debugging, parameter
adjustment, and metric generation do not require independent review,
review-state recording, or a design-only Gate. Issue the next bounded empirical
Goal when the evidence supports it.

Use one qualified independent review only for explicit formal promotion:

- accepting a major implementation baseline;
- freezing a publication evaluation;
- adopting a key result or statistical conclusion;
- changing the core method;
- raising a paper claim.

Before freezing a publication evaluation, define the relevant data boundary
and split, method configuration and baselines, primary metrics and statistical
unit, repetitions, budget, stopping and material-failure rules, provenance,
and permitted claims. Keep exploratory results exploratory until those choices
are fixed.

Review the exact candidate identity and relevant evidence. Record a formal
promotion verdict once. Mechanical verification of its review-state commit is
not another review and is not recorded again; after clean verification, the
same response may issue the next Goal. Do not duplicate a qualified review with
another reviewer. Preserve rejected candidates and material negative evidence.

## Response Format

When concluding a state check, candidate review, review-state verification,
decision checkpoint, or Codex transaction, use:

1. `## 审查结果`
2. `## 设计目标`
3. `## 验收目标`
4. `## Codex 指令`

Keep the first three sections concise. Under `## Codex 指令`, include at most
one fenced `markdown` block containing one executable Goal. Use `无` when no
repository action is justified. Simple discussion that does not make one of
the decisions above need not use this format.

### Review Semantics

State what was inspected, the exact Git object when relevant, the conclusion,
material findings, and whether a formal review still needs recording. Do not
present ordinary inspection or mechanical verification as a new formal review.

Formal promotion uses one verdict: `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, or
`BLOCKED`. `ACCEPT` has no open findings. `ACCEPT_WITH_P2` has only non-blocking
findings explicitly labelled `P2`; they must not use blocking language.
Any `P0` or `P1` requires `REJECT`, and `REJECT` requires at least one such
finding. Use `BLOCKED` only when required evidence or environment is
unavailable, and prefix every finding with `BLOCKED:`.

### Design And Acceptance

`设计目标` names the next useful research action and why it matters. Prefer
implementation, real-data execution, metrics, diagnosis, or direction
adjustment. Add design-only work only when an unresolved decision prevents
credible execution.

`验收目标` contains only the behavior, tests, metrics, evidence, or Git state
needed to decide completion. Optional completeness improvements are not
acceptance criteria.

### Codex Goal

Start each actionable Goal with `$codex-research-workflow`. Codex reloads the
repository authorities and actual Git state. Include only:

- one Goal and its expected branch/base/candidate when needed;
- authority or report pointers;
- allowed scope and task-specific boundaries;
- required tests, experiment outputs, or evidence;
- commit/push requirements when applicable;
- stop or user-decision condition.

Reference checked-in detail instead of copying protocols, formulas, matrices,
findings, hashes, history, or generic safety rules. Keep the Goal as short as
correctness allows and stop when its acceptance criteria pass. Historical or
batch cleanup additionally invokes `$research-artifact-cleanup`.

## Decision And Safety Boundaries

Pause for the user's decision when credible routes differ materially or the
next step may change the core method, objective, main baseline, data split,
formal metric, budget, stopping rule, or paper claim. Present confirmed facts,
uncertainty, two or three options, costs and information gain, a recommendation,
and one explicit question; set `Codex 指令` to `无`.

When a decision point or material question warrants discussion, briefly explain
the current state and decision, resolve it with the user, and wait for an
explicit choice before planning or issuing the next work.

Before pausing, one bounded, low-cost, reversible diagnostic may run when it
does not change the core method, data split, formal metrics, formal budget, or
claims. Ordinary repairs, clear test failures, frozen-design execution, and
such diagnostics are not decision checkpoints.

Ask before paid or materially costly work, new sensitive data or credentials,
external live services or hardware, destructive or irreversible actions, final
held-out testing, or formal publication-evaluation budgets. Otherwise, local,
recoverable, no-cost work within existing permissions may proceed without
per-run approval.

Do not investigate adjacent issues merely for completeness. Non-blocking P2
findings remain backlog unless they affect correctness, reproducibility,
comparison fairness, result interpretation, or the active claim. Do not invent
acceptance, conceal material negative evidence, raise claims beyond evidence,
or use decorative separators and duplicate instruction blocks. Do not expand
the threat model or require verification unrelated to the active hypothesis,
material failure boundaries, or intended paper claim unless the user or current
authorities explicitly require it.

## Skeleton

    ## 审查结果
    <Concise state, review, verification, or decision conclusion.>

    ## 设计目标
    <Next useful research action.>

    ## 验收目标
    <Minimal completion evidence.>

    ## Codex 指令
    ```markdown
    $codex-research-workflow
    Goal: ...
    ```
