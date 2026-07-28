#!/usr/bin/env python3
"""Read-only Codex lifecycle hook for canonical project handoffs."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from handoff import CORE_REL, STATE_REL, audit, find_repo, git, read_core, read_state


def emit(system_message: str = "", context: str = "", event: str = "") -> None:
    output: Dict[str, Any] = {}
    if system_message:
        output["systemMessage"] = system_message
    if context:
        output["hookSpecificOutput"] = {
            "hookEventName": event,
            "additionalContext": context,
        }
    if output:
        print(json.dumps(output, ensure_ascii=False))


def command_text(payload: Dict[str, Any]) -> str:
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return ""
    value = tool_input.get("command") or tool_input.get("cmd") or ""
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return str(value)


def has_git_action(command: str, action: str) -> bool:
    return bool(re.search(rf"(?i)(^|[;&|\s])git(?:\.exe)?\s+[^\r\n]*\b{re.escape(action)}\b", command))


def compact_list(values: Iterable[str], limit: int = 3) -> str:
    items = [str(value).strip() for value in values if str(value).strip()]
    selected = items[:limit]
    summary = " | ".join(selected) if selected else "none"
    if len(items) > limit:
        summary += f" | +{len(items) - limit} more"
    return summary


def governance_doc(path: str) -> bool:
    return path == "AGENTS.md" or path.startswith("docs/")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    event = str(payload.get("hook_event_name") or "")
    cwd = Path(str(payload.get("cwd") or ".")).resolve()
    repo = find_repo(cwd)
    if not repo:
        return 0

    if event == "SessionStart":
        core, core_errors = read_core(repo)
        state, state_errors = read_state(repo)
        messages: List[str] = []
        if core_errors:
            messages.append("PROJECT_CORE: " + "; ".join(core_errors))
        if state_errors:
            messages.append("CURRENT_STAGE: " + "; ".join(state_errors))
        context_parts = [
            f"Canonical handoff sources: AGENTS.md, {CORE_REL.as_posix()}, {STATE_REL.as_posix()}."
        ]
        if core:
            context_parts.append(
                f"Strategy: project={core['project']}; direction={core['primary_direction']}; "
                f"innovations={compact_list(core['primary_innovations'])}; "
                f"components={compact_list(core['core_components'])}; "
                f"evidence_level={core['evidence_level']}; strategic_status={core['strategic_status']}."
            )
        else:
            context_parts.append(
                "Strategic core is not available; migrate it before the next strategic decision and do not "
                "reconstruct research direction from chat memory."
            )
        if state:
            context_parts.append(
                f"Volatile state: branch={state['branch']}; actual_HEAD={git(repo, 'rev-parse', 'HEAD')}; "
                f"gate={state['current_gate']}; verdict={state['review_verdict']}; "
                f"open_findings={compact_list(state['open_findings'])}; next_action={state['next_action']}."
            )
        else:
            context_parts.append("Volatile Gate state is unavailable; do not begin substantial work.")
        context_parts.append(
            "Use the shortest empirical loop by default. Ordinary exploratory commits do not require review-state "
            "recording. Resolve material Git/strategy/stage conflicts before relying on them."
        )
        emit(system_message=" | ".join(messages), context=" ".join(context_parts), event=event)
        return 0

    if event == "SubagentStart":
        emit(
            context=(
                "You are the fresh research reviewer. Review only the exact base and candidate SHAs "
                "provided by the parent. Treat AGENTS.md, docs/PROJECT_CORE.md, docs/CURRENT_STAGE.md, "
                "repository evidence, and tests as authoritative boundaries; flag conflicts rather than "
                "resolving strategy yourself. Do not edit, stage, commit, push, repair, or update handoff "
                "files. Return findings as P0/P1/P2 and one verdict: ACCEPT, ACCEPT_WITH_P2, REJECT, or "
                "BLOCKED. P0/P1 requires REJECT."
            ),
            event=event,
        )
        return 0

    if event == "SubagentStop":
        emit(
            system_message=(
                "Research reviewer finished. If this was an explicitly requested formal promotion review, "
                "write its report, update docs/CURRENT_STAGE.md with maintain-codex-handoff, audit it, and "
                "create one governance-docs-only review-state commit. Exploratory work does not gain a "
                "review-state requirement merely because a reviewer was consulted."
            ),
            event=event,
        )
        return 0

    command = command_text(payload)
    if event == "PreToolUse":
        warnings: List[str] = []
        if has_git_action(command, "commit"):
            staged = git(repo, "diff", "--cached", "--name-only", check=False).splitlines()
            review_staged = any("review" in name.lower() and name.lower().endswith(".md") for name in staged)
            if review_staged and STATE_REL.as_posix() not in staged:
                warnings.append("review report is staged but docs/CURRENT_STAGE.md is not staged")
            if CORE_REL.as_posix() in staged:
                _, core_errors = read_core(repo)
                warnings.extend(f"PROJECT_CORE: {item}" for item in core_errors)
        if has_git_action(command, "push"):
            for rel in (CORE_REL, STATE_REL):
                status = git(repo, "status", "--short", "--", rel.as_posix(), check=False)
                if status:
                    warnings.append(f"{rel.as_posix()} has uncommitted changes before push")
        if warnings:
            emit(system_message="Handoff warning: " + "; ".join(warnings), event=event)
        return 0

    if event == "PostToolUse":
        warnings: List[str] = []
        if has_git_action(command, "commit"):
            changed = git(repo, "show", "--pretty=format:", "--name-only", "HEAD", check=False).splitlines()
            canonical_changed = CORE_REL.as_posix() in changed or STATE_REL.as_posix() in changed
            if CORE_REL.as_posix() in changed:
                core, core_errors = read_core(repo)
                warnings.extend(f"PROJECT_CORE: {item}" for item in core_errors)
            else:
                core = None
            if STATE_REL.as_posix() in changed:
                state, state_errors = read_state(repo)
                warnings.extend(f"CURRENT_STAGE: {item}" for item in state_errors)
            else:
                state = None
            if canonical_changed:
                non_governance = [name for name in changed if name and not governance_doc(name)]
                if non_governance:
                    warnings.append(
                        "canonical handoff commit contains non-governance files: " + ", ".join(non_governance)
                    )
                if core is None:
                    core, _ = read_core(repo)
                if state is None:
                    state, _ = read_state(repo)
                if core and state and core.get("project") != state.get("project"):
                    warnings.append("PROJECT_CORE and CURRENT_STAGE project values differ")
            elif any("review" in name.lower() and name.lower().endswith(".md") for name in changed):
                warnings.append("review report committed without docs/CURRENT_STAGE.md")
        if has_git_action(command, "push"):
            branch = git(repo, "branch", "--show-current", check=False)
            local = git(repo, "rev-parse", "HEAD", check=False)
            remote = git(repo, "rev-parse", f"origin/{branch}", check=False)
            if remote and local != remote:
                warnings.append(f"local HEAD {local[:12]} != origin/{branch} {remote[:12]} after push")
        if warnings:
            emit(system_message="Handoff validation warning: " + "; ".join(warnings), event=event)
        return 0

    if event == "Stop":
        result = audit(repo)
        warnings = list(result["errors"]) + list(result["warnings"])
        if warnings:
            emit(system_message="Handoff closure warning: " + "; ".join(warnings), event=event)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
