#!/usr/bin/env python3
"""Fail-open lifecycle hints for Codex Research Workflow."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict

from workflow import CORE_REL, STATE_REL, find_repo, git, read_core, read_state


def emit(*, system_message: str = "", context: str = "", event: str = "") -> None:
    output: Dict[str, Any] = {}
    if system_message:
        output["systemMessage"] = system_message
    if context:
        output["hookSpecificOutput"] = {"hookEventName": event, "additionalContext": context}
    if output:
        print(json.dumps(output, ensure_ascii=False))


def command_text(payload: Dict[str, Any]) -> str:
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return ""
    value = tool_input.get("command") or tool_input.get("cmd") or ""
    return " ".join(str(item) for item in value) if isinstance(value, list) else str(value)


def has_git_action(command: str, action: str) -> bool:
    return bool(re.search(rf"(?i)(^|[;&|\s])git(?:\.exe)?\s+[^\r\n]*\b{re.escape(action)}\b", command))


def core_changed(repo: Path, rev: str = "HEAD") -> bool:
    changed = git(repo, "show", "--pretty=format:", "--name-only", rev, check=False).splitlines()
    return CORE_REL.as_posix() in changed


def handle(payload: Dict[str, Any]) -> int:
    event = str(payload.get("hook_event_name") or "")
    repo = find_repo(Path(str(payload.get("cwd") or ".")).resolve())
    if not repo:
        return 0

    if event == "SessionStart":
        core, core_errors = read_core(repo)
        state, state_errors = read_state(repo)
        issues = [f"PROJECT_CORE: {item}" for item in core_errors] + [
            f"CURRENT_STAGE: {item}" for item in state_errors
        ]
        if core and state:
            context = (
                f"Use $codex-research-workflow. Authorities: AGENTS.md, {CORE_REL.as_posix()}, "
                f"{STATE_REL.as_posix()}. Verify Git. Project={state['project']}; "
                f"direction={core['primary_direction']}; gate={state['current_gate']}; "
                f"next={state['next_action']}."
            )
        else:
            context = (
                f"Use $codex-research-workflow. Read AGENTS.md, {CORE_REL.as_posix()}, and "
                f"{STATE_REL.as_posix()}; authority is incomplete, so do not infer state from chat."
            )
        emit(system_message=" | ".join(issues), context=context, event=event)
        return 0

    if event == "SubagentStart":
        emit(
            context=(
                "You are a fresh research reviewer. Review only the supplied base and candidate SHAs. "
                "Do not edit. Return P0/P1/P2 findings and ACCEPT, ACCEPT_WITH_P2, REJECT, or BLOCKED."
            ),
            event=event,
        )
        return 0

    if event == "SubagentStop":
        emit(
            system_message=(
                "If this was an explicitly authorized formal promotion review, record it once with "
                "$codex-research-workflow. Ordinary exploratory review creates no review-state transaction."
            ),
            event=event,
        )
        return 0

    command = command_text(payload)
    if event == "PreToolUse" and has_git_action(command, "push"):
        warnings = []
        for rel in (CORE_REL, STATE_REL):
            if git(repo, "status", "--short", "--", rel.as_posix(), check=False):
                warnings.append(f"{rel.as_posix()} has uncommitted changes")
        if warnings:
            emit(system_message="Workflow warning: " + "; ".join(warnings), event=event)
        return 0

    if event == "PostToolUse" and has_git_action(command, "commit") and core_changed(repo):
        emit(
            system_message=(
                "PROJECT_CORE changed. If the commit replaces, terminates, rejects, or supersedes a "
                "primary direction, use $research-artifact-cleanup to create a read-only plan and "
                "stop for user approval; wording-only changes do not trigger cleanup."
            ),
            event=event,
        )
        return 0

    if event == "Stop":
        _, core_errors = read_core(repo)
        _, state_errors = read_state(repo)
        issues = [f"PROJECT_CORE: {item}" for item in core_errors] + [
            f"CURRENT_STAGE: {item}" for item in state_errors
        ]
        git_dir = git(repo, "rev-parse", "--git-dir", check=False).strip()
        if git_dir:
            git_path = Path(git_dir)
            if not git_path.is_absolute():
                git_path = repo / git_path
            if (git_path / "index.lock").exists():
                issues.append("Git index.lock exists")
        if issues:
            emit(system_message="Workflow state warning: " + "; ".join(issues), event=event)
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        return handle(payload if isinstance(payload, dict) else {})
    except Exception:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
