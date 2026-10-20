"""Personal rendering evidence; canonical receipts remain unchanged."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import tomlkit

from devkit.advisory import ExitCode
from devkit.core.errors import ConfigError, GitError
from devkit.core.git import run_git
from devkit.core.local_config import LOCAL_CONFIG_PATH, read_effective_config, read_local_config
from devkit.core.project import git_toplevel
from devkit.core.receipt import CONFIG_PATH, RECEIPT_PATH, FileRecord, Receipt
from devkit.distribution.content import Content, json_content, signature
from devkit.distribution.installation.inventory import Inventory
from devkit.distribution.installation.results import Action
from devkit.distribution.installation.workspace import snapshot

LOCAL_RENDER = ".devkit/transient/local-render.json"
ELIGIBLE = {"skill", "instruction", "subagent", "playbook"}


class LocalNotIgnoredError(ConfigError):
    code = "CONFIG_LOCAL_NOT_IGNORED"


class LocalRenderForbiddenError(ConfigError):
    code = "CONFIG_LOCAL_RENDER_FORBIDDEN"
    fix = "Remove the local variable override or separate its shared use in the bundle template"


class LocalRenderStaleError(ConfigError):
    code = "CONFIG_LOCAL_RENDER_STALE"
    input_error = False
    exit_code = ExitCode.FINDINGS
    fix = "Run `devkit sync` in this workspace to refresh personal rendering evidence"


class LocalChangedError(ConfigError):
    code = "CONFIG_LOCAL_CHANGED"
    input_error = False
    exit_code = ExitCode.FINDINGS
    fix = "Rerun `devkit sync` after configuration edits finish"


def inputs(root: Path) -> dict[str, bytes | None]:
    read_effective_config(root)
    return {
        name: (root / name).read_bytes() if (root / name).exists() else None
        for name in (CONFIG_PATH, LOCAL_CONFIG_PATH)
    }


def unchanged(root: Path, before: dict[str, bytes | None]) -> None:
    try:
        current = {name: (root / name).read_bytes() if (root / name).exists() else None for name in before}
        changed = current != before or any((root / name).is_symlink() for name in before)
    except OSError:
        changed = True
    if changed:
        raise LocalChangedError(
            "shared or local configuration changed during planning",
            target_files=[str(root / name) for name in before],
        )


def variables_digest(root: Path) -> str:
    config = read_effective_config(root).values
    values = {"bundles": config.get("bundles", {}), "presentation": config["presentation"]}
    return hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def require_ignored(root: Path, name: str, *, planned_ignore: bool = False) -> None:
    if git_toplevel(root) is None:
        # Without an index there can be no tracked personal output. The managed ignore file is still planned.
        return
    tracked = bool(run_git(root, "ls-files", "--", name).strip())
    ignored = False
    try:
        ignored = bool(run_git(root, "check-ignore", "--no-index", "--", name).strip())
    except GitError as exc:
        if exc.returncode != 1:
            raise
    if tracked or (not ignored and not planned_ignore):
        fix = (
            f"git rm --cached -- {name}; add an effective ignore rule for {name}"
            if tracked
            else (f"Remove the negation or add an effective ignore rule for {name} in the applicable .gitignore")
        )
        raise LocalNotIgnoredError(
            f"{root / name}: personal state must be ignored and untracked", target_files=[str(root / name)], fix=fix
        )


def personal_files(root: Path, canonical: Inventory, effective: Inventory) -> dict[str, Content]:
    if (
        any(
            getattr(canonical, attr) != getattr(effective, attr)
            for attr in ("assets", "packages", "seeds", "guidance", "host_hooks", "projections")
        )
        or canonical.files.keys() != effective.files.keys()
    ):
        raise LocalRenderForbiddenError("local variables changed shared inventory structure, seeds or guidance")
    allowed = {path for asset in canonical.assets if asset.kind in ELIGIBLE for path in asset.paths}
    changed = {}
    for name, content in effective.files.items():
        before = canonical.files[name]
        if before == content:
            continue
        if name not in allowed or content.mode != before.mode:
            raise LocalRenderForbiddenError(f"local variables changed forbidden output: {name}", target_files=[name])
        changed[name] = content
    return changed


def plan_environment(
    root: Path, environment: str | None, changes: dict[str, Content | None], actions: list[Action]
) -> None:
    if environment is None:
        return
    before = snapshot(root, LOCAL_CONFIG_PATH)
    document = tomlkit.parse(before.data.decode() if before else "")
    execution = document.setdefault("execution", {})
    execution["environment"] = environment
    after = Content(tomlkit.dumps(document).encode(), before.mode if before else 0o644)
    if after != before:
        changes[LOCAL_CONFIG_PATH] = after
        actions.append(Action(LOCAL_CONFIG_PATH, "update" if before else "create"))


def plan_ledger(
    root: Path,
    personal: dict[str, Content],
    receipt_bytes: bytes,
    changes: dict[str, Content | None],
    actions: list[Action],
) -> None:
    before = snapshot(root, LOCAL_RENDER)
    local = read_local_config(root)
    active = bool(local.get("bundles") or local.get("presentation"))
    after = (
        json_content(
            {
                "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest(),
                "variables_sha256": variables_digest(root),
                "files": {
                    name: {"sha256": signature(content)[0], "mode": content.mode} for name, content in personal.items()
                },
            }
        )
        if active
        else None
    )
    if before != after:
        changes[LOCAL_RENDER] = after
        actions.append(Action(LOCAL_RENDER, "remove" if after is None else "update" if before else "create"))


def recorded_paths(root: Path) -> set[str]:
    """Prior personal destinations, used only to enforce ownership before restoration."""
    content = snapshot(root, LOCAL_RENDER)
    if content is None:
        return set()
    try:
        files = json.loads(content.data)["files"]
        return {name for name in files if isinstance(name, str)} if isinstance(files, dict) else set()
    except (ValueError, TypeError, KeyError):
        return set()


def runtime_receipt(root: Path, receipt: Receipt) -> Receipt:
    """Validate local evidence and return a runtime-only view, never used by engines or snapshots."""
    local = read_local_config(root)
    read_effective_config(root)
    content = snapshot(root, LOCAL_RENDER)
    if not (local.get("bundles") or local.get("presentation")) and content is None:
        return receipt
    try:
        data = json.loads(content.data) if content else {}
        if data["receipt_sha256"] != hashlib.sha256((root / RECEIPT_PATH).read_bytes()).hexdigest():
            raise ValueError("receipt changed")
        if data["variables_sha256"] != variables_digest(root):
            raise ValueError("variables changed")
        allowed = {path for asset in receipt.asset_records if asset.kind in ELIGIBLE for path in asset.paths}
        files = dict(receipt.file_records)
        for name, record in data["files"].items():
            if name not in allowed or name not in files or record["mode"] != files[name].mode:
                raise ValueError("ineligible local output")
            require_ignored(root, name)
            sha = record["sha256"]
            if not isinstance(sha, str) or len(sha) != 64:
                raise ValueError("invalid signature")
            files[name] = FileRecord(sha, record["mode"])
        return replace(receipt, file_records=files)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise LocalRenderStaleError(
            f"{root / LOCAL_RENDER}: missing or stale local evidence: {exc}", target_files=[str(root / LOCAL_RENDER)]
        ) from exc
