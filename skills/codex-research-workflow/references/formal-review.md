# Optional Implementation Inspection and Formal Promotion

## Optional implementation inspection

Routine exploratory code continues after task-relevant tests, and its
decision-complete Codex result packet normally supports the next controller
decision. Request an inspection only when tests and results cannot establish
the required correctness or the exact diff is needed to interpret evidence.
The reviewer may inspect uncommitted work. Commit and push only when the
reviewer needs GitHub access or the work is entering formal promotion. The
inspection may guide repair or the next Goal without a formal verdict, report,
`record-review`, review-state commit, or `CURRENT_STAGE.md` update.

## Formal promotion

Use exactly one qualified independent review only when formally adopting a
major implementation baseline, a stable publication-evaluation protocol, a key
result, a core-method change, or a higher claim. Formal promotion is not a
prerequisite for exploratory or publication-oriented experiment execution.
The review must be independent of the Codex executor and candidate production;
it does not require a particular model tier. Select a controller or reviewer by
actual access to the exact GitHub range and evidence, not by model label or
surface. A Chat or Work controller with that access may perform the single
qualified review and continue. If direct access is unavailable, request one
bounded verification packet from a capable reviewer. Use a configured read-only
reviewer agent only when no qualifying external review exists, evidence
conflicts, or the user requests a second opinion.

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
