"""devkit-spec's project policy: the ``[tool.spec]`` table of ``.devkit/config.toml``.

devkit passes ``[tool.<name>]`` tables through unread, so devkit-spec owns
this one. Policy that devkit already models stays in devkit's own tables:
approvals and stage switches in ``[workflow.approvals]`` and
``[workflow.stages]``, pull requests and branch cleanup in ``[worktree]``.

```toml
[tool.spec]
worktree = "auto"           # direct mode only: "auto" a separate worktree when the activity needs one; "required" always
depth_escalation = "auto"   # "auto": the Host raises planning-depth on its own; "ask": the user confirms each raise

[tool.spec.proposal_review]
auto_write = false         # default: explicit publication; true lets the agent write/publish before plan-accept

[tool.spec.feedback]
capture = "observed"       # concrete observations recorded autonomously; or requested-only
coverage = "repo"          # repository-owned tools and assets; or repo-and-upstream
detail = "standard"        # brief, standard or detailed
reminder = "contextual"    # contextual or off

[tool.spec.scope]          # the work-scope registry (devkit spec scope); every key is optional
shared_path = "/srv/scope" # absolute; default: devkit-spec-scope/ in the Git common directory
namespace = "team"         # default: a hash of the Git common directory
timeout = 10               # seconds per registry command, 1 to 300
```

``template`` is the ``devkit.config_template`` extension: ``devkit config template`` writes these tables into
``.devkit/config.toml`` as comments, each key at the default ``read_spec_config`` applies.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from devkit_dist.features.project.models.templates import TemplateKey, TemplateTable
from devkit_dist.features.project.repositories.project import read_project_config

from devkit_spec.base.errors import SpecConfigError
from devkit_spec.features.policy.models.config import SCOPE_TIMEOUT_DEFAULT, ScopeConfig

TABLE = "spec"
SCOPE_NAMESPACE = re.compile(r"^[A-Za-z0-9_-][A-Za-z0-9._-]*$")
SCOPE_TIMEOUT_RANGE = (1, 300)
WORKTREE_LEVELS = ("auto", "required")
DEPTH_ESCALATION = ("auto", "ask")
INTENT_GATE = "plan-intent"
APPROVAL_GATES = ("plan-accept", "proposal-handoff", "dev-integration")
"""Main business decision boundaries, independently delegated through ask or auto."""
INTEGRATION_GATE = "dev-integration"
INTEGRATION_POLICIES = ("ask", "auto")
FEEDBACK_CHOICES = {
    "capture": ("observed", "requested-only"),
    "coverage": ("repo", "repo-and-upstream"),
    "detail": ("brief", "standard", "detailed"),
    "reminder": ("contextual", "off"),
}


@dataclass(frozen=True)
class FeedbackConfig:
    """Repository-first observation policy consumed by the feedback skills through ``spec policy``."""

    capture: str = "observed"
    coverage: str = "repo"
    detail: str = "standard"
    reminder: str = "contextual"


@dataclass(frozen=True)
class SpecConfig:
    worktree: str = "auto"
    depth_escalation: str = "auto"
    scope: ScopeConfig = field(default=ScopeConfig())
    feedback: FeedbackConfig = field(default=FeedbackConfig())


def template() -> list[TemplateTable]:
    """``[tool.spec]`` and its tables for devkit's commented config template, at ``read_spec_config``'s defaults."""
    defaults = SpecConfig()
    low, high = SCOPE_TIMEOUT_RANGE
    return [
        TemplateTable(
            (
                TemplateKey(
                    "worktree",
                    defaults.worktree,
                    "direct mode only: whether a spec or proposal activity branch runs in a separate worktree; auto:"
                    " when the activity needs one; required: always (local-orchestrated always uses one)",
                    kind=" | ".join(f'"{level}"' for level in WORKTREE_LEVELS),
                ),
                TemplateKey(
                    "depth_escalation",
                    defaults.depth_escalation,
                    "auto: the Host raises planning-depth on its own judgment; ask: the user confirms each raise;"
                    " workers never raise it",
                    kind=" | ".join(f'"{value}"' for value in DEPTH_ESCALATION),
                ),
            ),
        ),
        TemplateTable(
            (
                TemplateKey(
                    "shared_path",
                    help="unset: devkit-spec-scope/ in the Git common directory; clones that share the path and the"
                    " namespace share one registry",
                    kind="string, an absolute directory (or one starting with ~)",
                    example="/srv/devkit-spec-scope",
                ),
                TemplateKey(
                    "namespace",
                    help="unset: a hash of the Git common directory",
                    kind="string of letters, digits, '.', '_' and '-', not starting with '.'",
                    example="team",
                ),
                TemplateKey(
                    "timeout",
                    defaults.scope.timeout,
                    "seconds one registry command may wait",
                    kind=f"integer from {low} to {high}",
                ),
            ),
            path=("scope",),
            help="The work-scope registry of `devkit spec scope`.",
        ),
        TemplateTable(
            tuple(
                TemplateKey(
                    key,
                    getattr(defaults.feedback, key),
                    help_text,
                    kind=" | ".join(f'"{choice}"' for choice in FEEDBACK_CHOICES[key]),
                )
                for key, help_text in (
                    (
                        "capture",
                        "observed records concrete observations autonomously; requested-only waits for explicit feedback requests",
                    ),
                    (
                        "coverage",
                        "repository-owned assets first; repo-and-upstream also covers tools used from upstream",
                    ),
                    (
                        "detail",
                        "brief: context and evidence; standard: kind-specific assessment; detailed: reproduction, versions and conditions",
                    ),
                    (
                        "reminder",
                        "contextual suggests a sweep for reusable observations; off disables optional reminders",
                    ),
                )
            ),
            path=("feedback",),
            help="Feedback capture policy; explicit user feedback requests override autonomous capture and coverage limits.",
        ),
    ]


def read_spec_config(root: Path) -> SpecConfig:
    """The ``[tool.spec]`` table of the project at ``root``; defaults when absent."""
    tool = read_project_config(root).get("tool", {})
    table = tool.get(TABLE, {}) if isinstance(tool, dict) else None
    if not isinstance(table, dict):
        raise SpecConfigError("config tool.spec: expected a table")
    unknown = sorted(set(table) - {"worktree", "depth_escalation", "scope", "feedback"})
    if unknown:
        raise SpecConfigError(f"config tool.spec: unknown keys: {', '.join(unknown)}")
    worktree = table.get("worktree", "auto")
    if worktree not in WORKTREE_LEVELS:
        raise SpecConfigError(f'config tool.spec.worktree: expected "auto" or "required", got {worktree!r}')
    escalation = table.get("depth_escalation", "auto")
    if escalation not in DEPTH_ESCALATION:
        raise SpecConfigError(f'config tool.spec.depth_escalation: expected "auto" or "ask", got {escalation!r}')
    return SpecConfig(
        worktree=worktree,
        depth_escalation=escalation,
        scope=_scope(table.get("scope", {})),
        feedback=_feedback(table.get("feedback", {})),
    )


def check_approvals(approvals: dict[str, str]) -> None:
    """Main decision boundaries and task intent permit ask or policy delegation, never off."""
    for gate in (INTENT_GATE, *APPROVAL_GATES):
        policy = approvals.get(gate, "ask")
        if policy not in INTEGRATION_POLICIES:
            raise SpecConfigError(
                f'config workflow.approvals.{gate}: expected "ask" or "auto", got {policy!r}',
                fix=f'Set {gate} = "ask" or "auto" in [workflow.approvals] of .devkit/config.toml',
            )


def _feedback(value: object) -> FeedbackConfig:
    where = "config tool.spec.feedback"
    if not isinstance(value, dict):
        raise SpecConfigError(f"{where}: expected a table")
    unknown = sorted(set(value) - set(FEEDBACK_CHOICES))
    if unknown:
        raise SpecConfigError(f"{where}: unknown keys: {', '.join(unknown)}")
    defaults = FeedbackConfig()
    settings: dict[str, str] = {}
    for key, choices in FEEDBACK_CHOICES.items():
        entry = value.get(key, getattr(defaults, key))
        if not isinstance(entry, str) or entry not in choices:
            raise SpecConfigError(f"{where}.{key}: expected {' | '.join(choices)}, got {entry!r}")
        settings[key] = entry
    return FeedbackConfig(**settings)


def _scope(value: object) -> ScopeConfig:
    where = "config tool.spec.scope"
    if not isinstance(value, dict):
        raise SpecConfigError(f"{where}: expected a table")
    unknown = sorted(set(value) - {"shared_path", "namespace", "timeout"})
    if unknown:
        raise SpecConfigError(f"{where}: unknown keys: {', '.join(unknown)}")
    shared = value.get("shared_path")
    shared_path: Path | None = None
    if shared is not None:
        expanded = Path(shared).expanduser() if isinstance(shared, str) and shared.strip() else None
        if expanded is None or not expanded.is_absolute():
            raise SpecConfigError(
                f"{where}.shared_path: expected an absolute directory path (or one starting with ~), got {shared!r}"
            )
        shared_path = expanded
    namespace = value.get("namespace")
    if namespace is not None and (not isinstance(namespace, str) or not SCOPE_NAMESPACE.match(namespace)):
        raise SpecConfigError(
            f"{where}.namespace: expected letters, digits, '.', '_' and '-' not starting with '.', got {namespace!r}"
        )
    timeout = value.get("timeout", SCOPE_TIMEOUT_DEFAULT)
    low, high = SCOPE_TIMEOUT_RANGE
    if isinstance(timeout, bool) or not isinstance(timeout, int) or not low <= timeout <= high:
        raise SpecConfigError(f"{where}.timeout: expected whole seconds from {low} to {high}, got {timeout!r}")
    return ScopeConfig(shared_path=shared_path, namespace=namespace, timeout=timeout)
