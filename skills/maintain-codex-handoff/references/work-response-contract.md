# Browser Work Response Contract

## Change Control

This public contract may be changed, renamed, replaced, relaxed, or expanded
only after the user explicitly authorizes a change to this contract. Do not
infer authorization from a request to use the skill, initialize or audit a
project, improve a project prompt, perform a review, or update project
governance. Agents must not modify this contract autonomously.

After an explicitly authorized contract change, keep the change bounded,
synchronize the public repository and installed skill copies, update tests and
generated prompts, validate the skill, and review the resulting diff before
delivery.

Use this contract for Browser ChatGPT Work responses that review a candidate,
verify a review-state commit, revalidate repository state, or issue the next
Codex Goal.

This contract governs visible output and decision boundaries. It does not ask
for or expose hidden chain-of-thought. Summarize conclusions and evidence
briefly.

## Required Output

Return exactly four top-level sections, in this order, with no preface,
epilogue, decorative separator, or second instruction block:

1. `## 审查结果`
2. `## 设计目标`
3. `## 验收目标`
4. `## Codex 指令`

Use exactly one fenced `markdown` block under `## Codex 指令`. That block must
contain one directly executable Codex Goal. Do not put another fenced block
anywhere in the response.

### 审查结果

Keep this section concise and name:

- response type: `CANDIDATE_REVIEW`, `REVIEW_STATE_VERIFICATION`, or
  `STATE_CHECK`;
- exact review object, such as `base..candidate` or a review-state commit SHA;
- verdict: `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, `BLOCKED`, `VERIFIED`, or
  `NO_NEW_REVIEW`;
- P0/P1/P2 findings or an explicit statement that none were added;
- closure state: whether the authoritative review is recorded and pushed.

Never describe a state check or review-state verification as a new independent
candidate review.

### 设计目标

Use at most three short sentences. State what the single Codex Goal will
accomplish and why it is the next authorized transaction.

This summary is not a separate design-only Gate. Do not create a protocol or
design document unless the research decision genuinely requires one.

### 验收目标

Use at most three short sentences. State the exact diff, tests, evidence, Git
state, and boundary conditions Work will inspect when Codex returns.

This section defines future verification criteria. It is not a second Codex
Goal, an authorization to alter the candidate, or a requirement to record the
verification in another report or commit.

### Codex 指令

Start the instruction block by invoking the installed
`$maintain-codex-handoff` skill. Codex will then reload `AGENTS.md`,
`docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`, the current report, and actual
Git state. Do not duplicate information that Codex can obtain from those
authorities and Git.

Use one compact Goal containing only:

- `Goal`
- expected branch and base or reviewed candidate SHA;
- authoritative file and report pointers, with relevant section names;
- exact allowed diff;
- task-specific changes or finding IDs not already defined by those sources;
- material prohibited boundaries;
- required validation commands;
- commit, push, return, and stop conditions.

Do not repeat stable repository rules, protocol or formula text, complete test
matrices, complete findings already stored in a report, full project history,
all known blob hashes, generic safety rules, or an exhaustive final-response
template. Reference the checked-in path and relevant section instead. Repeat
only identities or frozen payloads that cannot be recovered unambiguously from
the expected base and authority files and are material to correctness.

Keep the instruction block as short as correctness allows; there is no fixed
character limit. Framework-scale or cross-module Goals may include necessary
task-specific interface, migration, integration, and fail-closed detail.
Length is justified only by material content that cannot be recovered
unambiguously from repository authority, or by an exact user-supplied frozen
payload such as a not-yet-recorded external review. Repository repetition and
general complexity are not justification. When a Goal becomes unusually long,
prefer moving durable detail into an authorized protocol or report and
referencing it.

Do not combine two transactions in one instruction block.

## Closure State Machine

### Candidate review completed but not recorded

- Report `CANDIDATE_REVIEW`.
- This rule has precedence for every completed verdict, including `REJECT` and
  `BLOCKED`.
- The only Codex Goal is a governance-docs-only review-state recording.
- Do not include the next research, design, implementation, or experiment Goal.

### Review-state commit verified

- Report `REVIEW_STATE_VERIFICATION` with `VERIFIED`.
- Verification closes the existing review transaction and creates no new
  review report, `record-review` operation, or acceptance commit.
- For `ACCEPT` or `ACCEPT_WITH_P2`, the single Codex Goal may now be the next
  authorized candidate transaction.

### Candidate rejected or evidence blocked

- Apply this branch only after the `REJECT` or `BLOCKED` review-state commit has
  been recorded, pushed, and verified.
- The single Codex Goal may only remediate the findings or collect the missing
  evidence.
- Do not advance the Gate or issue unrelated work.

### No new review event

- Report `STATE_CHECK` with `NO_NEW_REVIEW`.
- Issue one next Goal only when Git and the three authorities agree on that
  action.

## Non-Negotiable Boundaries

- One Work response contains at most one Codex Goal.
- Never combine review-state recording with the next candidate.
- Never record the mechanical verification of a review-state commit as another
  independent review.
- Never invent acceptance from a chat summary or from Codex self-report.
- Never use long runs of `=`, repeated protocol boilerplate, or multiple
  copy-paste blocks as visual separators.
- If repository facts conflict, report `BLOCKED`; the instruction block may
  contain only a bounded reconciliation or evidence-gathering Goal.

## Output Skeleton

The following is structural guidance. Replace every placeholder and keep the
final response to one fenced block total.

    ## 审查结果
    - 类型：`<response type>`
    - 对象：`<exact SHA or range>`
    - 结论：`<verdict>`
    - Findings：<P0/P1/P2 summary>
    - 闭环状态：<recorded and pushed, or pending>

    ## 设计目标
    <No more than three short sentences.>

    ## 验收目标
    <No more than three short sentences.>

    ## Codex 指令
    ```markdown
    Goal
    ...
    ```
