"""Errors of ``devkit.rules``: ``AdvisoryError`` subclasses with stable codes.

Raised errors stop a run before any rule is evaluated (``RulesConfigError``,
or the core ``ConfigError`` for an unreadable ``.devkit/config.toml``,
``TargetError``, ``RulesDirError``, ``SnapshotError``). Problems a run collects
instead of raising (``RuleProblem`` and its subclasses) are returned in
``RuleRegistry.errors``, ``ProjectRun.load_errors`` and
``EvaluationResult.errors``; each carries a code and, when it concerns one rule,
that rule's ID in ``rule_id``. ``str(problem)`` is its message.
``PromotionReadyNotice`` is a notice a completed run returns in
``ProjectRun.notices``; it is never raised.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Unpack

from devkit.advisory import Actor, AdvisoryError, AdvisoryFields, Level, Retry
from devkit.core import errors as core_errors
from devkit.core.receipt import CONFIG_PATH

SYNC_FIX = "Run `devkit sync` and commit the receipt"


class RulesError(AdvisoryError):
    """Base class of every error of the rule engine."""

    actor = Actor.DEVELOPER
    retry = Retry.AFTER_FIX


class RulesConfigError(RulesError, core_errors.ConfigError):
    """The ``[rules]`` table of ``.devkit/config.toml`` is malformed.

    A file that cannot be read or parsed at all is the core ``ConfigError``
    (``CONFIG_INVALID``), raised unchanged by ``read_project_config``.
    """

    code = "RULES_CONFIG_INVALID"
    input_error = True
    target_files = (CONFIG_PATH,)
    fix = "Correct the [rules] table in .devkit/config.toml"


class TargetError(RulesError):
    """An explicit target is outside the workspace or is not an existing file or directory."""

    code = "RULES_TARGET_INVALID"
    input_error = True
    fix = "Pass existing files or directories inside the workspace"


class RulesDirError(RulesError):
    """``rules_dir`` cannot be used for a Git snapshot run (outside the repository, or not in the snapshot)."""

    code = "RULES_DIR_INVALID"
    input_error = True


class SnapshotError(RulesError):
    """Git is unavailable, the directory is not a repository top level, a ref cannot be resolved,
    or the tree cannot be materialized."""

    code = "RULES_SNAPSHOT_FAILED"


class PinnedWriteError(RulesError):
    """A rule tried to write a receipt-pinned copy under ``.devkit/managed/`` or ``.devkit/overrides/``."""

    code = "RULES_PINNED_WRITE_REFUSED"
    guardrail = True
    fix = "Edit the project override with `devkit override create <bundle>:<asset>` instead of the pinned copy"


class RuleProblem(RulesError):
    """A problem a run collects instead of raising; ``rule_id`` is the rule it concerns, if any."""

    def __init__(
        self, message: str, *details: object, rule_id: str | None = None, **fields: Unpack[AdvisoryFields]
    ) -> None:
        super().__init__(message, *details, **fields)
        self.rule_id = rule_id

    def to_dict(self, *, include_advisory: bool = True) -> dict[str, Any]:
        return {**super().to_dict(include_advisory=include_advisory), "rule_id": self.rule_id}


class PolicyError(RuleProblem):
    """``[rules]`` policy that cannot apply to the loaded rules (unknown rule, redundant override, bad settings)."""

    code = "RULES_POLICY_INVALID"
    input_error = True
    target_files = (CONFIG_PATH,)
    fix = "Correct or remove the entry in the [rules] table of .devkit/config.toml"


class SettingsError(PolicyError):
    """A rule's settings declaration or configured values do not type-check; the message starts with the rule ID.

    Raised by ``SettingsResolver``; collected as a policy problem by
    ``validate_policy`` and as a run problem when overrides combine to invalid
    settings for one file. A defect in the rule's own declaration is
    ``MAINTENANCE`` rather than ``INPUT_ERROR``.
    """

    code = "RULES_SETTINGS_INVALID"


class RuleLoadError(RuleProblem):
    """A rule file could not be loaded, or the receipt lists a synchronized rule that cannot be used."""

    code = "RULES_LOAD_FAILED"


class RuleExecutionError(RuleProblem):
    """A rule raised while checking or fixing."""

    code = "RULES_EXECUTION_FAILED"


class RuleDefinitionError(RulesError):
    """A rule class declares an invalid combination of attributes (for example ``promote_to``)."""

    code = "RULES_DEFINITION_INVALID"


class PromotionReadyNotice(RulesError):
    """A hygiene run found phase transitions with no violation left: drop the override or flip the phase (``NOTICE``)."""

    code = "RULES_PROMOTION_READY"
    level = Level.NOTICE


class RulesRunError(RulesError):
    """A project run could not complete; ``problems`` are the collected rule problems, also given as details.

    Raised by ``ProjectRun.raise_for_problems`` for callers that need one error for a failed run.
    """

    code = "RULES_RUN_FAILED"

    def __init__(self, problems: Sequence[RuleProblem], **fields: Unpack[AdvisoryFields]) -> None:
        super().__init__(
            "; ".join(str(problem) for problem in problems),
            *(f"({problem.code}) {problem}" for problem in problems),
            **fields,
        )
        self.problems = tuple(problems)
