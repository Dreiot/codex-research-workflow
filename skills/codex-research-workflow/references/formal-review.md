# Optional Implementation Inspection and Formal Promotion

## Optional implementation inspection

Routine exploratory code continues after task-relevant tests, and its Codex
result packet normally supports the next controller decision. Request an
inspection only when tests and results cannot establish the required
correctness or the exact diff is needed to interpret evidence. The reviewer may
inspect uncommitted work. Commit and push only when the reviewer needs GitHub
access or the work is entering formal promotion. The inspection may guide repair
or the next Goal without a formal verdict, report, `record-review`, review-state
commit, or `CURRENT_STAGE.md` update.

## Formal promotion

Use exactly one qualified independent review only when formally adopting a
major implementation baseline, a stable publication-evaluation protocol, a key
result, a core-method change, or a higher claim. Formal promotion is not a
prerequisite for exploratory or publication-oriented experiment execution.
Prefer a reviewer with direct access to the exact GitHub range and evidence. In
Chat, this is normally Extra High; in Work, it is Work. Use a configured
read-only reviewer agent only when no qualifying external review exists,
evidence conflicts, or the user requests a second opinion.

Formal verdicts are `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, and `BLOCKED`. P0/P1
requires `REJECT`; P2 is non-blocking; `BLOCKED` means required evidence or
environment is unavailable.

Keep the promotion transaction minimal:

1. if the implementation or results are not already committed, commit and push
   one natural candidate batch;
2. review that exact candidate once;
3. run `record-review` and `audit`, using `review_report: null` unless material
   findings need a separate durable report;
4. commit and push one necessary authority update. Change `PROJECT_CORE.md` only
   when durable strategy or claim content actually changes.

Accepted implementation candidates update accepted code. Accepted docs-only
candidates preserve it. Rejected, blocked, and review-state commits never
replace accepted code. Mechanical verification creates no second review or
commit and may be followed by the next Goal. Do not create another commit merely
to verify the authority update.
