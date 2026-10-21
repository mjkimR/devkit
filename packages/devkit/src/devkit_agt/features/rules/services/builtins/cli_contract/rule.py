"""``RULE-cli-contract``: Markdown cites only ``devkit`` commands and options the running command line has.

The command tree is the click tree of the ``devkit`` invocation running the check, plugin commands included (the
rules layer cannot import ``devkit_dist.cli``, so it reads the root of the current click context). A run outside a
``devkit`` invocation (a library caller, a test that does not pass a root) checks nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import click

from devkit_agt.features.rules.models.contracts import Phase, RuleContext, Severity, Violation
from devkit_agt.features.rules.models.settings import match_path, validate_pattern
from devkit_agt.features.rules.services.builtins.base import BaseRule
from devkit_agt.features.rules.services.builtins.cli_contract.citations import (
    PROGRAM,
    Citation,
    extract_citations,
    iter_option_names,
)

_COMMAND_NAME = re.compile(r"^[a-z][a-z0-9-]*$")

REMEDIATION = (
    "Cite the command as the CLI has it (`devkit <command> --help` lists subcommands and options)."
    " Describe a planned or removed command in prose instead of an inline-code `devkit` invocation;"
    " exclude documents that record history (decisions, proposals) through the rule's `exclude` setting"
)


@dataclass(frozen=True)
class CliContractSettings:
    # Markdown files not checked, as workspace-relative patterns (records of past or planned commands).
    exclude: list[str] = field(default_factory=list)
    # Command paths below `devkit` whose citations are not checked, such as "spec" for a plugin documented but not
    # installed here, or "bundle init" for a planned command; a path covers its subcommands and options.
    unchecked_commands: list[str] = field(default_factory=list)


class CliContractRule(BaseRule):
    def __init__(self, root: click.Command | None = None) -> None:
        super().__init__(
            id="RULE-cli-contract",
            name="cli-contract-check",
            description="Inline-code and fenced `devkit` invocations in Markdown name existing commands and options.",
            phase=Phase.LINTER,
            severity=Severity.ERROR,
            settings=CliContractSettings(),
            guide="guide.md",
        )
        self._root = root

    def validate_settings(self, settings: CliContractSettings) -> None:
        for pattern in settings.exclude:
            validate_pattern(pattern)
        for command in settings.unchecked_commands:
            if not command.split() or not all(_COMMAND_NAME.match(name) for name in command.split()):
                raise ValueError(f"unchecked_commands entries are command paths such as 'spec', got {command!r}")

    def check(self, ctx: RuleContext) -> list[Violation]:
        root = self._root or _running_root()
        if root is None:
            return []
        verifier = _Verifier(root)
        violations: list[Violation] = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: CliContractSettings = ctx.settings(self, rel)
            if any(match_path(pattern, rel) for pattern in settings.exclude):
                continue
            unchecked = frozenset(tuple(command.split()) for command in settings.unchecked_commands)
            for citation in extract_citations(ctx.cache.read_text(path)):
                if (problem := verifier.verify(citation, unchecked)) is not None:
                    violations.append(
                        Violation(
                            rule_id=self.id,
                            file=rel,
                            line=citation.line,
                            column=citation.column,
                            message=problem,
                            remediation=REMEDIATION,
                            severity=self.severity,
                            phase=self.phase,
                        )
                    )
        return violations


def _running_root() -> click.Command | None:
    """The root command of the current click invocation when it is ``devkit``."""
    current = click.get_current_context(silent=True)
    if current is None:
        return None
    root = current.find_root().command
    return root if root.name == PROGRAM else None


class _Verifier:
    """Walks citations through the click tree; subcommand lookups are cached, as plugins load on lookup."""

    def __init__(self, root: click.Command) -> None:
        self._root = root
        self._children: dict[tuple[str, ...], click.Command | None] = {}

    def _child(self, path: tuple[str, ...], group: click.Group, name: str) -> click.Command | None:
        key = (*path, name)
        if key not in self._children:
            self._children[key] = group.get_command(click.Context(group, info_name=name), name)
        return self._children[key]

    def verify(self, citation: Citation, unchecked: frozenset[tuple[str, ...]] = frozenset()) -> str | None:
        """The first problem of a citation, or ``None``: an unknown command first, then an unknown option.

        A citation reaching a command path in ``unchecked`` (paths below the program) is not checked further.
        """
        command, path = self._root, (PROGRAM,)
        options = _options(command)
        args = list(citation.args)
        index = 0
        while index < len(args):
            token = args[index]
            index += 1
            names = list(iter_option_names(token))
            if names:
                if _accepts_any_option(command):
                    continue
                for name in names:
                    if name not in options:
                        return f"Unknown option {name} of '{' '.join(path)}' in `{citation.text}`"
                option = options.get(names[0])
                if len(names) == 1 and "=" not in token and option is not None and _takes_value(option):
                    index += option.nargs
                continue
            if not isinstance(command, click.Group) or _has_arguments(command):
                continue  # an argument of the command (or a placeholder for one)
            if not _COMMAND_NAME.match(token):
                return None  # a placeholder for the subcommand: nothing after it can be checked
            if (*path[1:], token) in unchecked:
                return None
            child = self._child(path, command, token)
            if child is None:
                return f"Unknown command '{token}' of '{' '.join(path)}' in `{citation.text}`"
            command, path = child, (*path, token)
            options = _options(command)
        return None


def _options(command: click.Command) -> dict[str, click.Option]:
    """Every option spelling of a command, the help option included."""
    params = command.get_params(click.Context(command))
    return {
        name: param
        for param in params
        if isinstance(param, click.Option)
        for name in (*param.opts, *param.secondary_opts)
    }


def _takes_value(option: click.Option) -> bool:
    return not option.is_flag and not option.count


def _has_arguments(command: click.Command) -> bool:
    return any(isinstance(param, click.Argument) for param in command.params)


def _accepts_any_option(command: click.Command) -> bool:
    """A command that passes unknown options through (a stand-in for an unusable plugin, a wrapper)."""
    return bool(command.context_settings.get("ignore_unknown_options"))
