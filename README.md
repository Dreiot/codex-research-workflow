<p align="right">
  <strong>English</strong> · <a href="./README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="Codex Research Handoff separates stable rules, durable research strategy, and volatile gate state into three auditable authorities.">
</p>

Long-running research agents drift when operating rules, scientific direction,
and the current implementation Gate live only in conversation history. **Codex
Research Handoff** turns those layers into explicit repository authorities,
validates them against Git, and reloads them after resume or automatic context
compaction.

It is a Codex Skill for research software, paper pipelines, evidence-gated
experiments, and any repository where a plausible summary is not enough.

## The three-authority contract

| Authority | Time scale | Owns | Must not own |
| --- | --- | --- | --- |
| `AGENTS.md` | Stable | Operating rules, permissions, validation, Git, review, and claim boundaries | Current Gate or transient progress |
| `docs/PROJECT_CORE.md` | Durable | Research question, target contribution, innovation hypotheses, component map, explored directions, evidence level, and claim ceiling | Branch, HEAD, current verdict, or next action |
| `docs/CURRENT_STAGE.md` | Volatile | Branch, current Gate, reviewed candidate, verdict, open findings, and one next action | Long-form strategy or project history |

The separation prevents a common failure mode: a stale handoff summary quietly
becoming a second source of truth.

<p align="center">
  <img src="./assets/readme/workflow.svg" width="100%" alt="Continuous empirical iteration with formal review only when promoting work into a research baseline or paper evidence.">
</p>

## What the Skill does

| Command | Result | Writes files? |
| --- | --- | --- |
| `audit` | Validates both JSON envelopes, required sections, report pointers, Git ancestry, project identity, and legacy handoff files | No |
| `initialize` | Creates missing canonical files with conservative, explicitly unaudited placeholders | Yes, missing files only |
| `record-review` | Records an exact candidate SHA, fixed verdict, findings, report path, and next Gate in `CURRENT_STAGE.md` | Yes |
| `resume-prompt` | Produces a compact Codex or browser-review entry prompt that reloads repository truth | No |

The bundled lifecycle Hook injects a compact strategy/Gate summary on startup,
resume, clear, and automatic compaction. Optional reviewer hooks constrain an
explicit `research-reviewer` to read-only review. Routine shell commands and
task completion do not run automatic handoff audits. **Hooks never edit the
repository.**

## Browser Work response contract

The generated Work resume prompt links to the public
[response contract](./skills/maintain-codex-handoff/references/work-response-contract.md).
Work returns a concise review result, design objective, acceptance objective,
and at most one Markdown instruction block containing one Codex Goal. The
contract is an output format, not a mandatory review state machine.
Exploratory implementation and real-data work do not require review-state
commits. A clean mechanical verification may be followed by the next Goal in
the same response. Agents may change the public contract only after explicit
user authorization.

## Install

Install from the repository:

```bash
npx skills add Dreiot/codex-research-handoff
```

Or use Codex's built-in installer explicitly:

```text
Install the Skill from https://github.com/Dreiot/codex-research-handoff,
path skills/maintain-codex-handoff.
```

The installed Skill keeps the invocation name:

```text
$maintain-codex-handoff
```

## First use

On macOS or Linux:

```bash
python3 ~/.codex/skills/maintain-codex-handoff/scripts/handoff.py initialize --repo /path/to/repository
python3 ~/.codex/skills/maintain-codex-handoff/scripts/handoff.py audit --repo /path/to/repository
```

On Windows PowerShell:

```powershell
py -3 "$env:USERPROFILE\.codex\skills\maintain-codex-handoff\scripts\handoff.py" initialize --repo C:\path\to\repository
py -3 "$env:USERPROFILE\.codex\skills\maintain-codex-handoff\scripts\handoff.py" audit --repo C:\path\to\repository
```

`initialize` does not infer scientific truth. It creates an `unaudited`
`PROJECT_CORE.md`; a qualified project owner or reviewer must replace the
placeholders with evidence-backed strategy.

## Add lifecycle Hooks

Use [examples/hooks.template.json](./examples/hooks.template.json) as a merge
template for `~/.codex/hooks.json`. Do not overwrite unrelated existing Hooks.
The Windows command uses `%USERPROFILE%`; replace it with an absolute path if
your Hook runner does not expand environment variables.

The optional [research-reviewer.toml](./examples/research-reviewer.toml) defines
a read-only fallback reviewer. Install it as
`~/.codex/agents/research-reviewer.toml` when browser ChatGPT has not already
provided a qualified independent review.

## Execution and review policy

The default workflow is continuous empirical iteration:

```text
minimal implementation -> real-data run -> metrics -> diagnosis
-> direction adjustment -> paper evidence
```

Ordinary implementation, tests, debugging, data processing, local smoke,
exploratory experiments, parameter adjustment, and metric generation do not
need independent review or review-state recording.

Use one qualified independent review only for an explicit formal promotion:
accepting a major implementation baseline, freezing a publication evaluation,
adopting a key result, changing the core method, or raising a paper claim.

- A browser review qualifies when it is independent of implementation, names
  the exact base and candidate SHAs, inspects the actual diff and evidence, and
  returns P0/P1/P2 findings plus one fixed verdict.
- The `research-reviewer` subagent is a fallback when no qualified browser
  review exists, evidence is incomplete or conflicting, or a second opinion is
  explicitly requested.
- A rejected or blocked formal promotion is recorded before remediation so the
  decision and candidate identity are preserved.
- Mechanical verification creates no second review. When it passes, Work may
  immediately issue the next Goal.

The detailed review report and `CURRENT_STAGE.md` are committed separately from
the implementation candidate, preserving an auditable history:

```text
candidate implementation commit
review-state governance-docs commit
```

New `record-review` inputs should declare `candidate_kind`. Accepted `implementation` candidates
become the new `accepted_code_commit`; accepted `docs_only` candidates preserve
the prior accepted code. Rejected, blocked, and review-state commits never
replace accepted code.

Exploratory smoke is diagnostic evidence, not automatic publication evidence.
Formal runs freeze the data boundary, configuration, metrics, statistical
unit, comparators, stopping conditions, and provenance. The Skill does not add
duplicate execution authorization after that scope is already frozen and
authorized.

## Compaction is not handoff

Automatic context compaction is normal continuity inside one Codex task. It is
not a trigger to stop, force a checkpoint commit, or open a new task. Persist
state when evidence changes an authority; use an explicit handoff only when
opening a new task or browser conversation, after demonstrated context loss, or
at a natural Gate boundary.

## Safety boundaries

- The Skill does not decide scientific claims.
- Hooks warn and inject context; they are not a security sandbox.
- Scripts never auto-commit or auto-push.
- Browser ChatGPT does not load local Hooks, Skills, or memory automatically.
- Private data, large logs, generated artifacts, and secrets do not belong in
  canonical handoff files.
- `CODEX_HANDOFF.md` and `LATEST_STATE.md` are treated as legacy dynamic-state
  files because they can create competing authorities.

## Repository layout

```text
skills/maintain-codex-handoff/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── current-stage-schema.md
│   ├── project-core-schema.md
│   └── work-response-contract.md
└── scripts/
    ├── handoff.py
    └── hook.py

examples/
├── hooks.template.json
└── research-reviewer.toml
```

## Validate the package

```bash
python -m unittest discover -s tests -v
python -m py_compile skills/maintain-codex-handoff/scripts/handoff.py skills/maintain-codex-handoff/scripts/hook.py
```

The test suite creates temporary Git repositories and checks initialization,
idempotence, schema auditing, prompt generation, migration behavior, and
read-only Hook execution.

## License

[MIT](./LICENSE)
