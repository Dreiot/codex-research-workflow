<p align="right"><strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a></p>

<p align="center"><img src="./assets/readme/hero.svg" width="100%" alt="Codex Research Workflow"></p>

# Codex Research Workflow

Two compact, progressive-disclosure Codex Skills for governed research repositories:

- `$codex-research-workflow` keeps execution, Git identity, research strategy, current state, experiments, evidence, reviews, and handoffs coherent.
- `$research-artifact-cleanup` inventories and removes obsolete artifacts only through an explicit, user-approved, state-bound plan.

The workflow is empirical by default: minimal implementation → real-data run → metrics → diagnosis → direction adjustment → paper evidence. Ordinary smoke tests and exploratory runs do not become formal review Gates.

## Canonical authority

| File | Role |
|---|---|
| `AGENTS.md` | Stable repository rules and experiment-root policy |
| `docs/PROJECT_CORE.md` | Compact durable strategy and one synthesized record per past direction |
| `docs/CURRENT_STAGE.md` | Current Gate, accepted identity, findings, and next action only |

The internal markers `codex-project-core` and `codex-handoff-state` remain compatible with existing governed projects. Chat summaries never replace repository authority.

## Workflow commands

```text
workflow.py init                 # plan by default; --apply requires the exact plan ID
workflow.py migrate              # add the new structure without moving old artifacts
workflow.py audit
workflow.py prepare-experiment   # create an ignored run manifest only when needed
workflow.py prepare-evidence     # create a tracked evidence candidate only when needed
workflow.py validate-evidence
workflow.py record-review
workflow.py resume-prompt
```

`initialize` remains an undocumented compatibility alias for legacy automation.

New-project `init` checks the exact directory, nested Git state, upload candidates, sensitive/oversized files, origin history, GitHub owner/name/visibility, and an empty remote. It uses `main`, never creates branch variants, and refuses overwrite or force-push.

Existing-project `migrate` is also plan/apply. It adds only missing authority/policy files and generated-artifact ignore rules; it does not migrate artifacts, compact documents, or change scientific content.

## Experiment artifacts

The default root is `experiments/`; `AGENTS.md` may declare another repository-relative root. Directories are created on demand.

```text
experiments/
├── scripts/       tracked experiment entrypoints
├── configs/       tracked configurations
├── registry/      tracked compact registries and important cleanup records
├── evidence/      tracked decision candidates for Work review
├── runs/          ignored generated run outputs
├── .tmp/          ignored disposable files and cleanup plans
└── quarantine/    ignored artifacts awaiting a decision
```

Core method code stays in `src/` or the repository's existing code area. Raw and external datasets stay outside the experiment root.

Exploratory output in a Codex response is sufficient for another reversible exploration. Before Work adopts a result, changes the method/direction/baseline/data split/metric/claim from it, or promotes it to formal evidence, create `experiments/evidence/<experiment-id>/<candidate-id>/` with `manifest.json`, `analysis_report.md`, and `metrics.json` only when numerical metrics exist.

## Cleanup transaction

Cleanup uses exactly six classifications: `keep_formal_evidence`, `keep_negative_evidence`, `keep_active`, `delete_reproducible`, `delete_technical_failure`, and `unknown`. Unknown items are never deleted.

After a committed `PROJECT_CORE.md` change that actually retires, rejects, supersedes, or makes a primary direction obsolete, the Workflow may invoke Cleanup to produce a read-only plan. The Goal then stops. Relocation or deletion requires the user to approve the numbered scope and exact `plan_id`.

The detailed JSON plan is ignored. Important verified cleanups create `experiments/registry/cleanup/<cleanup-id>.json`. Current-run files explicitly marked temporary may be removed by the Workflow after a successful run without a historical cleanup transaction.

## Browser Work contract

Every actionable Work Goal explicitly invokes `$codex-research-workflow`; cleanup Goals invoke both Skills. The public [Work Response Contract](./skills/codex-research-workflow/references/work-response-contract.md) preserves the existing four-section response format and review boundaries. The contract is an output protocol, not a mandatory state machine.

## Install

```bash
npx skills add Dreiot/codex-research-workflow
```

Install both paths:

```text
skills/codex-research-workflow
skills/research-artifact-cleanup
```

Example on Windows:

```powershell
py -3 "$env:USERPROFILE\.codex\skills\codex-research-workflow\scripts\workflow.py" audit --repo C:\path\to\repository
```

The optional fail-open lifecycle Hook injects only a compact authority/Gate pointer. Explicit `audit` remains fail-closed. Reviewer hooks retain the formal-review boundary.

## Validate

```bash
python -m py_compile skills/codex-research-workflow/scripts/workflow.py skills/codex-research-workflow/scripts/hook.py skills/research-artifact-cleanup/scripts/cleanup.py
python -m unittest discover -s tests -v
```

Licensed under Apache-2.0.
