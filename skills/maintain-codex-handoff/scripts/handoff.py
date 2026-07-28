#!/usr/bin/env python3
"""Deterministic helpers for canonical research-project handoffs."""

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CORE_REL = Path("docs/PROJECT_CORE.md")
CORE_START = "<!-- codex-project-core"
STATE_REL = Path("docs/CURRENT_STAGE.md")
STATE_START = "<!-- codex-handoff-state"
ENVELOPE_END = "-->"
REVIEW_VERDICTS = {"ACCEPT", "ACCEPT_WITH_P2", "REJECT", "BLOCKED"}
STATE_VERDICTS = REVIEW_VERDICTS | {"NO_REVIEW"}
CANDIDATE_KINDS = {"implementation", "docs_only"}
STRATEGIC_STATUSES = {"unaudited", "active", "paused", "redirected", "completed"}
WORK_CONTRACT_URL = (
    "https://github.com/Dreiot/codex-research-handoff/blob/main/"
    "skills/maintain-codex-handoff/references/work-response-contract.md"
)
STATE_REQUIRED_FIELDS = (
    "schema_version",
    "project",
    "branch",
    "research_phase",
    "current_gate",
    "last_reviewed_candidate",
    "accepted_code_commit",
    "review_verdict",
    "review_report",
    "open_findings",
    "next_gate",
    "next_action",
    "updated_at",
)
CORE_REQUIRED_FIELDS = (
    "schema_version",
    "project",
    "research_question",
    "target_outcome",
    "primary_direction",
    "primary_innovations",
    "core_components",
    "evidence_level",
    "strategic_status",
    "last_strategic_review",
    "updated_at",
)
CORE_REQUIRED_HEADINGS = (
    "## Research Objective",
    "## Core Direction",
    "## Innovation Hypotheses",
    "## Component Map",
    "## Explored Directions",
    "## Evidence and Claim Position",
    "## Scientific Boundaries",
    "## Open Strategic Questions",
    "## Strategic Roadmap",
    "## Canonical Sources",
    "## Update Rules",
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NON_BLOCKING_LANGUAGE_RE = re.compile(
    r"\b(?:non[- ]blocking|not\s+blocking|does\s+not\s+block)\b",
    flags=re.IGNORECASE,
)
BLOCKING_LANGUAGE_RE = re.compile(
    r"\b(?:blocking|blocker|blocks|blocked|"
    r"must\s+(?:be\s+)?(?:fixed|closed|resolved)\s+(?:before|prior\s+to)|"
    r"prevents?\s+(?:acceptance|promotion))\b|阻塞",
    flags=re.IGNORECASE,
)


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def find_repo(start: Path) -> Optional[Path]:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve()


def read_envelope(path: Path, marker: str, label: str) -> Tuple[Optional[Dict[str, Any]], List[str], str]:
    if not path.is_file():
        return None, [f"missing {path.name}"], ""
    text = path.read_text(encoding="utf-8")
    start = text.find(marker)
    end = text.find(ENVELOPE_END, start + len(marker)) if start >= 0 else -1
    if start < 0 or end < 0:
        return None, [f"missing {label} JSON envelope"], text
    raw = text[start + len(marker) : end].strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, [f"invalid {label} JSON: {exc}"], text
    if not isinstance(value, dict):
        return None, [f"{label} JSON must be an object"], text
    return value, [], text


def validate_timestamp(value: Any, field: str) -> List[str]:
    try:
        parsed = dt.datetime.fromisoformat(value) if isinstance(value, str) else None
        if parsed is None or parsed.tzinfo is None:
            raise ValueError
    except ValueError:
        return [f"{field} must be timezone-aware ISO 8601"]
    return []


def validate_relative_report(repo: Path, value: Any, field: str) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, str) or not value.strip():
        return [f"{field} must be a path or null"]
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return [f"{field} must be repository-relative"]
    if not (repo / path).is_file():
        return [f"{field} does not exist: {value}"]
    return []


def read_state(repo: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    path = repo / STATE_REL
    state, errors, _ = read_envelope(path, STATE_START, "codex-handoff-state")
    if state is None:
        if errors == [f"missing {path.name}"]:
            errors = [f"missing {STATE_REL.as_posix()}"]
        return None, errors
    return state, errors + validate_state(repo, state)


def validate_review_semantics(
    verdict: Any, findings: Any, *, require_explicit_labels: bool = False
) -> List[str]:
    if verdict == "NO_REVIEW":
        return []
    if verdict not in REVIEW_VERDICTS or not isinstance(findings, list):
        return []

    errors: List[str] = []
    severities: List[Optional[str]] = []
    for finding in findings:
        match = (
            re.match(r"^\s*(P[012])\b", finding, flags=re.IGNORECASE)
            if isinstance(finding, str)
            else None
        )
        severities.append(match.group(1).upper() if match else None)

    if verdict == "ACCEPT" and findings:
        errors.append("ACCEPT requires no open findings")
    if verdict == "ACCEPT_WITH_P2":
        invalid_severity = (
            any(item != "P2" for item in severities)
            if require_explicit_labels
            else any(item in {"P0", "P1"} for item in severities)
        )
        if not findings or invalid_severity:
            errors.append("ACCEPT_WITH_P2 requires one or more P2-only findings")
        elif any(
            BLOCKING_LANGUAGE_RE.search(NON_BLOCKING_LANGUAGE_RE.sub("", item))
            for item in findings
        ):
            errors.append("P2 findings are non-blocking and must not use blocking language")
    if verdict != "REJECT" and any(item in {"P0", "P1"} for item in severities):
        errors.append("P0 or P1 findings require REJECT")
    if verdict == "REJECT" and (
        not findings
        or (
            require_explicit_labels
            and not any(item in {"P0", "P1"} for item in severities)
        )
    ):
        errors.append("REJECT requires at least one P0 or P1 finding")
    if verdict == "BLOCKED" and (
        not findings
        or (
            require_explicit_labels
            and not all(
                isinstance(item, str)
                and re.match(r"^\s*BLOCKED\s*:", item, flags=re.IGNORECASE)
                for item in findings
            )
        )
    ):
        errors.append("BLOCKED requires one or more BLOCKED: evidence or environment findings")
    return errors


def validate_state(repo: Path, state: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    missing = [key for key in STATE_REQUIRED_FIELDS if key not in state]
    extra = sorted(set(state) - set(STATE_REQUIRED_FIELDS))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if extra:
        errors.append("unexpected fields: " + ", ".join(extra))
    if state.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if state.get("review_verdict") not in STATE_VERDICTS:
        errors.append("invalid review_verdict")
    if not isinstance(state.get("open_findings"), list) or not all(
        isinstance(item, str) and item.strip() for item in state.get("open_findings", [])
    ):
        errors.append("open_findings must be an array of non-empty strings")
    else:
        errors.extend(
            validate_review_semantics(state.get("review_verdict"), state.get("open_findings"))
        )
    for key in ("project", "branch", "research_phase", "current_gate", "next_gate", "next_action"):
        if not isinstance(state.get(key), str) or not state.get(key, "").strip():
            errors.append(f"{key} must be a non-empty string")
    for key in ("last_reviewed_candidate", "accepted_code_commit"):
        value = state.get(key)
        if value is not None and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            errors.append(f"{key} must be a full lowercase SHA or null")
    errors.extend(validate_relative_report(repo, state.get("review_report"), "review_report"))
    errors.extend(validate_timestamp(state.get("updated_at"), "updated_at"))
    return errors


def read_core(repo: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    path = repo / CORE_REL
    core, errors, text = read_envelope(path, CORE_START, "codex-project-core")
    if core is None:
        if errors == [f"missing {path.name}"]:
            errors = [f"missing {CORE_REL.as_posix()}"]
        return None, errors
    errors.extend(validate_core(repo, core))
    lines = {line.strip() for line in text.splitlines()}
    missing_headings = [heading for heading in CORE_REQUIRED_HEADINGS if heading not in lines]
    if missing_headings:
        errors.append("missing PROJECT_CORE sections: " + ", ".join(missing_headings))
    return core, errors


def validate_core(repo: Path, core: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    missing = [key for key in CORE_REQUIRED_FIELDS if key not in core]
    extra = sorted(set(core) - set(CORE_REQUIRED_FIELDS))
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if extra:
        errors.append("unexpected fields: " + ", ".join(extra))
    if core.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for key in (
        "project",
        "research_question",
        "target_outcome",
        "primary_direction",
        "evidence_level",
    ):
        if not isinstance(core.get(key), str) or not core.get(key, "").strip():
            errors.append(f"{key} must be a non-empty string")
    for key in ("primary_innovations", "core_components"):
        value = core.get(key)
        if not isinstance(value, list) or not value or not all(
            isinstance(item, str) and item.strip() for item in value
        ):
            errors.append(f"{key} must be a non-empty array of non-empty strings")
    if core.get("strategic_status") not in STRATEGIC_STATUSES:
        errors.append("invalid strategic_status")
    errors.extend(
        validate_relative_report(repo, core.get("last_strategic_review"), "last_strategic_review")
    )
    errors.extend(validate_timestamp(core.get("updated_at"), "updated_at"))
    return errors


def render_state(state: Dict[str, Any]) -> str:
    findings = state["open_findings"] or ["None recorded."]
    finding_lines = "\n".join(f"- {item}" for item in findings)
    report = state["review_report"] or "Not recorded."
    reviewed = state["last_reviewed_candidate"] or "Not recorded."
    accepted = state["accepted_code_commit"] or "Not recorded."
    payload = json.dumps(state, ensure_ascii=False, indent=2)
    return (
        "# Current Stage\n\n"
        f"{STATE_START}\n{payload}\n{ENVELOPE_END}\n\n"
        "This file is the canonical volatile handoff state. Verify all SHAs against Git; "
        "the JSON block never records the commit that contains this file.\n\n"
        "## Current Gate\n\n"
        f"- Research phase: `{state['research_phase']}`\n"
        f"- Gate: `{state['current_gate']}`\n"
        f"- Verdict: `{state['review_verdict']}`\n"
        f"- Last reviewed candidate: `{reviewed}`\n"
        f"- Accepted code commit: `{accepted}`\n"
        f"- Review report: `{report}`\n\n"
        "## Open Findings\n\n"
        f"{finding_lines}\n\n"
        "## Next Action\n\n"
        f"- Next gate: `{state['next_gate']}`\n"
        f"- Action: {state['next_action']}\n\n"
        "## Resume Rule\n\n"
        "Read `AGENTS.md`, `docs/PROJECT_CORE.md`, and this file; fetch the configured remote, "
        "verify the branch and actual HEAD, then compare Git history with this state before editing. "
        "Stop and report any mismatch.\n"
    )


def render_core(core: Dict[str, Any]) -> str:
    innovations = "\n".join(f"- {item}" for item in core["primary_innovations"])
    components = "\n".join(f"- {item}" for item in core["core_components"])
    review = core["last_strategic_review"] or "Not recorded."
    payload = json.dumps(core, ensure_ascii=False, indent=2)
    return (
        "# Project Core\n\n"
        f"{CORE_START}\n{payload}\n{ENVELOPE_END}\n\n"
        "This file is the canonical durable research-strategy record. It does not contain "
        "the current branch, HEAD, Gate, verdict, or next action.\n\n"
        "## Research Objective\n\n"
        f"- Research question: {core['research_question']}\n"
        f"- Target outcome: {core['target_outcome']}\n"
        "- Evaluation object and intended scope: Not yet audited.\n\n"
        "## Core Direction\n\n"
        f"{core['primary_direction']}\n\n"
        "## Innovation Hypotheses\n\n"
        f"{innovations}\n\n"
        "For each hypothesis, record novelty relative to baselines, expected mechanism, "
        "maturity, and evidence links.\n\n"
        "## Component Map\n\n"
        f"{components}\n\n"
        "| Component | Scientific role | Implementation | Interfaces / dependencies | Maturity | Evidence |\n"
        "|---|---|---|---|---|---|\n"
        "| Not yet audited | Not yet audited | Not yet audited | Not yet audited | unaudited | None |\n\n"
        "## Explored Directions\n\n"
        "| Direction | Status | Decision and reason | Reusable residue | Evidence |\n"
        "|---|---|---|---|---|\n"
        "| Not yet audited | deferred | Project history has not yet been synthesized. | Unknown | None |\n\n"
        "Use `active`, `supported`, `rejected`, `deferred`, or `superseded`. Preserve negative results.\n\n"
        "## Evidence and Claim Position\n\n"
        f"- Evidence level: `{core['evidence_level']}`\n"
        "- Validated facts: Not yet audited.\n"
        "- Current claim ceiling: No project-specific claim established by this placeholder.\n"
        "- Missing evidence: A strategic evidence audit is required.\n\n"
        "## Scientific Boundaries\n\n"
        "Document data/provenance, mathematical, experimental, compute, and publication boundaries.\n\n"
        "## Open Strategic Questions\n\n"
        "- Which hypotheses and components are supported by repository evidence?\n"
        "- What explicit evidence would accept, redirect, or reject each open direction?\n\n"
        "## Strategic Roadmap\n\n"
        "Record dependency order and long-horizon milestones here, not the current Gate.\n\n"
        "## Canonical Sources\n\n"
        f"- Last strategic review: `{review}`\n"
        "- Specifications, implementation entry points, protocols, reports, experiment registries, "
        "and paper sections: Not yet indexed.\n\n"
        "## Update Rules\n\n"
        "Update after a strategic decision, architecture change, material evidence change, or explicit "
        "core audit. Preserve rejected and superseded directions. Link detailed evidence instead of "
        "copying it. Never record branch, HEAD, current Gate, verdict, or next action here; keep volatile "
        "state in `docs/CURRENT_STAGE.md`.\n"
    )


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().replace(microsecond=0).isoformat()


def commit_exists(repo: Path, sha: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def is_ancestor(repo: Path, sha: str, head: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", sha, head],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def audit(repo: Path) -> Dict[str, Any]:
    state, state_errors = read_state(repo)
    errors = list(state_errors)
    warnings: List[str] = []
    agents_path = repo / "AGENTS.md"
    agents_text = agents_path.read_text(encoding="utf-8") if agents_path.is_file() else ""
    if not agents_path.is_file():
        errors.append("missing AGENTS.md")

    core_path = repo / CORE_REL
    core, core_errors = read_core(repo)
    if not core_path.is_file():
        migration_message = f"missing {CORE_REL.as_posix()}; run initialize and complete a strategic audit"
        if CORE_REL.as_posix() in agents_text:
            errors.append(migration_message)
        else:
            warnings.append(migration_message)
    else:
        errors.extend(f"PROJECT_CORE: {item}" for item in core_errors)
        if core and core.get("strategic_status") == "unaudited":
            warnings.append("PROJECT_CORE is an unaudited migration placeholder")
        if CORE_REL.as_posix() not in agents_text:
            warnings.append("AGENTS.md does not name docs/PROJECT_CORE.md as the strategic authority")

    branch = git(repo, "branch", "--show-current")
    head = git(repo, "rev-parse", "HEAD")
    status = git(repo, "status", "--short", "--untracked-files=all")
    if state:
        if state.get("branch") != branch:
            errors.append(f"state branch {state.get('branch')!r} != Git branch {branch!r}")
        for key in ("last_reviewed_candidate", "accepted_code_commit"):
            sha = state.get(key)
            if sha and not commit_exists(repo, sha):
                errors.append(f"{key} is not available in Git: {sha}")
            elif sha and not is_ancestor(repo, sha, head):
                errors.append(f"{key} is not an ancestor of HEAD: {sha}")
    if state and core and state.get("project") != core.get("project"):
        errors.append(
            f"PROJECT_CORE project {core.get('project')!r} != CURRENT_STAGE project {state.get('project')!r}"
        )

    legacy = []
    for rel in (
        Path("CODEX_HANDOFF.md"),
        Path("LATEST_STATE.md"),
        Path("docs/CODEX_HANDOFF.md"),
        Path("docs/LATEST_STATE.md"),
    ):
        if (repo / rel).exists():
            legacy.append(rel.as_posix())
    if legacy:
        warnings.append("legacy handoff files present: " + ", ".join(legacy))

    state_commit = git(repo, "log", "-1", "--format=%H", "--", STATE_REL.as_posix(), check=False)
    core_commit = git(repo, "log", "-1", "--format=%H", "--", CORE_REL.as_posix(), check=False)
    head_newer_than_state = bool(state_commit and state_commit != head)
    return {
        "repo": str(repo),
        "branch": branch,
        "head": head,
        "state_commit": state_commit or None,
        "core_commit": core_commit or None,
        "head_newer_than_state": head_newer_than_state,
        "worktree_clean": not bool(status),
        "errors": errors,
        "warnings": warnings,
        "core": core,
        "state": state,
    }


def command_audit(args: argparse.Namespace) -> int:
    repo = find_repo(Path(args.repo).resolve())
    if not repo:
        print("not a Git repository", file=sys.stderr)
        return 2
    result = audit(repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"repo: {result['repo']}")
        print(f"branch: {result['branch']}")
        print(f"HEAD: {result['head']}")
        print(f"worktree_clean: {result['worktree_clean']}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 1 if result["errors"] else 0


def command_initialize(args: argparse.Namespace) -> int:
    repo = find_repo(Path(args.repo).resolve())
    if not repo:
        print("not a Git repository", file=sys.stderr)
        return 2
    agents = repo / "AGENTS.md"
    if not agents.exists():
        agents.write_text(
            "# Project Agent Rules\n\n"
            "## Authority\n\n"
            "- Read `docs/PROJECT_CORE.md` for durable research strategy and "
            "`docs/CURRENT_STAGE.md` for the volatile Gate, review state, findings, and next "
            "action. Treat Git and checked-in evidence as authoritative.\n"
            "- Do not create a second dynamic state file. Keep branch, HEAD, Gate, verdict, "
            "and next action out of `PROJECT_CORE.md`.\n\n"
             "## Execution\n\n"
             "- Verify the Git identity needed by the current Goal. Resolve material conflicts "
             "between Git, project strategy, and current state before relying on them.\n"
             "- Default to the shortest empirical loop: minimal implementation, real-data run, "
             "metrics, diagnosis, direction adjustment, and paper evidence. Keep naturally "
             "coupled implementation, critical tests, and bounded exploratory runs together.\n"
             "- Local, recoverable, no-cost work using project-authorized data is allowed by "
             "default. Ask before paid, sensitive, external side-effecting, destructive, or "
             "irreversible actions; do not request duplicate permission for an already authorized "
             "and frozen run.\n"
             "- Use the simplest correct, testable implementation. Do not add speculative "
             "abstractions, broad refactors, defensive infrastructure, exhaustive validation, "
             "or design-only Gates unless they directly block the current research decision.\n"
             "- Stop when acceptance criteria pass or metrics are sufficient to choose the next "
             "direction. Record unrelated issues without investigating them.\n"
             "- Preserve data integrity, statistical validity, fair comparison, reproducibility, "
             "material failure handling, negative results, and honest claim boundaries.\n\n"
             "## Review And State\n\n"
             "- Exploratory implementation, tests, smoke, debugging, parameter adjustment, and "
             "metric generation do not require independent review or review-state commits.\n"
             "- Require one qualified independent review only for an explicit formal promotion: "
             "accepting a major implementation baseline, freezing a publication evaluation, "
             "adopting a key result, changing the core method, or raising a paper claim.\n"
             "- Do not duplicate a qualifying Browser Work review with a Codex reviewer. Record "
             "a rejected or blocked formal promotion before remediation; mechanical verification "
             "creates no new review and may be followed immediately by the next Goal.\n"
             "- Update `docs/CURRENT_STAGE.md` only after a material milestone, formal review, "
             "material blocker, or next-action change. Ordinary commits do not imply pending "
             "review closure. Update `docs/PROJECT_CORE.md` only after a durable strategic, "
             "innovation, component, evidence, or claim-boundary change.\n"
             "- Browser Work responses must follow the public Work Response Contract: exactly "
             "`审查结果`, `设计目标`, `验收目标`, and `Codex 指令`, with one fenced "
             "Markdown block containing at most one Codex Goal. A clean review-state verification "
             "may be followed by the next Goal in the same response.\n"
            "- Keep the Codex Goal as short as correctness allows; there is no fixed character "
            "limit. Framework-scale or cross-module Goals may retain necessary task-specific "
            "interface, migration, integration, and fail-closed detail. Invoke the "
            "installed handoff skill and reference checked-in authorities, protocols, reports, "
            "formulas, tests, findings, and Git state instead of copying them. Include only the "
            "unique Goal, expected branch/base, authority pointers, exact allowed diff, "
            "task-specific delta, material prohibitions, validation, commit/push, and stop "
            "condition. Repository repetition is never justification for length; move durable "
            "detail into an authorized protocol or report and reference it when possible.\n"
             "- Work verification of a formal review-state commit is mechanical closure, not a "
             "new independent review. Do not create another report, `record-review` operation, "
             "or acceptance commit for that verification.\n"
            "- For an accepted implementation candidate, set both `last_reviewed_candidate` and "
            "`accepted_code_commit` to the candidate SHA. For an accepted docs-only protocol or "
            "governance candidate, update only `last_reviewed_candidate`; rejected, blocked, and "
            "review-state commits never replace the prior accepted code. Every review-state "
            "recording must pass `candidate_kind=implementation` or `candidate_kind=docs_only` "
            "explicitly to the handoff tool.\n"
            "- Automatic context compaction alone is not a reason to stop, commit, or hand off. "
            "At an explicit handoff, audit the repository and report unresolved work exactly.\n\n"
            "## Git\n\n"
            "- Before committing, verify the staged path set and required validation. After an "
            "authorized push, verify local and remote alignment and a clean worktree.\n"
            "- Do not amend, rebase, force-push, rewrite history, or commit incomplete work "
            "unless explicitly authorized.\n",
            encoding="utf-8",
        )
        print("created AGENTS.md")
    else:
        print("kept existing AGENTS.md")

    core_path = repo / CORE_REL
    if core_path.exists():
        print(f"kept existing {CORE_REL.as_posix()}")
    else:
        core = {
            "schema_version": 1,
            "project": repo.name,
            "research_question": "Not yet audited.",
            "target_outcome": "Not yet audited.",
            "primary_direction": "Not yet audited.",
            "primary_innovations": [
                "UNAUDITED: project-specific innovation hypotheses have not yet been established."
            ],
            "core_components": [
                "UNAUDITED: project-specific core components have not yet been mapped."
            ],
            "evidence_level": "unaudited",
            "strategic_status": "unaudited",
            "last_strategic_review": None,
            "updated_at": now_iso(),
        }
        core_path.parent.mkdir(parents=True, exist_ok=True)
        core_path.write_text(render_core(core), encoding="utf-8")
        print(f"created {CORE_REL.as_posix()}")

    state_path = repo / STATE_REL
    if state_path.exists():
        print(f"kept existing {STATE_REL.as_posix()}")
    else:
        branch = git(repo, "branch", "--show-current")
        state = {
            "schema_version": 1,
            "project": repo.name,
            "branch": branch,
            "research_phase": "exploratory_iteration",
            "current_gate": "Begin the shortest empirical loop",
            "last_reviewed_candidate": None,
            "accepted_code_commit": None,
            "review_verdict": "NO_REVIEW",
            "review_report": None,
            "open_findings": [],
            "next_gate": "First decision-complete empirical result",
            "next_action": "Audit PROJECT_CORE.md, then run the smallest experiment that answers the current research question.",
            "updated_at": now_iso(),
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(render_state(state), encoding="utf-8")
        print(f"created {STATE_REL.as_posix()}")
    return 0


def command_record_review(args: argparse.Namespace) -> int:
    repo = find_repo(Path(args.repo).resolve())
    if not repo:
        print("not a Git repository", file=sys.stderr)
        return 2
    state, errors = read_state(repo)
    if not state or errors:
        print("cannot update invalid CURRENT_STAGE: " + "; ".join(errors), file=sys.stderr)
        return 2
    review = json.loads(Path(args.input).read_text(encoding="utf-8"))
    required = (
        "candidate_sha",
        "verdict",
        "review_report",
        "open_findings",
        "next_gate",
        "next_action",
    )
    missing = [key for key in required if key not in review]
    if missing:
        print("review input missing: " + ", ".join(missing), file=sys.stderr)
        return 2
    candidate = review["candidate_sha"]
    verdict = review["verdict"]
    if not isinstance(candidate, str) or not SHA_RE.fullmatch(candidate):
        print("candidate_sha must be a full lowercase SHA", file=sys.stderr)
        return 2
    if verdict not in REVIEW_VERDICTS:
        print("invalid verdict", file=sys.stderr)
        return 2
    findings = review["open_findings"]
    if not isinstance(findings, list) or any(
        not isinstance(item, str) or not item.strip() for item in findings
    ):
        print("open_findings must be an array of non-empty strings", file=sys.stderr)
        return 2
    semantic_errors = validate_review_semantics(
        verdict, findings, require_explicit_labels=True
    )
    if semantic_errors:
        print("; ".join(semantic_errors), file=sys.stderr)
        return 2
    prior_accepted = state["accepted_code_commit"]
    requested_accepted = review.get("accepted_code_commit")
    candidate_kind = review.get("candidate_kind")
    if candidate_kind is not None and (
        not isinstance(candidate_kind, str) or candidate_kind not in CANDIDATE_KINDS
    ):
        print("candidate_kind must be implementation or docs_only", file=sys.stderr)
        return 2
    if candidate_kind is None and verdict in {"ACCEPT", "ACCEPT_WITH_P2"}:
        if "accepted_code_commit" not in review or requested_accepted == candidate:
            candidate_kind = "implementation"
        elif requested_accepted == prior_accepted:
            candidate_kind = "docs_only"
        else:
            print(
                "legacy accepted_code_commit cannot determine candidate_kind",
                file=sys.stderr,
            )
            return 2
    if verdict in {"ACCEPT", "ACCEPT_WITH_P2"}:
        expected_accepted = candidate if candidate_kind == "implementation" else prior_accepted
    else:
        expected_accepted = prior_accepted
    if "accepted_code_commit" in review and requested_accepted != expected_accepted:
        print(
            "accepted_code_commit conflicts with candidate_kind and verdict semantics",
            file=sys.stderr,
        )
        return 2
    state.update(
        {
            "current_gate": review.get("current_gate", state["current_gate"]),
            "last_reviewed_candidate": candidate,
            "review_verdict": verdict,
            "review_report": review["review_report"],
            "open_findings": findings,
            "next_gate": review["next_gate"],
            "next_action": review["next_action"],
            "updated_at": now_iso(),
        }
    )
    state["accepted_code_commit"] = expected_accepted
    errors = validate_state(repo, state)
    if errors:
        print("review state invalid: " + "; ".join(errors), file=sys.stderr)
        return 2
    (repo / STATE_REL).write_text(render_state(state), encoding="utf-8")
    print(f"updated {STATE_REL.as_posix()} for {candidate[:12]}: {verdict}")
    return 0


def command_resume_prompt(args: argparse.Namespace) -> int:
    repo = find_repo(Path(args.repo).resolve())
    if not repo:
        print("not a Git repository", file=sys.stderr)
        return 2
    core, core_errors = read_core(repo)
    state, state_errors = read_state(repo)
    errors = [f"PROJECT_CORE: {item}" for item in core_errors] + [
        f"CURRENT_STAGE: {item}" for item in state_errors
    ]
    if not core or not state or errors:
        print("cannot generate prompt from invalid canonical handoff: " + "; ".join(errors), file=sys.stderr)
        return 2
    if core["project"] != state["project"]:
        print("cannot generate prompt: PROJECT_CORE and CURRENT_STAGE project values differ", file=sys.stderr)
        return 2
    if args.surface == "work":
        print(
            "这是该项目的新 Browser ChatGPT Work 主控对话。\n\n"
            "先从 GitHub 重新读取 `AGENTS.md`、`docs/PROJECT_CORE.md`、"
            "`docs/CURRENT_STAGE.md` 及其指向的最新报告，核验远端分支与实际 HEAD；"
            "本 Prompt 和旧聊天摘要都不是权威状态。再读取公开输出规范：\n"
            f"{WORK_CONTRACT_URL}\n\n"
            "默认推进：最小实现 → 真实数据运行 → 指标 → 诊断 → 方向调整。探索性实现、测试、"
            "smoke、调试和调参不需要独立审查或 review-state。只有明确准备接受主要实现、冻结"
            "正式论文评估、采纳关键结果、改变核心方法或提升论文 claim 时，才进行一次 formal "
            "promotion 审查并记录结论；机械验收通过后可立即签发下一 Goal。\n\n"
            "按公开 Contract 简洁输出，最多给出一个 Codex Goal。Goal 引用仓库权威内容，不复制"
            "完整协议、历史、hash 或通用规则。达到验收目标即停止，相邻问题只记录。已授权的本地、"
            "可恢复、无付费真实数据工作无需逐次询问；只有付费、敏感数据、外部副作用、破坏性或"
            "不可逆操作需要先询问。若权威状态存在实质冲突，只给出最小核对或修正 Goal。"
        )
    else:
        print(
            "这是该项目的新 Codex 任务。\n\n"
            "先读取并遵守 `AGENTS.md`，再读取 `docs/PROJECT_CORE.md`、"
            "`docs/CURRENT_STAGE.md` 及当前 Gate 指向的报告；fetch 后实查分支、HEAD、远端跟踪 "
            f"ref、index 和 worktree。记录的预期分支为 `{state['branch']}`，但必须以 Git 实查为准。"
            "任何策略、状态或 Git 冲突都必须停止，不得依赖本 Prompt 或旧聊天自行补全。\n\n"
            "默认执行探索流程：最小实现、测试、真实数据运行、指标、诊断和方向调整。只有 Goal、"
            "用户或 CURRENT_STAGE 明确要求正式提升主要实现、冻结正式论文评估、关键结果、核心方法或论文 "
            "claim 时，才启动一次独立审查和 review-state。普通探索提交不需要审查或状态落库。"
            "合格的 Browser Work 审查不得重复自审；机械验收不得生成新的审查报告。完成后报告实际 "
            "diff、验证、实验指标、commit/push 和未闭环事项。达到验收目标即停止，不调查相邻问题。"
            "对已获授权的本地、可恢复、无付费真实数据工作不得增加 Gate；仅在涉及付费、敏感数据、"
            "外部副作用、破坏性或不可逆操作时主动询问用户。"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--repo", default=".")
    audit_parser.add_argument("--json", action="store_true")
    audit_parser.set_defaults(func=command_audit)
    init_parser = sub.add_parser("initialize")
    init_parser.add_argument("--repo", default=".")
    init_parser.set_defaults(func=command_initialize)
    review_parser = sub.add_parser("record-review")
    review_parser.add_argument("--repo", default=".")
    review_parser.add_argument("--input", required=True)
    review_parser.set_defaults(func=command_record_review)
    prompt_parser = sub.add_parser("resume-prompt")
    prompt_parser.add_argument("--repo", default=".")
    prompt_parser.add_argument("--surface", choices=("codex", "work"), default="codex")
    prompt_parser.set_defaults(func=command_resume_prompt)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
