"""Explicit project provider selection and local-only post-finish extensions; all checks fail closed."""

from __future__ import annotations

import re
import tomllib
from importlib import metadata
from pathlib import Path
from typing import Any, cast

from devkit.advisory import AdvisoryError
from devkit.core.git import run_git
from devkit.core.project import read_project_config
from devkit.integration.errors import CleanupContractError, IntegrationConfigError, ProviderError, ReadinessError
from devkit.integration.models import (
    CleanupScope,
    CleanupTarget,
    IntegrationContext,
    Readiness,
    ReadinessProvider,
    ScopedCleanup,
    digest,
)

CONFIG_PATH = ".devkit/config.toml"
DISCLOSURE_LIMIT = 200
PROVIDER_GROUP = "devkit.integration.readiness"
POST_FINISH_GROUP = "devkit.post_finish"
GUARD_GROUP = "devkit.finish_guard"
CODE = re.compile(r"[A-Z][A-Z0-9_]*\Z")
NAME = re.compile(r"[a-z][a-z0-9-]*\Z")


def effective(config: dict[str, Any]) -> dict[str, Any]:
    """The integration policy devkit owns, normalized with its defaults (``ADR-effective-policy-digest``).

    Asset hashes, the receipt and keys other packages own are not part of it; a provider binds its own policy through
    its evidence.
    """

    def table(value: object, key: str) -> dict[str, Any]:
        found = value.get(key) if isinstance(value, dict) else None
        return found if isinstance(found, dict) else {}

    approvals = table(table(config, "workflow"), "approvals")
    worktree = table(config, "worktree")
    return {
        "dev-integration": approvals.get("dev-integration", "ask"),
        "pull_request": worktree.get("pull_request", "auto"),
        "delete_branch": worktree.get("delete_branch", True),
        "merge": worktree.get("merge", "no-ff"),
        "provider": table(config, "integration").get("provider"),
    }


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
    if not run_git(root, "ls-tree", "--name-only", sha, "--", CONFIG_PATH).strip():
        return None
    try:
        return tomllib.loads(run_git(root, "show", f"{sha}:{CONFIG_PATH}").decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise IntegrationConfigError(f"commit {sha[:12]} contains an invalid integration policy") from exc


def policy(root: Path) -> tuple[str, str]:
    """The configured provider name and the effective policy digest of the base checkout at ``root``."""
    config = read_project_config(root)
    table = config.get("integration")
    if (
        not isinstance(table, dict)
        or set(table) != {"provider"}
        or not isinstance(table["provider"], str)
        or not NAME.fullmatch(table["provider"])
    ):
        raise IntegrationConfigError(
            "integration requires exactly one configured provider name; there is no permissive fallback"
        )
    workflow = config.get("workflow", {})
    approvals = workflow.get("approvals", {}) if isinstance(workflow, dict) else None
    if not isinstance(approvals, dict) or approvals.get("dev-integration", "ask") not in {"ask", "auto"}:
        raise IntegrationConfigError(
            "integration requires dev-integration=ask or auto",
            fix="Use the existing integration path for the configured policy; do not change project approval policy to bypass this refusal",
        )
    return table["provider"], current_policy(root)


def identity(entry: metadata.EntryPoint) -> str:
    dist = entry.dist
    package = f"{dist.name}=={dist.version}" if dist is not None else "unversioned"
    return f"{entry.name}:{entry.value}@{package}"


def guards() -> tuple[str, ...]:
    return tuple(sorted(identity(entry) for entry in metadata.entry_points(group=GUARD_GROUP)))


def provider(name: str) -> tuple[str, ReadinessProvider]:
    entries = list(metadata.entry_points(group=PROVIDER_GROUP, name=name))
    if len(entries) != 1:
        raise ProviderError(f"provider {name} requires exactly one installed {PROVIDER_GROUP} entry point")
    try:
        value = entries[0].load()
        if not callable(getattr(value, "check", None)):
            raise TypeError("provider must expose check(context)")
        return identity(entries[0]), cast(ReadinessProvider, value)
    except Exception as exc:
        raise ProviderError(f"provider {name} could not load ({type(exc).__name__})") from exc


def check(value: ReadinessProvider, context: IntegrationContext) -> Readiness:
    """Run the provider; fail closed on a malformed result, refuse on reasons.

    The result must bind the context's source, target and result commits, carry nonempty coded evidence, declare its
    target-bound codes and a one-line result-check disclosure of 1 to ``DISCLOSURE_LIMIT`` characters.
    """
    try:
        result = value.check(context)
        if (
            not isinstance(result, Readiness)
            or result.source_sha != context.finish.source_sha
            or result.target_sha != context.finish.target_sha
            or result.result_sha != context.result_sha
        ):
            raise TypeError("readiness must bind the requested source, target and result SHAs")
        if not isinstance(result.target_bound, tuple) or not all(
            isinstance(code, str) and CODE.fullmatch(code) for code in result.target_bound
        ):
            raise TypeError("readiness must declare its target-bound evidence codes")
        if (
            not isinstance(result.disclosure, str)
            or not result.disclosure.strip()
            or len(result.disclosure) > DISCLOSURE_LIMIT
            or any(not char.isprintable() for char in result.disclosure)
        ):
            raise TypeError("readiness requires a one-line result-check disclosure of at most 200 characters")
        if (
            not isinstance(result.evidence, tuple)
            or not result.evidence
            or any(
                not CODE.fullmatch(item.code)
                or not isinstance(item.value, str)
                or not item.value
                or len(item.value) > 4096
                for item in result.evidence
            )
        ):
            raise TypeError("readiness requires nonempty coded evidence")
        if not isinstance(result.reasons, tuple) or not all(
            isinstance(reason, str) and reason for reason in result.reasons
        ):
            raise TypeError("readiness reasons must be a tuple of strings")
        if result.reasons:
            raise ReadinessError("the configured provider refused integration", *result.reasons)
        return result
    except AdvisoryError:
        raise
    except Exception as exc:
        raise ProviderError(f"readiness verification failed ({type(exc).__name__})") from exc


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
