"""Collect read-only worker evidence; the Host retains every acceptance decision."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from devkit.advisory import AdvisoryError, Level
from devkit_agt.features.workflow.repositories.git import is_ancestor
from devkit_core.core import FrontmatterError, run_git

from devkit_spec.base.errors import SpecError
from devkit_spec.features.worker.usecases.inputs import ScopeUnresolved, derive_scope, git, inputs, prefix, records


class CheckNotRun(SpecError):
    code = "WORKER_CHECK_NOT_RUN"
    level = Level.NOTICE
    fix = "Inspect the reported cause and run the named check after correcting it"


def run_check(root: Path, args: Sequence[str]) -> dict[str, Any]:
    """Keep the wrapped command's result and advisory output intact."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "devkit_dist", *args, "--format", "json"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return {"status": "not-run", "cause": str(exc)}
    try:
        payload = json.loads(result.stdout)
    except ValueError:
        payload = {"stdout": result.stdout}
        if result.returncode == 0:
            return {
                "status": "not-run",
                "cause": "Wrapped check returned no JSON result",
                "result": payload,
                "stderr": result.stderr,
            }
    return {
        "status": "pass" if result.returncode == 0 else "fail" if result.returncode == 1 else "not-run",
        "exit_code": result.returncode,
        "result": payload,
        "stderr": result.stderr,
    }


def dirty_paths(root: Path) -> list[str]:
    # -z avoids quoting and also carries both sides of rename/copy entries.
    values = os.fsdecode(
        run_git(root, "--no-optional-locks", "status", "--porcelain=v1", "-z", "--untracked-files=all")
    ).split("\0")
    paths = []
    index = 0
    while index < len(values):
        item = values[index]
        index += 1
        if not item:
            continue
        paths.append(item[3:])
        if "R" in item[:2] or "C" in item[:2]:
            if index < len(values) and values[index]:
                paths.append(values[index])
            index += 1
    return sorted(set(paths))


def inspect(
    root: Path,
    *,
    unit: str | None = None,
    base: str | None = None,
    head: str | None = None,
    scope: Sequence[str] | None = None,
    base_checkout: str | None = None,
    details: bool = True,
    runner: Callable[[Path, Sequence[str]], dict[str, Any]] = run_check,
) -> dict[str, Any]:
    root, tip, chosen = inputs(root, unit, base, head, base_checkout)
    unit = str(chosen["unit"]["value"])
    base, head = str(chosen["base"]["value"]), str(chosen["head"]["value"])
    checks: dict[str, Any] = {}
    notices: list[dict[str, Any]] = []
    result: dict[str, Any] = {"inputs": chosen, "base": base, "head": head, "checks": checks, "notices": notices}
    checks["ancestry"] = {"status": "pass" if is_ancestor(root, base, head) else "fail"}
    checks["head"] = {"status": "pass" if tip == head else "fail", "actual": tip}
    # Disable rename detection so both removed and added names are checked against the scope.
    changed = [
        p
        for p in os.fsdecode(run_git(root, "diff", "--no-renames", "--name-only", "-z", base, head, "--")).split("\0")
        if p
    ]
    result["changed_paths"] = changed
    if scope is not None:
        scope = [prefix(p) for p in scope]
    try:
        entries = (
            [{"path": prefix(p), "source": "argument"} for p in scope]
            if scope is not None
            else derive_scope(root, tip, unit)
        )
        result["scope"] = entries
        outside = [
            p
            for p in changed
            if not any(e["path"] == "." or p == e["path"] or p.startswith(e["path"] + "/") for e in entries)
        ]
        result["outside_scope"] = outside
        checks["scope"] = {"status": "fail" if outside else "pass"}
    except (AdvisoryError, FrontmatterError, UnicodeError) as exc:
        cause = exc.to_dict() if isinstance(exc, AdvisoryError) else ScopeUnresolved(str(exc)).to_dict()
        result["scope"] = []
        checks["scope"] = {"status": "not-run", "cause": cause}
    dirty = dirty_paths(root)
    checks["worktree"] = {"status": "fail" if dirty else "pass", "dirty_paths": dirty}
    loaded = records(root, tip, unit)
    checks["envelopes"] = {
        "status": "fail" if loaded.errors or loaded.unresolved_problems() or loaded.pending_questions() else "pass",
        "result": loaded.inspection_dict(details=details),
    }
    checks["rules"] = (
        runner(root, ["rules", "check", "--ci", "--base", base])
        if tip == head
        else {"status": "not-run", "cause": "Worktree HEAD differs from returned head"}
    )
    checks["workflow"] = (
        {"status": "not-run", "cause": "Working tree differs from committed HEAD; workflow next reads disk"}
        if dirty
        else runner(root, ["workflow", "next", "--unit", unit])
    )
    checkout = chosen["base_checkout"]["value"]
    if checkout:
        path = Path(checkout)
        result["base_checkout"] = {"head": git(path, "rev-parse", "HEAD"), "dirty_paths": dirty_paths(path)}
    for name, check in checks.items():
        if check["status"] == "not-run":
            notices.append(
                CheckNotRun(f"{name}: {check.get('cause', check.get('stderr', 'check could not run'))}").to_dict()
            )
    result["exit_code"] = int(any(c["status"] == "fail" for c in checks.values()))
    return result
