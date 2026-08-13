# Workflow Integration

Cleanup is triggered only after a committed `PROJECT_CORE.md` change that replaces or terminates the primary direction, rejects or supersedes a durable direction, or makes old runs obsolete through a core-component change. Wording, citation, evidence-level, and claim-narrowing edits do not automatically trigger cleanup.

The same Codex Goal may commit the direction decision and produce a read-only cleanup plan, but it must stop before relocation or deletion. The Browser Work response should summarize:

1. plan ID, Git HEAD, and `PROJECT_CORE.md` base commit;
2. counts and bytes by the six classifications;
3. one row per experiment or candidate group, including references and proposed action;
4. numbered approval scopes, clearly separating relocation from deletion;
5. materials retained for subsequent Work review.

The detailed plan stays under the ignored experiment temporary area. Important cleanup transactions create `experiments/registry/cleanup/<cleanup-id>.json` (or the configured experiment root) after verification. Ordinary deletion of current-run temporary files is handled by Codex Research Workflow and does not create a cleanup record.
