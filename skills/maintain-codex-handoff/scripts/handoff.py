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
VERDICTS = {"ACCEPT", "ACCEPT_WITH_P2", "REJECT", "BLOCKED"}
STRATEGIC_STATUSES = {"unaudited", "active", "paused", "redirected", "completed"}
WORK_CONTRACT_URL = (
    "https://github.com/Dreiot/codex-research-handoff/blob/main/"
    "skills/maintain-codex-handoff/references/work-response-contract-v1.md"
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
    if state.get("review_verdict") not in VERDICTS:
        errors.append("invalid review_verdict")
    if not isinstance(state.get("open_findings"), list) or not all(
        isinstance(item, str) and item.strip() for item in state.get("open_findings", [])
    ):
        errors.append("open_findings must be an array of non-empty strings")
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
    pending = bool(state_commit and state_commit != head)
    if pending:
        warnings.append(
            f"HEAD {head[:12]} is newer than state commit {state_commit[:12]}; review closure may be pending"
        )
    return {
        "repo": str(repo),
        "branch": branch,
        "head": head,
        "state_commit": state_commit or None,
        "core_commit": core_commit or None,
        "pending_after_state": pending,
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
            "- Before editing, verify the branch, HEAD, index, worktree, and any remote or "
            "tracking ref required by the current Goal. Stop and report any conflict between "
            "Git, project strategy, and current state.\n"
            "- Execute one bounded Goal at a time. Keep every change within its authorized "
            "file and evidence scope; do not infer authorization for a later Gate.\n"
            "- During method development, prefer the smallest sufficient implementation and "
            "experiment matrix that is correct, testable, reproducible, and robust enough to "
            "answer the current research question and support the target claim. Reuse existing "
            "components and avoid speculative abstractions, duplicate mechanisms, broad "
            "refactors, exhaustive generalization, or unnecessary design-only Gates.\n"
            "- Never trade away data integrity, statistical validity, reproducibility, "
            "fail-closed safeguards, or claim boundaries for speed or smaller code.\n"
            "- Do not advance a Gate or scientific claim without explicit evidence.\n\n"
            "## Review And State\n\n"
            "- Require one qualified independent review pinned to the exact base and candidate "
            "SHAs. Do not duplicate a qualifying Browser Work review with a Codex reviewer, "
            "and do not let the reviewer modify the candidate.\n"
            "- Update `docs/CURRENT_STAGE.md` only after an authoritative Gate, review, "
            "finding, or next-action change. Update `docs/PROJECT_CORE.md` only after a durable "
            "strategic, innovation, component, evidence, or claim-boundary change.\n"
            "- Do not treat chat summaries, local tests, or candidate-local validation as "
            "independent acceptance.\n"
            "- Browser Work responses must follow the public Work Response Contract: exactly "
            "`审查结果`, `设计目标`, `验收目标`, and `Codex 指令`, with one fenced "
            "Markdown block containing one Codex Goal. Never combine review-state recording "
            "with the next candidate.\n"
            "- Record every completed candidate review before remediation or Gate advancement, "
            "including `REJECT` and `BLOCKED`. After Work verifies that review-state commit, "
            "accepted work may advance; rejected or blocked work may only remediate findings "
            "or collect missing evidence.\n"
            "- Work verification of a review-state commit is mechanical closure, not a new "
            "independent review. Do not create another report, `record-review` operation, or "
            "acceptance commit for that verification.\n"
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
            "research_phase": "handoff_migration",
            "current_gate": "Establish canonical project state",
            "last_reviewed_candidate": None,
            "accepted_code_commit": None,
            "review_verdict": "BLOCKED",
            "review_report": None,
            "open_findings": ["Project-specific current state has not yet been audited."],
            "next_gate": "Project state audit",
            "next_action": "Audit governing documents and Git history before implementation.",
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
    required = ("candidate_sha", "verdict", "review_report", "open_findings", "next_gate", "next_action")
    missing = [key for key in required if key not in review]
    if missing:
        print("review input missing: " + ", ".join(missing), file=sys.stderr)
        return 2
    candidate = review["candidate_sha"]
    verdict = review["verdict"]
    if not isinstance(candidate, str) or not SHA_RE.fullmatch(candidate):
        print("candidate_sha must be a full lowercase SHA", file=sys.stderr)
        return 2
    if verdict not in VERDICTS:
        print("invalid verdict", file=sys.stderr)
        return 2
    state.update(
        {
            "current_gate": review.get("current_gate", state["current_gate"]),
            "last_reviewed_candidate": candidate,
            "review_verdict": verdict,
            "review_report": review["review_report"],
            "open_findings": review["open_findings"],
            "next_gate": review["next_gate"],
            "next_action": review["next_action"],
            "updated_at": now_iso(),
        }
    )
    if verdict in {"ACCEPT", "ACCEPT_WITH_P2"}:
        state["accepted_code_commit"] = review.get("accepted_code_commit", candidate)
    elif "accepted_code_commit" in review:
        state["accepted_code_commit"] = review["accepted_code_commit"]
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
            "判断当前事务属于 candidate 独立审查、review-state 机械验收、普通状态核验，"
            "还是阻塞修正。严格按规范只输出 `审查结果`、`设计目标`、`验收目标`、"
            "`Codex 指令` 四节；最后一节只能有一个 fenced `markdown` 指令块，且其中只能有"
            "一个最小、可验证的 Codex Goal。不要输出隐藏推理，不要使用冗长分隔线，不要把"
            "审查落库与下一 candidate 合并。\n\n"
            "若 candidate 审查已完成但尚未落库（包括 REJECT/BLOCKED），唯一 Goal 必须是 "
            "docs-only review-state recording，此优先级高于 remediation。若 review-state "
            "commit 已验收，验收本身不得再次落库；ACCEPT/ACCEPT_WITH_P2 可把下一项已授权 "
            "candidate 作为唯一 Goal，REJECT/BLOCKED 则只能给出 remediation 或补证据 Goal。"
            "若 Git、PROJECT_CORE 与 CURRENT_STAGE "
            "冲突，报告 BLOCKED，且只允许给出有界的核对或修正 Goal。"
        )
    else:
        print(
            "这是该项目的新 Codex 任务。\n\n"
            "先读取并遵守 `AGENTS.md`，再读取 `docs/PROJECT_CORE.md`、"
            "`docs/CURRENT_STAGE.md` 及当前 Gate 指向的报告；fetch 后实查分支、HEAD、远端跟踪 "
            f"ref、index 和 worktree。记录的预期分支为 `{state['branch']}`，但必须以 Git 实查为准。"
            "任何策略、状态或 Git 冲突都必须停止，不得依赖本 Prompt 或旧聊天自行补全。\n\n"
            "开始前把当前工作归类为以下唯一一种事务：review-state recording、remediation、"
            "next candidate 或 handoff-only。只执行 `CURRENT_STAGE.md` 与用户提供指令共同授权的"
            "一个原子 Goal；简要说明它与项目主方向、当前 Gate、最近 verdict 和未解决问题的关系。"
            "合格的 Browser Work 审查不得重复自审；review-state 的机械验收不得生成新的审查报告或"
            "acceptance commit；不得把审查落库与下一 Gate 合并。完成后报告精确 diff、验证、commit、"
            "push、远端对齐和仍未闭环事项。"
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
