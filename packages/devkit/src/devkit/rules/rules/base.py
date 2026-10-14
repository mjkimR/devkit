from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from devkit.core.receipt import MANAGED_PATH, OVERRIDES_PATH
from devkit.rules.engine.errors import RuleDefinitionError
from devkit.rules.engine.models import Phase, Rule, Severity

RELATED_REF = re.compile(r"[a-z][a-z0-9-]*:[a-z][a-z0-9-]*")


@dataclass
class BaseRule(Rule):
    id: str
    name: str
    description: str
    phase: Phase = Phase.LINTER
    severity: Severity = Severity.ERROR
    # Declared on a ``hygiene`` rule that is meant to become a ``linter`` rule once
    # the codebase is clean. The CLI reports remaining violations for such rules.
    promote_to: Phase | None = None
    # Default settings as a dataclass instance; ``[rules.settings.<id>]`` may change
    # its fields per project and per path. ``None`` means the rule has no settings.
    settings: Any = None
    # Markdown guide for this rule, relative to the module defining the rule class.
    guide: str | None = None
    # Instructions and playbooks that hold the judgment or procedure behind the rule, as ``<bundle>:<asset-id>``;
    # ``devkit rules explain`` resolves each to the file agents read (the project override, else the managed copy).
    related: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for ref in self.related:
            if not RELATED_REF.fullmatch(ref):
                raise RuleDefinitionError(
                    f"{self.id}: related entry {ref!r} must be <bundle>:<asset-id> (lowercase slugs)"
                )
        if self.promote_to is None:
            return
        if self.phase != Phase.HYGIENE or self.promote_to != Phase.LINTER:
            raise RuleDefinitionError(
                f"{self.id}: promote_to is only valid as 'linter' on a 'hygiene' rule "
                f"(got phase={self.phase.value}, promote_to={self.promote_to.value})"
            )

    def validate_settings(self, settings: Any) -> None:
        """Reject settings values the field types alone cannot express; raise ``ValueError``."""


def guide_path(rule: Rule) -> Path | None:
    """Absolute path of the rule's guide document, if it declares one and the file exists."""
    name = getattr(rule, "guide", None)
    if not isinstance(name, str) or not name:
        return None
    try:
        module_file = Path(inspect.getfile(type(rule)))
    except (TypeError, OSError):
        return None
    for directory in (module_file.parent, managed_counterpart(module_file.parent)):
        if directory is not None and (path := (directory / name).resolve()).is_file():
            return path
    return None


def managed_counterpart(path: Path) -> Path | None:
    """The managed copy of a path inside a project override (``.devkit/overrides/<bundle>/...`` becomes
    ``.devkit/managed/<bundle>/...``), else ``None``.

    An override replaces files one by one: the files of an asset it does not hold (a rule's guide, its tests) are
    the managed copies, so a file looked up beside an overridden module is looked up there too.
    """
    return _counterpart(path, OVERRIDES_PATH, MANAGED_PATH)


def override_counterpart(path: Path) -> Path | None:
    """The project override location of a path inside the managed root (``.devkit/managed/<bundle>/...`` becomes
    ``.devkit/overrides/<bundle>/...``), else ``None``; ``managed_counterpart`` the other way round."""
    return _counterpart(path, MANAGED_PATH, OVERRIDES_PATH)


def _counterpart(path: Path, source: str, target: str) -> Path | None:
    parts = path.parts
    marker = tuple(PurePosixPath(source).parts)
    for index in range(len(parts) - len(marker) + 1):
        if parts[index : index + len(marker)] == marker:
            return Path(*parts[:index], *PurePosixPath(target).parts, *parts[index + len(marker) :])
    return None
