# Research Artifact Cleanup Integration

In a governed project, invoke `$codex-research-workflow` and
`$research-artifact-cleanup` together. Workflow owns scientific meaning,
authority, Git-tracked reference changes, and the final commit/push. Cleanup
owns metadata inventory, classification inputs, state-bound plans, physical
moves/deletions, and execution verification.

Trigger a read-only plan after a committed `PROJECT_CORE.md` change that:

- replaces or terminates the primary direction;
- marks a direction retired, rejected, or superseded; or
- changes core components so prior runs no longer match the method.

Do not trigger for wording, citations, evidence additions, or claim narrowing.
The direction commit comes first. Generate a plan bound to that commit in the
same Goal, present the Cleanup Plan Review, and stop for user approval.

Cleanup execution is normally non-blocking for later research. It blocks only
when storage exhaustion, path collision, or contamination risk prevents safe
new work. New persistent artifacts must use the current experiment root even
when old cleanup is deferred.

For relocation, Cleanup handles physical paths; Workflow updates tracked
scripts, configs, registry, and report references and validates the resulting
diff. Put irreversible deletion last. Commit/push only after the approved scope
passes Cleanup Execution Verification. Never modify scientific conclusions or
canonical authorities merely to make an artifact deletable.
