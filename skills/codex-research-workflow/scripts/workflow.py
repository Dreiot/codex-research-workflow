#!/usr/bin/env python3
"""Deterministic helpers for governed research-project workflows."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
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
    "https://github.com/Dreiot/codex-research-workflow/blob/main/"
    "skills/codex-research-workflow/references/work-response-contract.md"
)
EXPERIMENT_ROOT_DEFAULT = Path("experiments")
EXPERIMENT_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62})$")
RUN_SCHEMA = "research-experiment-run/v1"
EVIDENCE_SCHEMA = "research-evidence-candidate/v1"
RUN_STATUSES = {"running", "completed", "failed", "interrupted"}
EVIDENCE_KINDS = {"direction_decision", "formal_evidence", "implementation_review"}
EVIDENCE_REPORT_HEADINGS = {
    "## Question",
    "## Method and Data",
    "## Results",
    "## Decision Boundary",
}
EXPERIMENT_IGNORE_RULES = (
    "experiments/runs/",
    "experiments/.tmp/",
    "experiments/quarantine/",
)
STATE_CURRENT_HEADINGS = {
    "## Current Gate",
    "## Open Findings",
    "## Next Action",
    "## Resume Rule",
}
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


def run(command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(payload: Dict[str, Any], prefix: str) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return f"{prefix}-{sha256_bytes(encoded)[:16]}"


def require_relative_path(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"{label} must be a repository-relative path")
    return path


def exact_repo(path: Path) -> Optional[Path]:
    resolved = path.resolve()
    repo = find_repo(resolved)
    return repo if repo == resolved else None


def immediate_nested_repositories(path: Path) -> List[Path]:
    roots: List[Path] = []
    for child in path.iterdir():
        if child.is_dir() and (child / ".git").exists():
            roots.append(child.resolve())
    return sorted(roots)


def validate_id(value: str, label: str) -> str:
    if not EXPERIMENT_ID_RE.fullmatch(value):
        raise ValueError(f"{label} must use lowercase ASCII letters, digits, and hyphens")
    return value


def experiment_root(repo: Path) -> Path:
    agents = repo / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"(?im)^\s*-?\s*Experiment root:\s*`([^`]+)`", text)
        if match:
            return require_relative_path(match.group(1).strip(), "Experiment root")
    return EXPERIMENT_ROOT_DEFAULT


def worktree_fingerprint(repo: Path) -> Tuple[bool, Optional[str]]:
    status = git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    if not status:
        return False, None
    digest = hashlib.sha256()
    digest.update(status.encode("utf-8"))
    for args in (("diff", "--binary", "HEAD"), ("diff", "--cached", "--binary", "HEAD")):
        result = run(["git", "-C", str(repo), *args])
        digest.update(result.stdout.encode("utf-8"))
    for line in status.splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:]
        path = repo / rel
        if path.is_file():
            digest.update(rel.encode("utf-8"))
            digest.update(sha256_file(path).encode("ascii"))
    return True, digest.hexdigest()


def clean_worktree(repo: Path) -> bool:
    return not bool(git(repo, "status", "--porcelain=v1", "--untracked-files=all"))


def current_head(repo: Path) -> Optional[str]:
    value = git(repo, "rev-parse", "--verify", "HEAD", check=False)
    return value if SHA_RE.fullmatch(value) else None


def remote_url(repo: Path) -> Optional[str]:
    value = git(repo, "remote", "get-url", "origin", check=False)
    return value or None


def git_accessible(repo: Path, rel: Path) -> bool:
    return run(["git", "-C", str(repo), "ls-files", "--error-unmatch", rel.as_posix()]).returncode == 0


def merge_ignore_rules(path: Path, rules: Tuple[str, ...] = EXPERIMENT_IGNORE_RULES) -> bool:
    original = path.read_text(encoding="utf-8") if path.is_file() else ""
    lines = original.splitlines()
    present = {line.strip() for line in lines}
    missing = [rule for rule in rules if rule not in present]
    if not missing:
        return False
    updated = original
    if updated and not updated.endswith("\n"):
        updated += "\n"
    if updated and updated.strip():
        updated += "\n"
    updated += "# Codex Research Workflow experiment artifacts\n"
    updated += "\n".join(missing) + "\n"
    path.write_text(updated, encoding="utf-8")
    return True


def next_identifier(parent: Path, prefix: str) -> str:
    maximum = 0
    if parent.is_dir():
        for child in parent.iterdir():
            match = re.fullmatch(rf"{re.escape(prefix)}(\d+)", child.name)
            if match:
                maximum = max(maximum, int(match.group(1)))
    return f"{prefix}{maximum + 1:03d}"


def initialize_authorities(repo: Path) -> List[str]:
    """Create only missing authority files and return their repository paths."""
    created: List[str] = []
    agents = repo / "AGENTS.md"
    if not agents.exists():
        agents.write_text(
            "# Project Agent Rules\n\n"
            "## Authority\n\n"
            "- Read `docs/PROJECT_CORE.md` for durable strategy and `docs/CURRENT_STAGE.md` "
            "for current state. For an ordinary Goal, check the exact root, branch, expected HEAD, "
            "and conflicting local changes. Run a full audit only before commit/push, formal promotion, "
            "authority updates, explicit handoff, or a material state conflict.\n"
            "- Chat summaries are not authoritative. Resolve material conflicts before editing.\n\n"
            "## Research Execution\n\n"
            "- Use `$codex-research-workflow` for governed Goals, reviews, handoffs, and durable "
            "direction changes.\n"
            "- Default to the shortest empirical loop: minimal implementation, real-data run, "
            "metrics, diagnosis, direction adjustment, and paper evidence.\n"
            "- Local, recoverable, no-cost work using project-authorized data is allowed by default. "
            "Ask before paid, sensitive, externally side-effecting, destructive, irreversible, or "
            "final held-out evaluation work.\n"
            "- Use the simplest correct, testable implementation. Do not add speculative abstractions "
            "or design-only Gates unless they directly block the current research decision.\n"
            "- Prefer semantic checks, declared numerical tolerances, material invariants, and existing "
            "Git identity. Do not add redundant hashes or use floating-output hashes as acceptance criteria.\n"
            "- Stop when acceptance criteria pass or metrics are sufficient to choose the next direction.\n\n"
            "## Review And State\n\n"
            "- Exploratory implementation, tests, smoke, debugging, parameter adjustment, and metric "
            "generation do not require independent review or review-state commits.\n"
            "- A Codex result packet normally supports the next decision. Optional implementation "
            "inspection does not require commit or push unless the reviewer needs GitHub access or "
            "the work is entering formal promotion.\n"
            "- Require one qualified independent review only for an explicit formal promotion: accepting "
            "a major implementation baseline, adopting a stable publication evaluation or key result, "
            "changing the core method, or raising a paper claim.\n"
            "- For an accepted implementation candidate, update accepted code identity; docs-only, rejected, "
            "blocked, and review-state commits never replace prior accepted code.\n"
            "- Research-controller responses must follow the public Work Response Contract. A clean review-state "
            "verification may be followed by the next Goal in the same response.\n"
            "- Codex is the executor, not the research controller. Its final report must not use the controller "
            "four-section format or output a `Codex 指令`.\n"
            "- Verification of a formal review-state commit is mechanical closure, not a new review.\n"
            "- Automatic context compaction alone is not a reason to stop, commit, or hand off.\n\n"
            "## Experiment Artifacts\n\n"
            "- Experiment root: `experiments`\n"
            "- Create experiment directories only when persistent artifacts are needed. Keep core "
            "method code in `src/` or the project's existing code location.\n"
            "- Do not place raw or external datasets under the experiment root.\n"
            "- Track scripts, configs, registry entries, and decision evidence needed for durable decisions. Ignore run outputs, "
            "temporary files, and quarantine.\n\n"
            "## Git\n\n"
            "- Verify the staged path set and validation before commit. Do not amend, rebase, force-push, "
            "rewrite history, or commit incomplete work unless explicitly authorized.\n",
            encoding="utf-8",
        )
        created.append("AGENTS.md")

    core_path = repo / CORE_REL
    if not core_path.exists():
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
        created.append(CORE_REL.as_posix())

    state_path = repo / STATE_REL
    if not state_path.exists():
        state = {
            "schema_version": 1,
            "project": repo.name,
            "branch": git(repo, "branch", "--show-current") or "main",
            "research_phase": "exploratory_iteration",
            "current_gate": "Begin the shortest empirical loop",
            "last_reviewed_candidate": None,
            "accepted_code_commit": None,
            "review_verdict": "NO_REVIEW",
            "review_report": None,
            "open_findings": [],
            "next_gate": "First decision-complete empirical result",
            "next_action": (
                "Audit PROJECT_CORE.md, then run the smallest experiment that answers the current "
                "research question."
            ),
            "updated_at": now_iso(),
        }
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(render_state(state), encoding="utf-8")
        created.append(STATE_REL.as_posix())
    return created


def initialize_experiment_policy(repo: Path) -> List[str]:
    changed: List[str] = []
    if merge_ignore_rules(repo / ".gitignore"):
        changed.append(".gitignore")
    return changed


def json_print(value: Dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


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
        "Read `AGENTS.md`, `docs/PROJECT_CORE.md`, and this file. For an ordinary Goal, check "
        "the exact Git root, branch, actual HEAD against the Goal's expected base, and conflicting "
        "index or worktree changes. Fetch, check the tracking ref, and run the full audit only before "
        "commit/push, formal promotion, authority updates, explicit handoff, or a material state "
        "conflict. Stop and report any mismatch.\n"
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

    state_path = repo / STATE_REL
    if state_path.is_file():
        state_text = state_path.read_text(encoding="utf-8", errors="replace")
        headings = [line.strip() for line in state_text.splitlines() if line.startswith("## ")]
        repeated = sorted({heading for heading in headings if headings.count(heading) > 1})
        if repeated:
            errors.append("CURRENT_STAGE repeats current-state sections: " + ", ".join(repeated))
        historical = [
            heading for heading in headings
            if re.search(r"(?i)history|historical|previous|past|archive|历史|往期|此前", heading)
        ]
        if historical:
            warnings.append(
                "CURRENT_STAGE contains historical sections; move durable direction history to PROJECT_CORE: "
                + ", ".join(historical)
            )

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
        core_text = core_path.read_text(encoding="utf-8", errors="replace")
        run_headings = [
            line.strip() for line in core_text.splitlines()
            if line.startswith("## ") and re.search(r"(?i)\brun\b|batch|逐次实验|运行记录", line)
        ]
        if run_headings:
            warnings.append(
                "PROJECT_CORE contains run-level narration; synthesize one record per durable direction: "
                + ", ".join(run_headings)
            )

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
    try:
        repo = require_exact_git_repo(args.repo)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    result = audit(repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"project_root: {result['repo']}")
        print(f"branch: {result['branch']}")
        print(f"HEAD: {result['head']}")
        print(f"worktree_clean: {result['worktree_clean']}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 1 if result["errors"] else 0


def command_initialize(args: argparse.Namespace) -> int:
    try:
        repo = require_exact_git_repo(args.repo, require_history=False)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    created = initialize_authorities(repo)
    for rel in ("AGENTS.md", CORE_REL.as_posix(), STATE_REL.as_posix()):
        print(("created " if rel in created else "kept existing ") + rel)
    return 0


def sensitive_initial_path(rel: Path) -> bool:
    lowered = rel.as_posix().lower()
    name = rel.name.lower()
    return (
        name.startswith(".env")
        or name in {"id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
        or name.endswith((".pem", ".key", ".p12", ".pfx"))
        or any(part.lower() in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in rel.parts)
        or lowered.startswith("experiments/runs/")
        or lowered.startswith("experiments/.tmp/")
        or lowered.startswith("experiments/quarantine/")
    )


def init_plan(target: Path, github_repo: Optional[str], visibility: Optional[str]) -> Dict[str, Any]:
    target = target.resolve()
    if not target.is_dir():
        raise ValueError("target directory does not exist")
    discovered = find_repo(target)
    if discovered and discovered != target:
        raise ValueError(f"target is nested inside Git repository: {discovered}")
    nested = [item for item in target.rglob(".git") if item.parent != target]
    if nested:
        raise ValueError("target contains a nested Git repository")
    repo = discovered
    if repo and current_head(repo):
        raise ValueError("repository already has commits; use migrate")
    origin = remote_url(repo) if repo else None
    if origin:
        probe = run(["git", "-C", str(repo), "ls-remote", "--heads", "origin"])
        if probe.returncode != 0:
            raise ValueError("cannot verify origin remote")
        if probe.stdout.strip():
            raise ValueError("origin already has branch history; refusing overwrite")
    elif not github_repo:
        raise ValueError("no origin remote; provide --github-repo OWNER/NAME and --visibility")
    if github_repo and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", github_repo):
        raise ValueError("--github-repo must be OWNER/NAME")
    if github_repo and visibility not in {"public", "private", "internal"}:
        raise ValueError("--visibility is required with --github-repo")

    include: List[Dict[str, Any]] = []
    blocked: List[str] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(target)
        if sensitive_initial_path(rel) or path.stat().st_size > 100 * 1024 * 1024:
            blocked.append(rel.as_posix())
            continue
        include.append({"path": rel.as_posix(), "sha256": sha256_file(path), "bytes": path.stat().st_size})
    payload: Dict[str, Any] = {
        "schema": "codex-research-workflow-init-plan/v1",
        "repo": str(target),
        "origin": origin,
        "github_repo": github_repo,
        "visibility": visibility,
        "initial_files": include,
        "blocked_files": blocked,
        "creates": ["AGENTS.md", CORE_REL.as_posix(), STATE_REL.as_posix(), ".gitignore"],
        "branch": "main",
    }
    payload["plan_id"] = stable_id(payload, "init")
    return payload


def command_init(args: argparse.Namespace) -> int:
    target = Path(args.repo).resolve()
    try:
        plan = init_plan(target, args.github_repo, args.visibility)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not args.apply:
        json_print(plan)
        return 0
    if plan["blocked_files"]:
        print("blocked or oversized files require user resolution: " + ", ".join(plan["blocked_files"]), file=sys.stderr)
        return 2
    if args.expected_plan_id != plan["plan_id"]:
        print("plan changed or --expected-plan-id is missing", file=sys.stderr)
        return 2
    repo = exact_repo(target)
    if not repo:
        result = run(["git", "init", "-b", "main", str(target)])
        if result.returncode != 0:
            print(result.stderr.strip(), file=sys.stderr)
            return 2
        repo = target
    else:
        git(repo, "branch", "-M", "main")
    if not remote_url(repo) and args.github_repo:
        create = run(
            ["gh", "repo", "create", args.github_repo, f"--{args.visibility}", "--source", str(repo), "--remote", "origin"]
        )
        if create.returncode != 0:
            print(create.stderr.strip(), file=sys.stderr)
            return 2
    created = initialize_authorities(repo)
    changed = initialize_experiment_policy(repo)
    stage = [item["path"] for item in plan["initial_files"]] + created + changed
    stage = sorted(set(stage))
    if stage:
        git(repo, "add", "--", *stage)
    staged = git(repo, "diff", "--cached", "--name-only")
    if not staged:
        print("nothing staged; initialization aborted", file=sys.stderr)
        return 2
    git(repo, "commit", "-m", "chore: initialize Codex Research Workflow")
    git(repo, "push", "-u", "origin", "main")
    json_print({"status": "initialized", "plan_id": plan["plan_id"], "head": git(repo, "rev-parse", "HEAD"), "staged_paths": staged.splitlines()})
    return 0


def migration_plan(repo: Path) -> Dict[str, Any]:
    repo = repo.resolve()
    if exact_repo(repo) != repo or not current_head(repo):
        raise ValueError("migrate requires the exact root of an existing Git repository")
    if not clean_worktree(repo):
        raise ValueError("migrate requires a clean worktree")
    agents = repo / "AGENTS.md"
    agents_text = agents.read_text(encoding="utf-8", errors="replace") if agents.is_file() else ""
    changes: List[str] = []
    if "Experiment root:" not in agents_text:
        changes.append("append experiment artifact policy to AGENTS.md")
    root = experiment_root(repo).as_posix().rstrip("/")
    ignore_rules = tuple(f"{root}/{part}/" for part in ("runs", ".tmp", "quarantine"))
    ignore_text = (repo / ".gitignore").read_text(encoding="utf-8", errors="replace") if (repo / ".gitignore").is_file() else ""
    if any(rule not in {line.strip() for line in ignore_text.splitlines()} for rule in ignore_rules):
        changes.append("add generated-artifact ignore rules")
    for rel in ("AGENTS.md", CORE_REL.as_posix(), STATE_REL.as_posix()):
        if not (repo / rel).is_file():
            changes.append(f"create missing {rel}")
    payload: Dict[str, Any] = {
        "schema": "codex-research-workflow-migration-plan/v1",
        "repo": str(repo),
        "head": current_head(repo),
        "origin": remote_url(repo),
        "changes": changes,
        "does_not_change": ["existing experiment artifacts", "historical analysis_reports paths", "scientific content"],
    }
    payload["plan_id"] = stable_id(payload, "migrate")
    return payload


def append_experiment_policy(repo: Path) -> bool:
    path = repo / "AGENTS.md"
    text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else "# Project Agent Rules\n"
    if "Experiment root:" in text:
        return False
    if not text.endswith("\n"):
        text += "\n"
    text += (
        "\n## Experiment Artifacts\n\n"
        "- Experiment root: `experiments`\n"
        "- Create experiment directories only when persistent outputs are needed. Keep raw and external datasets outside this root.\n"
        "- Track scripts, configs, registry entries, and evidence; ignore runs, temporary files, and quarantine.\n"
    )
    path.write_text(text, encoding="utf-8")
    return True


def command_migrate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    try:
        plan = migration_plan(repo)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not args.apply:
        json_print(plan)
        return 0
    if args.expected_plan_id != plan["plan_id"]:
        print("plan changed or --expected-plan-id is missing", file=sys.stderr)
        return 2
    changed = initialize_authorities(repo)
    if append_experiment_policy(repo):
        changed.append("AGENTS.md")
    root = experiment_root(repo).as_posix().rstrip("/")
    if merge_ignore_rules(repo / ".gitignore", tuple(f"{root}/{part}/" for part in ("runs", ".tmp", "quarantine"))):
        changed.append(".gitignore")
    if not changed:
        json_print({"status": "already-current", "plan_id": plan["plan_id"], "head": current_head(repo)})
        return 0
    git(repo, "add", "--", *sorted(set(changed)))
    git(repo, "commit", "-m", "chore: migrate to Codex Research Workflow")
    if not args.no_push and remote_url(repo):
        git(repo, "push", "origin", git(repo, "branch", "--show-current"))
    json_print({"status": "migrated", "plan_id": plan["plan_id"], "head": current_head(repo), "changed": sorted(set(changed))})
    return 0


def require_exact_git_repo(value: str, require_history: bool = True) -> Path:
    repo = Path(value).resolve()
    if exact_repo(repo) == repo:
        if require_history and not current_head(repo):
            raise ValueError("command requires an existing commit at the exact project/Git root")
        return repo
    nested = immediate_nested_repositories(repo) if repo.is_dir() else []
    if nested:
        joined = ", ".join(str(path) for path in nested)
        raise ValueError(
            "project root contains a nested Git repository; relocate Git to the project root: "
            + joined
        )
    discovered = find_repo(repo) if repo.is_dir() else None
    if discovered:
        raise ValueError(f"--repo must name the exact project/Git root, not a subdirectory: {discovered}")
    raise ValueError("command requires one project root that is also the exact Git root")


def require_ignored(repo: Path, rel: Path) -> None:
    probe = run(["git", "-C", str(repo), "check-ignore", "--no-index", "--quiet", rel.as_posix()])
    if probe.returncode != 0:
        raise ValueError(f"generated path is not ignored: {rel.as_posix()}; run migrate")


def command_prepare_experiment(args: argparse.Namespace) -> int:
    try:
        repo = require_exact_git_repo(args.repo)
        experiment_id = validate_id(args.experiment_id, "experiment-id")
        root = experiment_root(repo)
        run_id = validate_id(args.run_id or next_identifier(repo / root / "runs" / experiment_id, "r"), "run-id")
        rel_dir = root / "runs" / experiment_id / run_id
        require_ignored(repo, rel_dir / "manifest.json")
        target = repo / rel_dir
        if target.exists():
            raise ValueError(f"run already exists: {rel_dir.as_posix()}")
        dirty, diff_hash = worktree_fingerprint(repo)
        manifest = {
            "schema": RUN_SCHEMA,
            "experiment_id": experiment_id,
            "run_id": run_id,
            "created_at": now_iso(),
            "entrypoint": args.entrypoint,
            "config": args.config,
            "data_ids": args.data_id or [],
            "git_head": current_head(repo),
            "worktree_dirty": dirty,
            "diff_hash": diff_hash,
            "status": args.status,
        }
        target.mkdir(parents=True)
        (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        json_print({"path": rel_dir.as_posix(), "manifest": manifest})
        return 0
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def evidence_manifest(
    repo: Path,
    rel_dir: Path,
    experiment_id: str,
    candidate_id: str,
    base: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    artifacts: Dict[str, str] = {}
    target = repo / rel_dir
    for path in sorted(target.iterdir()):
        if path.is_file() and path.name != "manifest.json":
            artifacts[path.name] = sha256_file(path)
    manifest = dict(base or {})
    manifest.update({
        "schema": EVIDENCE_SCHEMA,
        "experiment_id": experiment_id,
        "candidate_id": candidate_id,
        "artifacts": artifacts,
    })
    manifest.setdefault("created_at", now_iso())
    manifest.setdefault("candidate_kind", "direction_decision")
    manifest.setdefault("question", "Not yet recorded.")
    manifest.setdefault("git_head", current_head(repo))
    manifest.setdefault("source_run_ids", [])
    manifest.setdefault("config", None)
    manifest.setdefault("validator", None)
    manifest.setdefault("validator_status", "not_run")
    return manifest


def command_prepare_evidence(args: argparse.Namespace) -> int:
    try:
        repo = require_exact_git_repo(args.repo)
        experiment_id = validate_id(args.experiment_id, "experiment-id")
        parent = repo / experiment_root(repo) / "evidence" / experiment_id
        candidate_id = validate_id(args.candidate_id or next_identifier(parent, "c"), "candidate-id")
        rel_dir = experiment_root(repo) / "evidence" / experiment_id / candidate_id
        target = repo / rel_dir
        if target.exists():
            raise ValueError(f"evidence candidate already exists: {rel_dir.as_posix()}")
        target.mkdir(parents=True)
        (target / "analysis_report.md").write_text(
            f"# Analysis Report\n\n## Question\n\n{args.question}\n\n"
            "## Method and Data\n\nRecord entrypoint, configuration, data identifiers, and statistical unit.\n\n"
            "## Results\n\nRecord positive, negative, and mixed results.\n\n## Decision Boundary\n\n"
            "State what this evidence supports, what it does not support, and the next decision.\n",
            encoding="utf-8",
        )
        if args.with_metrics:
            (target / "metrics.json").write_text("{}\n", encoding="utf-8")
        manifest = evidence_manifest(
            repo,
            rel_dir,
            experiment_id,
            candidate_id,
            {
                "created_at": now_iso(),
                "candidate_kind": args.candidate_kind,
                "question": args.question,
                "git_head": current_head(repo),
                "source_run_ids": args.source_run or [],
                "config": args.config,
                "validator": args.validator,
                "validator_status": "not_run" if args.validator else "not_applicable",
            },
        )
        (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        json_print({"path": rel_dir.as_posix(), "manifest": manifest})
        return 0
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


def command_validate_evidence(args: argparse.Namespace) -> int:
    try:
        repo = require_exact_git_repo(args.repo)
        rel_dir = require_relative_path(args.path, "path")
        target = repo / rel_dir
        manifest_path = target / "manifest.json"
        report_path = target / "analysis_report.md"
        if not manifest_path.is_file() or not report_path.is_file() or not report_path.read_text(encoding="utf-8").strip():
            raise ValueError("evidence candidate requires non-empty manifest.json and analysis_report.md")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("schema") != EVIDENCE_SCHEMA:
            raise ValueError("invalid evidence schema")
        required = {
            "experiment_id",
            "candidate_id",
            "candidate_kind",
            "question",
            "git_head",
            "source_run_ids",
            "config",
            "validator",
            "validator_status",
            "artifacts",
        }
        missing = sorted(required - set(manifest))
        if missing:
            raise ValueError("evidence manifest missing: " + ", ".join(missing))
        if manifest.get("candidate_kind") not in EVIDENCE_KINDS:
            raise ValueError("invalid evidence candidate_kind")
        if not isinstance(manifest.get("question"), str) or not manifest["question"].strip():
            raise ValueError("evidence question must be non-empty")
        if not isinstance(manifest.get("source_run_ids"), list):
            raise ValueError("source_run_ids must be an array")
        report_headings = {
            line.strip() for line in report_path.read_text(encoding="utf-8").splitlines()
            if line.startswith("## ")
        }
        missing_headings = sorted(EVIDENCE_REPORT_HEADINGS - report_headings)
        if missing_headings:
            raise ValueError("analysis report missing sections: " + ", ".join(missing_headings))
        if args.refresh:
            refreshed = evidence_manifest(
                repo,
                rel_dir,
                manifest["experiment_id"],
                manifest["candidate_id"],
                manifest,
            )
            manifest_path.write_text(json.dumps(refreshed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            manifest = refreshed
        errors: List[str] = []
        for name, expected in manifest.get("artifacts", {}).items():
            path = target / name
            if not path.is_file() or sha256_file(path) != expected:
                errors.append(f"artifact hash mismatch: {name}")
        for path in target.iterdir():
            if path.is_file() and not git_accessible(repo, path.relative_to(repo)):
                errors.append(f"artifact is not tracked or staged: {path.relative_to(repo).as_posix()}")
        if errors:
            print("; ".join(errors), file=sys.stderr)
            return 2
        json_print({"status": "valid", "path": rel_dir.as_posix(), "git_head": current_head(repo)})
        return 0
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


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
            "网页端不加载本机 Codex Skill；请遵守本项目的 Project Instructions、可见上下文和"
            "上述公开 Contract。\n\n"
            "默认推进：最小实现 → 真实数据运行 → 指标 → 诊断 → 方向调整。探索性实现、测试、"
            "smoke、调试和调参不需要独立审查或 review-state。只有明确准备接受主要实现、采纳"
            "稳定的正式论文评价方案或关键结果、改变核心方法或提升论文 claim 时，才进行一次 formal "
            "promotion 审查并记录结论；机械验收通过后可立即签发下一 Goal。\n\n"
            "按公开 Contract 简洁输出，最多给出一个 Codex Goal。Goal 引用仓库权威内容，不复制"
            "完整协议、历史、hash 或通用规则。达到验收目标即停止，相邻问题只记录。已授权的本地、"
            "可恢复、无付费真实数据工作无需逐次询问；只有付费、敏感数据、外部副作用、破坏性或"
            "不可逆操作需要先询问。若权威状态存在实质冲突，只给出最小核对或修正 Goal。"
        )
    else:
        print(
            "这是该项目的新 Codex 任务。\n\n"
            "请显式使用 `$codex-research-workflow`。"
            "先读取并遵守 `AGENTS.md`，再读取 `docs/PROJECT_CORE.md`、"
            "`docs/CURRENT_STAGE.md` 及本 Goal 所需的当前报告。普通 Goal 只做轻量本地核对："
            f"精确 Git 根、分支、HEAD 是否符合预期（记录分支为 `{state['branch']}`）以及 index/worktree "
            "是否有冲突性修改。不要重复网页控制器已经完成的远端审查。只有准备 commit/push、formal "
            "promotion、权威文件更新、显式交接，或发现实质状态冲突时，才 fetch、核验远端并运行完整 "
            "audit。冲突时停止，不得依赖本 Prompt 或旧聊天自行补全。\n\n"
            "默认执行探索流程：最小实现、测试、真实数据运行、指标、诊断和方向调整。只有 Goal、"
            "用户或 CURRENT_STAGE 明确要求正式提升主要实现、稳定论文评价、关键结果、核心方法或论文 "
            "claim 时，才启动一次独立审查和 review-state。普通探索不要求提交、push、审查或状态落库；"
            "Codex 结果包足以支持下一步时，不增加 implementation inspection。"
            "合格的独立审查不得重复；机械验收不得生成新的审查报告。完成后报告实际 "
            "diff、验证、实验指标、commit/push 和未闭环事项。达到验收目标即停止，不调查相邻问题。"
            "你是执行端，不是 Research Controller；最终不得使用 Work Response Contract 四段式或输出 "
            "`Codex 指令`。默认采用语义验证、声明的数值容差、关键不变量和现有 Git 身份，不得自行增加"
            "冗余 hash，也不得把浮点结果 hash 作为验收条件。"
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
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--repo", default=".")
    init_parser.add_argument("--github-repo")
    init_parser.add_argument("--visibility", choices=("public", "private", "internal"))
    init_parser.add_argument("--apply", action="store_true")
    init_parser.add_argument("--expected-plan-id")
    init_parser.set_defaults(func=command_init)
    migrate_parser = sub.add_parser("migrate")
    migrate_parser.add_argument("--repo", default=".")
    migrate_parser.add_argument("--apply", action="store_true")
    migrate_parser.add_argument("--expected-plan-id")
    migrate_parser.add_argument("--no-push", action="store_true")
    migrate_parser.set_defaults(func=command_migrate)
    experiment_parser = sub.add_parser("prepare-experiment")
    experiment_parser.add_argument("--repo", default=".")
    experiment_parser.add_argument("--experiment-id", required=True)
    experiment_parser.add_argument("--run-id")
    experiment_parser.add_argument("--entrypoint", required=True)
    experiment_parser.add_argument("--config")
    experiment_parser.add_argument("--data-id", action="append")
    experiment_parser.add_argument("--status", choices=sorted(RUN_STATUSES), default="running")
    experiment_parser.set_defaults(func=command_prepare_experiment)
    evidence_parser = sub.add_parser("prepare-evidence")
    evidence_parser.add_argument("--repo", default=".")
    evidence_parser.add_argument("--experiment-id", required=True)
    evidence_parser.add_argument("--candidate-id")
    evidence_parser.add_argument("--candidate-kind", choices=sorted(EVIDENCE_KINDS), default="direction_decision")
    evidence_parser.add_argument("--question", required=True)
    evidence_parser.add_argument("--source-run", action="append")
    evidence_parser.add_argument("--config")
    evidence_parser.add_argument("--validator")
    evidence_parser.add_argument("--with-metrics", action="store_true")
    evidence_parser.set_defaults(func=command_prepare_evidence)
    validate_parser = sub.add_parser("validate-evidence")
    validate_parser.add_argument("--repo", default=".")
    validate_parser.add_argument("--path", required=True)
    validate_parser.add_argument("--refresh", action="store_true")
    validate_parser.set_defaults(func=command_validate_evidence)
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
    if len(sys.argv) > 1 and sys.argv[1] == "initialize":
        legacy = argparse.ArgumentParser()
        legacy.add_argument("command")
        legacy.add_argument("--repo", default=".")
        return command_initialize(legacy.parse_args())
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
