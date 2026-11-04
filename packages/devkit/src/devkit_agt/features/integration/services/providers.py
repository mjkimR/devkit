"""Git policy normalization and local-only scoped post-finish extensions."""

from __future__ import annotations

from importlib import metadata
from pathlib import Path
from typing import Any, cast

from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project import development_approach
from devkit_dist.features.project.repositories.project import commit_config as committed_config
from devkit_dist.features.project.repositories.project import read_project_config

from devkit_agt.features.integration.models.contracts import (
    CleanupScope,
    CleanupTarget,
    IntegrationContext,
    ScopedCleanup,
    digest,
)
from devkit_agt.features.integration.models.errors import (
    CleanupContractError,
    IntegrationConfigError,
)

CONFIG_PATH = ".devkit/config.toml"
POST_FINISH_GROUP = "devkit.post_finish"


def effective(config: dict[str, Any]) -> dict[str, Any]:
    """The integration policy devkit owns, normalized with its defaults (``ADR-effective-policy-digest``).

    Asset hashes, the receipt and keys other packages own are not part of Git approval policy.
    """

    def table(value: object, key: str) -> dict[str, Any]:
        found = value.get(key) if isinstance(value, dict) else None
        return found if isinstance(found, dict) else {}

    legacy = config.get("integration", {})
    if not isinstance(legacy, dict) or set(legacy) - {"provider"}:
        raise IntegrationConfigError(
            "integration accepts only the ignored legacy provider key",
            target_files=[CONFIG_PATH],
            fix="Remove unknown keys from [integration]; provider selection is no longer required",
        )
    approvals = table(table(config, "workflow"), "approvals")
    worktree = table(config, "worktree")
    return {
        "dev-integration": approvals.get("dev-integration", "ask"),
        "pull_request": worktree.get("pull_request", "auto"),
        "delete_branch": worktree.get("delete_branch", True),
        "merge": worktree.get("merge", "no-ff"),
        "development_approach": development_approach(config).approach,
    }


def approval(config: dict[str, Any], gate: str) -> str:
    """Read an owning decision policy with validated table shapes."""
    workflow = config.get("workflow", {})
    approvals = workflow.get("approvals", {}) if isinstance(workflow, dict) else None
    value = approvals.get(gate, "ask") if isinstance(approvals, dict) else None
    if value not in ("ask", "auto"):
        raise IntegrationConfigError(f"{gate} requires ask or auto in workflow.approvals")
    return value


def policy_digest(config: dict[str, Any]) -> str:
    return digest(effective(config))


def current_policy(root: Path) -> str:
    """The effective policy digest of the checkout at ``root`` (its working-tree ``.devkit/config.toml``)."""
    path = root / CONFIG_PATH
    if path.is_symlink():
        raise IntegrationConfigError("integration policy files must be regular files", target_files=[CONFIG_PATH])
    return policy_digest(read_project_config(root))


def commit_config(root: Path, sha: str) -> dict[str, Any] | None:
    """The parsed ``.devkit/config.toml`` committed at ``sha``; ``None`` when the commit has none."""
    try:
        return committed_config(root, sha)
    except ConfigError as exc:
        raise IntegrationConfigError(f"commit {sha[:12]} contains an invalid integration policy") from exc


def policy(root: Path) -> str:
    """Validate merge policy; provider is accepted only as an ignored legacy key."""
    config = read_project_config(root)
    approval(config, "dev-integration")
    return current_policy(root)


def identity(entry: metadata.EntryPoint) -> str:
    dist = entry.dist
    package = f"{dist.name}=={dist.version}" if dist is not None else "unversioned"
    return f"{entry.name}:{entry.value}@{package}"


def cleanup_extensions() -> dict[str, tuple[str, ScopedCleanup]]:
    found: dict[str, tuple[str, ScopedCleanup]] = {}
    for entry in sorted(metadata.entry_points(group=POST_FINISH_GROUP), key=lambda item: (item.name, item.value)):
        try:
            extension = entry.load()
            if (
                entry.name in found
                or getattr(extension, "integration_local_only", None) is not True
                or not all(
                    callable(getattr(extension, method, None))
                    for method in ("integration_plan", "integration_validate", "integration_run")
                )
            ):
                raise TypeError("scoped local-only contract required")
            found[entry.name] = (identity(entry), cast(ScopedCleanup, extension))
        except Exception as exc:
            raise CleanupContractError(
                f"post-finish extension {entry.name} cannot execute within an approved scope ({type(exc).__name__})"
            ) from exc
    return found


def cleanup_scopes(
    context: IntegrationContext, extensions: dict[str, tuple[str, ScopedCleanup]]
) -> tuple[CleanupScope, ...]:
    scopes = []
    for name, (ident, extension) in extensions.items():
        targets = extension.integration_plan(context)
        if not isinstance(targets, tuple) or not all(
            isinstance(target, CleanupTarget)
            and all(isinstance(value, str) and value for value in (target.kind, target.identity, target.revision))
            for target in targets
        ):
            raise CleanupContractError(f"extension {name} must declare exact cleanup identities and revisions")
        if len(set(targets)) != len(targets):
            raise CleanupContractError(f"extension {name} declared duplicate cleanup targets")
        extension.integration_validate(context, targets)
        scopes.append(CleanupScope(name, ident, targets))
    return tuple(scopes)
