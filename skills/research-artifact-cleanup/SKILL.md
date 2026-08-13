---
name: research-artifact-cleanup
description: Plan and apply user-approved cleanup across the exact single-root research project, including ignored obsolete runs, technical failures, duplicate reproducible outputs, and retired-direction artifacts. Use after a committed PROJECT_CORE direction retirement or for an explicit project cleanup request. Integrates with Codex Research Workflow, preserves formal and negative evidence, and never deletes from an unapproved inventory.
---

# Research Artifact Cleanup

Clean historical research artifacts without weakening the evidence available to Browser Work or changing scientific authority by inference.

## Required Boundary

- Use together with `$codex-research-workflow` for governed repositories.
- Require the Codex-opened project root to equal the exact Git root. `--repo`
  names this one root; never clean a parent workspace or an outside sibling.
- This Skill cleans existing artifacts. It does not create experiments, choose a research direction, compact authority documents, or judge scientific sufficiency.
- Treat `AGENTS.md`, `docs/PROJECT_CORE.md`, `docs/CURRENT_STAGE.md`, Git, current reports, and approved evidence packets as authority.
- Never inspect raw/external datasets merely to classify storage.
- Never apply deletion from prose approval alone. Apply only an unchanged machine plan whose `plan_id` the user approved.

## Workflow

1. Audit the project with Codex Research Workflow and require one clean, exact project/Git root.
2. Read [classification-policy.md](references/classification-policy.md), inventory the entire project root plus Git references, then prepare a decisions JSON.
3. Run `cleanup.py plan`. Present its plan identity, totals, experiment-level table, and numbered approval scope. Stop for user approval.
4. After explicit approval, run `apply --phase relocate` first when migration is required. Update and validate references before deletion.
5. Run `apply --phase delete` with the same `plan_id`. Unknown, active, formal-evidence, and negative-evidence items remain non-deletable.
6. Run `apply --phase verify`. Important cleanups create a compact tracked record; the ignored detailed plan is removed only after verification succeeds.
7. Let `$codex-research-workflow` audit and commit any tracked relocation, reference, or registry changes.

Read [workflow-integration.md](references/workflow-integration.md) when cleanup follows a `PROJECT_CORE.md` direction change.

## Commands

```powershell
py scripts/cleanup.py plan --repo C:\project --decisions decisions.json
py scripts/cleanup.py apply --repo C:\project --plan experiments/.tmp/cleanup/cleanup-....json --plan-id cleanup-... --phase relocate
py scripts/cleanup.py apply --repo C:\project --plan experiments/.tmp/cleanup/cleanup-....json --plan-id cleanup-... --phase delete
py scripts/cleanup.py apply --repo C:\project --plan experiments/.tmp/cleanup/cleanup-....json --plan-id cleanup-... --phase verify
```

Any precondition failure stops the current phase. Do not claim rollback; report the completed operations and unresolved remainder exactly.
