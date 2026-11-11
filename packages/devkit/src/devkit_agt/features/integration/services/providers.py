"""Git policy normalization, local-only scoped post-finish extensions and the checks both routes repeat before
and after Git effects."""

from __future__ import annotations

import sys
from collections.abc import Collection
from importlib import metadata
from pathlib import Path
from typing import Any, cast

from devkit_core.core.extensions import ExtensionFailed, call_extensions
from devkit_dist.base.errors import ConfigError
from devkit_dist.features.project import development_approach
from devkit_dist.features.project.repositories.project import commit_config as committed_config
from devkit_dist.features.project.repositories.project import read_project_config

from devkit_agt.features.integration.models.contracts import (
    CleanupScope,
    CleanupTarget,
    IntegrationContext,
    IntegrationRequest,
    ScopedCleanup,
    digest,
)
from devkit_agt.features.integration.models.errors import (
    CleanupContractError,
    IntegrationConfigError,
    StaleRequestError,
)
from devkit_agt.features.worktree import POLICY_DEFAULTS, worktree_policy

CONFIG_PATH = ".devkit/config.toml"
POST_FINISH_GROUP = "devkit.post_finish"


def effective(config: dict[str, Any]) -> dict[str, Any]:
    """The integration policy devkit owns, normalized with its defaults (``ADR-effective-policy-digest``).

    Asset hashes, the receipt and keys other packages own are not part of Git approval policy.
    """

    def table(value: object, key: str) -> dict[str, Any]:
        found = value.get(key) if isinstance(value, dict) else None
        return found if isinstance(found, dict) else {}

    reserved = config.get("integration", {})
    if not isinstance(reserved, dict):
        raise IntegrationConfigError(
            "integration must be a table",
            target_files=[CONFIG_PATH],
            fix="Remove [integration] or leave it empty; it accepts no keys",
        )
    if "provider" in reserved:
        raise IntegrationConfigError(
            "integration key provider is retired",
            target_files=[CONFIG_PATH],
            fix="Delete provider from [integration]; the readiness-provider selection is retired",
        )
    if reserved:
        keys = ", ".join(sorted(reserved))
        raise IntegrationConfigError(
            f"integration accepts no keys: {keys}",
            target_files=[CONFIG_PATH],
            fix=f"Remove {keys} from [integration]; it accepts no keys",
        )
    approvals = table(table(config, "workflow"), "approvals")
    return {
        "dev-integration": approvals.get("dev-integration", "ask"),
        **(worktree_policy(config) or POLICY_DEFAULTS),
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
    """Validate merge policy and return its effective digest."""
    config = read_project_config(root)
    approval(config, "dev-integration")
    return current_policy(root)


def identity(entry: metadata.EntryPoint) -> str:
    dist = entry.dist
    package = f"{dist.name}=={dist.version}" if dist is not None else "unversioned"
    return f"{entry.name}:{entry.value}@{package}"


def cleanup_extensions() -> dict[str, tuple[str, ScopedCleanup]]:
    """Every ``devkit.post_finish`` extension by name with its identity; ``CleanupContractError`` at the first one
    that fails to load or lacks the scoped local-only contract, a duplicate name, or a group that cannot be listed
    (named ``discovery``)."""
    seen: set[str] = set()

    def scoped(entry: metadata.EntryPoint) -> tuple[str, ScopedCleanup]:
        extension = entry.load()
        if (
            entry.name in seen
            or getattr(extension, "integration_local_only", None) is not True
            or not all(
                callable(getattr(extension, method, None))
                for method in ("integration_plan", "integration_validate", "integration_run")
            )
        ):
            raise TypeError("scoped local-only contract required")
        seen.add(entry.name)
        return identity(entry), cast(ScopedCleanup, extension)

    found: dict[str, tuple[str, ScopedCleanup]] = {}
    for outcome in call_extensions(POST_FINISH_GROUP, scoped, fail_fast=True):
        if isinstance(outcome, ExtensionFailed):
            raise CleanupContractError(
                f"post-finish extension {outcome.name} cannot execute within an approved scope"
                f" ({type(outcome.error).__name__})"
            ) from outcome.error
        found[outcome.name] = outcome.result
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


def revalidate_cleanup(
    request: IntegrationRequest, context: IntegrationContext, done: Collection[str], *, changed: str
) -> None:
    """Refuse with ``StaleRequestError(changed)`` when the installed post-finish extensions differ from the approved
    ones; otherwise revalidate the approved targets of every scope whose cleanup is not in ``done``."""
    extensions = cleanup_extensions()
    if {name: ident for name, (ident, _) in extensions.items()} != {
        scope.extension: scope.identity for scope in request.cleanup
    }:
        raise StaleRequestError(changed)
    for scope in request.cleanup:
        if scope.extension not in done:
            extensions[scope.extension][1].integration_validate(context, scope.targets)


def runtime_in(path: str | Path) -> bool:
    """Whether the running interpreter lives inside ``path``, the worktree an approved cleanup removes."""
    return Path(sys.executable).absolute().is_relative_to(path) or Path(sys.prefix).resolve().is_relative_to(path)
