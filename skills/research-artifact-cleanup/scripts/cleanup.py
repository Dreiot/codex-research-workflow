#!/usr/bin/env python3
"""Plan and apply explicit, state-bound research-artifact cleanup transactions."""

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


CLASSES = {
    "keep_formal_evidence",
    "keep_negative_evidence",
    "keep_active",
    "delete_reproducible",
    "delete_technical_failure",
    "unknown",
}
DELETE_CLASSES = {"delete_reproducible", "delete_technical_failure"}
KEEP_CLASSES = CLASSES - DELETE_CLASSES
CORE_REL = Path("docs/PROJECT_CORE.md")
PLAN_SCHEMA = "research-artifact-cleanup-plan/v1"
RECORD_SCHEMA = "research-artifact-cleanup-record/v2"


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


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = run(["git", "-C", str(repo), *args])
    if check and result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().replace(microsecond=0).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value: Dict[str, Any]) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def resolve_repo(value: str) -> Path:
    repo = Path(value).resolve()
    result = run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"])
    if result.returncode != 0 or Path(result.stdout.strip()).resolve() != repo:
        raise ValueError("cleanup requires one project root that is also the exact Git root")
    if git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("cleanup planning requires a clean worktree")
    return repo


def relative_path(value: str, label: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or path == Path("."):
        raise ValueError(f"{label} must be a non-root repository-relative path")
    return path


def inside(repo: Path, rel: Path) -> Path:
    resolved = (repo / rel).resolve()
    try:
        resolved.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {rel.as_posix()}") from exc
    return resolved


def tree_state(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise ValueError(f"artifact does not exist: {path}")
    files = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
    digest = hashlib.sha256()
    total = 0
    for item in files:
        rel = item.name if path.is_file() else item.relative_to(path).as_posix()
        stat = item.stat()
        total += stat.st_size
        digest.update(rel.encode("utf-8"))
        digest.update(str(stat.st_size).encode("ascii"))
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
    return {
        "kind": "file" if path.is_file() else "directory",
        "files": len(files),
        "bytes": total,
        "metadata_sha256": digest.hexdigest(),
    }


def experiment_root(repo: Path) -> Path:
    agents = repo / "AGENTS.md"
    if agents.is_file():
        import re

        match = re.search(r"(?im)^\s*-?\s*Experiment root:\s*`([^`]+)`", agents.read_text(encoding="utf-8", errors="replace"))
        if match:
            return relative_path(match.group(1).strip(), "Experiment root")
    return Path("experiments")


def references(repo: Path, rel: Path) -> List[str]:
    result = run(["git", "-C", str(repo), "grep", "-l", "-F", rel.as_posix(), "--", ":(exclude)" + rel.as_posix()])
    return sorted(
        line
        for line in result.stdout.splitlines()
        if line.strip() and Path(line).name != ".gitignore"
    )


def tracked(repo: Path, rel: Path) -> List[str]:
    return sorted(git(repo, "ls-files", "--", rel.as_posix(), check=False).splitlines())


def ignored(repo: Path, rel: Path) -> bool:
    return run(["git", "-C", str(repo), "check-ignore", "--no-index", "--quiet", rel.as_posix()]).returncode == 0


def build_plan(repo: Path, decisions: Dict[str, Any]) -> Dict[str, Any]:
    raw_items = decisions.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise ValueError("decisions JSON requires a non-empty items array")
    items: List[Dict[str, Any]] = []
    seen: List[Path] = []
    for index, raw in enumerate(raw_items, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"item {index} must be an object")
        rel = relative_path(str(raw.get("path", "")), f"item {index} path")
        classification = raw.get("classification")
        action = raw.get("action", "keep")
        reason = raw.get("reason")
        if classification not in CLASSES:
            raise ValueError(f"item {index} has invalid classification")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"item {index} requires a reason")
        if classification in DELETE_CLASSES and action != "delete":
            raise ValueError(f"item {index}: delete classifications require action=delete")
        if classification in KEEP_CLASSES and action not in {"keep", "relocate"}:
            raise ValueError(f"item {index}: retained classifications allow keep or relocate only")
        target_rel: Optional[Path] = None
        if action == "relocate":
            target_rel = relative_path(str(raw.get("target", "")), f"item {index} target")
        for prior in seen:
            if rel == prior or rel in prior.parents or prior in rel.parents:
                raise ValueError(f"overlapping cleanup paths: {prior.as_posix()} and {rel.as_posix()}")
        seen.append(rel)
        source = inside(repo, rel)
        item = {
            "path": rel.as_posix(),
            "classification": classification,
            "action": action,
            "target": target_rel.as_posix() if target_rel else None,
            "reason": reason.strip(),
            "state": tree_state(source),
            "tracked": tracked(repo, rel),
            "ignored": ignored(repo, rel),
            "references": references(repo, rel),
        }
        items.append(item)
    head = git(repo, "rev-parse", "HEAD")
    core_commit = git(repo, "log", "-1", "--format=%H", "--", CORE_REL.as_posix(), check=False) or None
    plan: Dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "repo": str(repo),
        "created_at": now_iso(),
        "head": head,
        "project_core_commit": core_commit,
        "important": bool(decisions.get("important", False)),
        "items": items,
    }
    identity = dict(plan)
    identity.pop("created_at")
    plan["plan_id"] = "cleanup-" + canonical_hash(identity)[:16]
    plan["execution"] = {"relocate": [], "delete": [], "verified": False, "failures": []}
    return plan


def save(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command_plan(args: argparse.Namespace) -> int:
    try:
        repo = resolve_repo(args.repo)
        decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
        plan = build_plan(repo, decisions)
        root = experiment_root(repo)
        output_rel = relative_path(args.output, "output") if args.output else root / ".tmp" / "cleanup" / f"{plan['plan_id']}.json"
        if not ignored(repo, output_rel):
            raise ValueError(f"cleanup plan must be ignored by Git: {output_rel.as_posix()}")
        output = inside(repo, output_rel)
        if output.exists():
            raise ValueError(f"cleanup plan already exists: {output_rel.as_posix()}")
        save(output, plan)
        totals: Dict[str, Dict[str, int]] = {}
        for item in plan["items"]:
            bucket = totals.setdefault(item["classification"], {"items": 0, "files": 0, "bytes": 0})
            bucket["items"] += 1
            bucket["files"] += item["state"]["files"]
            bucket["bytes"] += item["state"]["bytes"]
        print(json.dumps({"plan_id": plan["plan_id"], "plan": output_rel.as_posix(), "head": plan["head"], "project_core_commit": plan["project_core_commit"], "totals": totals, "items": plan["items"]}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


def verify_identity(repo: Path, plan: Dict[str, Any], plan_id: str) -> None:
    if plan.get("schema") != PLAN_SCHEMA or plan.get("plan_id") != plan_id:
        raise ValueError("plan schema or approved plan ID mismatch")
    if Path(str(plan.get("repo"))).resolve() != repo:
        raise ValueError("plan belongs to a different repository")
    if git(repo, "rev-parse", "HEAD") != plan.get("head"):
        raise ValueError("Git HEAD changed since planning")
    core_commit = git(repo, "log", "-1", "--format=%H", "--", CORE_REL.as_posix(), check=False) or None
    if core_commit != plan.get("project_core_commit"):
        raise ValueError("PROJECT_CORE base changed since planning")


def verify_state(path: Path, expected: Dict[str, Any]) -> None:
    if tree_state(path) != expected:
        raise ValueError(f"artifact changed since planning: {path}")


def delete_failure_inside(plan: Dict[str, Any], source: Path) -> bool:
    def normalized(value: Any) -> str:
        return str(value).replace("\\\\", "\\").replace("\\", "/").casefold()

    source_text = normalized(source)
    return any(
        failure.get("phase") == "delete"
        and source_text in normalized(failure.get("error", ""))
        for failure in plan["execution"]["failures"]
    )


def clear_readonly_and_retry(function: Any, path: str, exc_info: Tuple[Any, Any, Any]) -> None:
    if not isinstance(exc_info[1], PermissionError):
        raise exc_info[1]
    os.chmod(path, stat.S_IWRITE)
    function(path)


def apply_relocate(repo: Path, plan: Dict[str, Any]) -> None:
    done = set(plan["execution"]["relocate"])
    for item in plan["items"]:
        if item["action"] != "relocate" or item["path"] in done:
            continue
        source = inside(repo, Path(item["path"]))
        target = inside(repo, Path(item["target"]))
        verify_state(source, item["state"])
        if target.exists():
            raise ValueError(f"relocation target already exists: {item['target']}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
        verify_state(target, item["state"])
        plan["execution"]["relocate"].append(item["path"])


def apply_delete(repo: Path, plan: Dict[str, Any]) -> None:
    done = set(plan["execution"]["delete"])
    for item in plan["items"]:
        if item["action"] != "delete" or item["path"] in done:
            continue
        if item["classification"] not in DELETE_CLASSES:
            raise ValueError(f"non-deletable classification: {item['classification']}")
        source = inside(repo, Path(item["path"]))
        try:
            verify_state(source, item["state"])
        except ValueError:
            if not delete_failure_inside(plan, source):
                raise
        live_refs = references(repo, Path(item["path"]))
        if live_refs:
            raise ValueError(f"tracked references remain for {item['path']}: {', '.join(live_refs)}")
        if source.is_dir():
            shutil.rmtree(source, onerror=clear_readonly_and_retry)
        elif source.exists():
            source.unlink()
        plan["execution"]["delete"].append(item["path"])


def apply_verify(repo: Path, plan: Dict[str, Any]) -> None:
    for item in plan["items"]:
        source = inside(repo, Path(item["path"]))
        if item["action"] == "keep":
            verify_state(source, item["state"])
        elif item["action"] == "relocate":
            if source.exists():
                raise ValueError(f"relocated source still exists: {item['path']}")
            verify_state(inside(repo, Path(item["target"])), item["state"])
        elif source.exists():
            raise ValueError(f"deleted source still exists: {item['path']}")
    plan["execution"]["verified"] = True
    if plan.get("important"):
        root = experiment_root(repo)
        record_rel = root / "registry" / "cleanup" / f"{plan['plan_id']}.json"
        inventory = [
            {key: item[key] for key in ("path", "classification", "action", "target", "reason")}
            for item in plan["items"]
        ]
        totals: Dict[str, Dict[str, int]] = {}
        groups: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        for item in plan["items"]:
            classification = item["classification"]
            bucket = totals.setdefault(classification, {"items": 0, "files": 0, "bytes": 0})
            bucket["items"] += 1
            bucket["files"] += item["state"]["files"]
            bucket["bytes"] += item["state"]["bytes"]
            key = (classification, item["action"], item["reason"])
            group = groups.setdefault(
                key,
                {
                    "classification": classification,
                    "action": item["action"],
                    "reason": item["reason"],
                    "files": 0,
                    "bytes": 0,
                    "paths": [],
                },
            )
            group["files"] += item["state"]["files"]
            group["bytes"] += item["state"]["bytes"]
            path_entry = {"path": item["path"]}
            if item["target"] is not None:
                path_entry["target"] = item["target"]
            group["paths"].append(path_entry)
        record = {
            "schema": RECORD_SCHEMA,
            "cleanup_id": plan["plan_id"],
            "verified_at": now_iso(),
            "base_head": plan["head"],
            "project_core_commit": plan["project_core_commit"],
            "inventory_sha256": canonical_hash({"items": inventory}),
            "totals": totals,
            "groups": list(groups.values()),
        }
        save(inside(repo, record_rel), record)


def command_apply(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    try:
        repo = Path(args.repo).resolve()
        result = run(["git", "-C", str(repo), "rev-parse", "--show-toplevel"])
        if result.returncode != 0 or Path(result.stdout.strip()).resolve() != repo:
            raise ValueError("cleanup requires one project root that is also the exact Git root")
        if plan_path.is_absolute():
            resolved_plan = plan_path.resolve()
            resolved_plan.relative_to(repo)
        else:
            resolved_plan = inside(repo, relative_path(args.plan, "plan"))
        plan = json.loads(resolved_plan.read_text(encoding="utf-8"))
        verify_identity(repo, plan, args.plan_id)
        if args.phase == "relocate":
            apply_relocate(repo, plan)
        elif args.phase == "delete":
            apply_delete(repo, plan)
        else:
            apply_verify(repo, plan)
        save(resolved_plan, plan)
        if args.phase == "verify" and plan["execution"]["verified"]:
            resolved_plan.unlink()
        print(json.dumps({"status": "complete", "phase": args.phase, "plan_id": args.plan_id, "execution": plan["execution"]}, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        try:
            if "plan" in locals() and "resolved_plan" in locals():
                plan["execution"]["failures"].append({"phase": args.phase, "at": now_iso(), "error": str(exc)})
                save(resolved_plan, plan)
        except Exception:
            pass
        print(str(exc), file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--repo", default=".")
    plan.add_argument("--decisions", required=True)
    plan.add_argument("--output")
    plan.set_defaults(func=command_plan)
    apply = sub.add_parser("apply")
    apply.add_argument("--repo", default=".")
    apply.add_argument("--plan", required=True)
    apply.add_argument("--plan-id", required=True)
    apply.add_argument("--phase", choices=("relocate", "delete", "verify"), required=True)
    apply.set_defaults(func=command_apply)
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))
