# Candidate and Formal Review

## Natural implementation candidate

Before new code becomes a stable dependency, push one natural candidate batch
to `main`. Browser Work reviews exact base/candidate SHAs, the actual diff,
tests, and relevant results. It may issue repairs or the next Goal without a
formal verdict, report, `record-review`, or `CURRENT_STAGE.md` update.

## Formal promotion

Use exactly one qualified independent review only to accept a major
implementation baseline, freeze a publication evaluation, adopt a key result,
change the core method, or raise a claim. Browser Work is preferred when it can
inspect the exact GitHub range and evidence. Use `research-reviewer` only when
no qualifying Work review exists, evidence conflicts, or the user requests a
second opinion.

Formal verdicts are `ACCEPT`, `ACCEPT_WITH_P2`, `REJECT`, and `BLOCKED`. P0/P1
requires `REJECT`; P2 is non-blocking; `BLOCKED` means required evidence or
environment is unavailable.

Record the review once:

1. commit and push the candidate;
2. write the detailed independent report;
3. run `record-review` and `audit`;
4. commit and push one governance-docs-only review-state change.

Accepted implementation candidates update accepted code. Accepted docs-only
candidates preserve it. Rejected, blocked, and review-state commits never
replace accepted code. Mechanical verification creates no second review or
commit and may be followed by the next Goal.
