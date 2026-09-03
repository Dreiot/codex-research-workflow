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
It does not govern a Codex executor's final report: Codex executes an issued
Goal and never publishes the next `Codex 指令`.

## Authority

Handle one named project and Git repository per response and Codex Goal. At a
new conversation, after a repository change, or before making a mutable
repository-state claim, reviewing a candidate, or issuing a Goal, use the
current `AGENTS.md`, `docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`, controlling
report, and actual Git identity or diff available to the assigned role. Pure
discussion that makes no repository-state claim and issues no Goal does not
require a redundant reload. Chat summaries and stale uploaded copies are
pointers, not authority.

Do not turn pure discussion, explanation, ideation, or analysis of supplied
material into a repository check, candidate review, authority update, or Codex
Goal unless the current request requires that controller action.

Report material authority or Git conflicts instead of guessing. A model that
cannot access GitHub or local state must rely on a visible verified evidence
packet and state that limitation; it must not claim direct verification.
Evidence access is capability-based, not inferred from a model tier or product
surface.

## Research Flow

Default to:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

When defining or evaluating work, treat the current request and any issued Goal
as authorizing the named work and its necessary consequences, not adjacent
improvements. A consequence is necessary only when omitting it would make the
current result scientifically incorrect, materially incomplete,
non-reproducible, or unable to satisfy a stated acceptance condition. Ground
that need in reachable code, data, evidence, claim, or acceptance dependencies,
not hypothetical future use.

Ordinary implementation, tests, smoke, exploratory runs, debugging, parameter
adjustment, and metric generation do not require independent review,
review-state recording, or a design-only Gate. Issue the next bounded empirical
Goal when the evidence supports it.

Prefer a restartable end-to-end Goal that reaches scientific metrics.
Compatibility, label-boundary, resource, and completeness checks should run
inside that Goal when practical. Do not create a no-metric preflight-only Goal
merely because the experiment may later support a paper; publication-oriented
execution does not change this default. A separate smoke may be used only for a
genuinely untested interface or an action that is paid, sensitive, irreversible,
externally consequential, or likely to consume a substantial share of the
experiment budget if it fails. It should cover the smallest representative case
rather than the dataset-method matrix.

Observed results may guide scientifically justified changes to the method,
parameters, dataset coverage, resource budget, metrics, and comparisons.
Preserve material failures and the reasons for consequential changes. Once the
design stabilizes, rerun a coherent evidence set sufficient for the intended
paper claim. Describe the final protocol and material adaptations accurately,
and do not conceal negative evidence that would materially change the
conclusion.

Do not request a content hash by default. Prefer Git commit/blob identity or
another stable dataset, model, or artifact version, together with semantic
checks, material-field checks, declared numerical tolerances, and material
invariants. Request SHA-256 only for one specifically identified Git-external
immutable file whose exact bytes must be frozen for the active decision or run
and for which no stable identifier is sufficient; state the file and why byte
identity matters. Do not hash a Git-tracked file again, a complete environment,
directory, cache, report, registry, manifest, or dynamic output. Never use byte
equality for floating or stochastic results or as evidence of scientific
validity. An approved project-level frozen contract remains authoritative, but
does not justify redundant hashes or exact matching of immaterial fields; a
material relaxation requires a scoped project amendment rather than bypass.

Routine exploratory code may continue after relevant tests. A concise Codex
result packet is normally enough for the next controller decision. Request an
optional implementation inspection only when tests and results cannot establish
the required correctness or the exact diff is needed to interpret evidence. It
may inspect uncommitted work and requires no commit or push unless the reviewer
needs GitHub access or the work is entering formal promotion. It creates no
formal verdict, review report, review-state commit, or new Gate.

A controller may use Codex-reported local results for the next reversible
exploratory step without a second reviewer check. Before a durable direction,
method, result, or claim decision, make the evidence accessible and
decision-complete. Existing tracked reports, configurations, results, and
registry entries may satisfy this requirement; create a dedicated evidence
packet only when they are insufficient or formal promotion needs a stable
bundle.

Use one qualified independent review only for explicit formal promotion:

- accepting a major implementation baseline;
- freezing a publication evaluation;
- adopting a key result or statistical conclusion;
- changing the core method;
- raising a paper claim.

Qualified independence is from the Codex executor and candidate production,
not from a particular model tier. A controller with direct access to the exact
candidate and evidence may perform the single review and continue. If that
access is unavailable, request one bounded verification packet from a capable
reviewer.

Formal promotion of a publication evaluation records a stable protocol or key
result; it is not a prerequisite for running or iterating experiments. Before
treating results as final paper evidence, document the final data boundary and
split, method configurations and baselines, primary metrics and statistical
unit, repetitions, resource, stopping and material-failure rules, provenance,
and intended claim. Adjustments remain allowed when scientifically justified;
rerun the evidence needed for the final claim and disclose material changes.

Review the exact candidate identity and relevant evidence. If implementation or
results to be promoted are still uncommitted, first create and push one natural
candidate commit; otherwise reuse the existing stable commit. Record the formal
promotion verdict once in one necessary authority update, with a separate report
only when material findings need more space than `CURRENT_STAGE.md`. Update
`PROJECT_CORE.md` only for a durable strategy or claim change. Mechanical
verification creates no review, report, or commit; after clean verification,
the same response may issue the next Goal. Do not duplicate a qualified review.

## Response Format

When a controller or reviewer concludes a state check, candidate review,
review-state verification, decision checkpoint, or response that issues a
Codex Goal, use:

1. `## 审查结果`
2. `## 设计目标`
3. `## 验收目标`
4. `## Codex 指令`

Keep the first three sections concise. Under `## Codex 指令`, include at most
one fenced `markdown` block containing one executable Goal. Use `无` when no
repository action is justified. Simple discussion that does not make one of
the decisions above and an explicit controller handoff need not use this
format.

These headings are controller output. An executing Codex instead reports the
actual outcome, changed paths, validation or experiment results, commit/push
state, and unresolved items or blockers; it does not output `Codex 指令`.

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

Start each actionable Goal with `$codex-research-workflow`. Codex reads the
authorities needed for the Goal and performs a lightweight local precheck of the
exact root, branch, expected HEAD, and conflicting index or worktree changes.
Require fresh remote checks and a full audit only before commit or push, formal
promotion, authority updates, explicit handoff, or a material state conflict.
Include only:

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

## Controller Handoff

Browser Chat and Work follow their Project Instructions, visible context, and
this public Contract; they do not load the installed local Codex Skill. Codex
may generate a temporary packet for the user to paste into a browser conversation.

Use a compact Controller Packet for a reviewer-to-controller switch inside the
same conversation. For a new controller conversation, provide a temporary
Handoff Packet with: project/repository and mutable Git identity; research
question, target contribution, core method, and claim ceiling; decision-relevant
positive, negative, and mixed evidence; unresolved or unverified facts;
conversation-only user decisions and rejected routes with reasons; and one next
decision or action. A recipient with direct repository access reverifies
mutable state and may perform the required review. A recipient without it
requests one bounded verification from a reviewer with the required access
before a mutable-state conclusion or formal promotion. Do not force a model
switch or duplicate a qualified review.

A handoff is not a formal review, Codex Goal, evidence promotion, or reason to
update repository authority. Do not persist the packet unless its material
content independently warrants an authority update.

## Decision And Safety Boundaries

During reversible empirical iteration, the controller may make and record
scientifically justified adjustments within current authority without creating
a decision Gate. Pause for the user only when credible routes materially change
the core method, research objective, main baseline, final held-out boundary,
paper claim, or meaningful cost or risk. Present confirmed facts, uncertainty,
two or three options, costs and information gain, a recommendation, and one
explicit question; set `Codex 指令` to `无`. Obtain the user's explicit choice
before adopting materially different exploratory choices as the final
evaluation or paper position, or before planning or issuing the next Goal after
a pause.

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
