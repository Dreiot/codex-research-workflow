# Browser Work Response Contract

## Change Control

Only the user may authorize changing, renaming, replacing, relaxing, or
expanding this contract. Agents must not modify it autonomously. After an
authorized change, synchronize the public repository and installed skill,
update tests and generated prompts, validate the skill, and review the diff.

This contract governs concise visible output. It is not a mandatory review
workflow and does not request hidden reasoning.

## Output

When a response evaluates state, reviews a formal promotion candidate, verifies
a review-state commit, or issues a Codex Goal, use these four sections:

1. `## 审查结果`
2. `## 设计目标`
3. `## 验收目标`
4. `## Codex 指令`

Keep the first three sections short. Under `## Codex 指令`, include at most one
fenced `markdown` block containing one executable Codex Goal. A state check or
answer that needs no repository action may leave this section as `无`.

### 审查结果

State what was inspected, the exact Git object when relevant, the conclusion,
material findings, and whether a formal review still needs recording. Do not
describe a state check or review-state verification as a new candidate review.

Formal promotion reviews use exactly one verdict: `ACCEPT`,
`ACCEPT_WITH_P2`, `REJECT`, or `BLOCKED`. `ACCEPT` has no open findings;
`ACCEPT_WITH_P2` has only non-blocking P2 findings. P2 is non-blocking by
definition, so a P2 description must not call itself blocking or say that it
prevents promotion. Any P0 or P1 requires `REJECT`; use `BLOCKED` only when
required evidence or environment is unavailable, and describe each blocker as
`BLOCKED: ...`.

### 设计目标

Briefly explain the next useful research action. Default to implementation,
real-data execution, metrics, diagnosis, or direction adjustment. Do not create
a design-only or protocol-only Gate unless an unresolved decision prevents
credible execution.

### 验收目标

Name only the behavior, tests, metrics, evidence, or Git state needed to know
the Goal is complete. Do not turn optional completeness improvements into
acceptance criteria.

### Codex 指令

Start every actionable Goal with `$codex-research-workflow`. Codex will reload
repository authorities and actual Git state. Include only:

- the unique Goal;
- necessary expected branch, base, or candidate identity;
- authority and report pointers;
- allowed scope and task-specific boundaries;
- required tests or experiment outputs;
- commit/push requirements when applicable;
- the stop condition.

Reference checked-in detail instead of copying protocols, formulas, matrices,
findings, hashes, history, boilerplate, or generic safety rules. Keep the Goal
as short as correctness allows. Once acceptance criteria pass, stop.

For a historical or batch cleanup Goal, invoke both
`$codex-research-workflow` and `$research-artifact-cleanup`. Do not invoke the
cleanup Skill for current-run temporary-file cleanup.

## Research Flow

The default flow is:

`minimal implementation -> real-data run -> metrics -> diagnosis -> direction adjustment -> paper evidence`

Exploratory implementation, testing, smoke, debugging, parameter adjustment,
and metric generation do not require independent review or review-state
recording. Work may issue the next bounded empirical Goal as soon as repository
state supports it.

Use one independent review only for an explicit formal promotion: accepting a
major implementation baseline, freezing a publication evaluation, adopting a
key result, changing the core method, or raising a paper claim.

After a formal promotion review:

- if recording is pending, issue a review-state recording Goal;
- mechanical verification creates no new review or recording;
- if verification passes, the same Work response may issue the next Goal;
- a formally rejected or blocked promotion is recorded before remediation.

Do not duplicate a qualifying Browser Work review with a Codex reviewer.

## Boundaries

- One response contains at most one executable Codex Goal.
- A clean verification and the next Goal may coexist because verification is
  not a second Goal.
- Adjacent issues may be reported but must not be investigated unless they
  directly block completion.
- Non-blocking findings remain backlog and do not block empirical work.
- Ask before paid, sensitive, external side-effecting, destructive, or
  irreversible actions.
- Do not invent acceptance, conceal material negative evidence, or raise claims
  beyond the evidence.
- Do not use decorative separators or multiple copy-paste instruction blocks.
- If material Git or authority facts conflict, issue only a bounded
  reconciliation or evidence-gathering Goal.

## Skeleton

    ## 审查结果
    <Concise state, review, or verification conclusion.>

    ## 设计目标
    <The next useful research action.>

    ## 验收目标
    <Minimal completion evidence.>

    ## Codex 指令
    ```markdown
    $codex-research-workflow
    Goal: ...
    ```
