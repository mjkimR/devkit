"""Repository-wide guards for the agent output contract of every ``devkit`` package.

An agent acts on what devkit prints, so the contract (``ARCH-08-1-agent-output``,
``CAP-ADV-agent-advisory-protocol`` sections 6 and 8, ``ADR-keep-uv-run-as-the-agent-facing-devkit-invocation``)
must hold for every command and error, not only the ones a feature's own tests happen to exercise:

- a ``[FIX]`` is runnable as written: no ``<placeholder>`` or ``--option METAVAR`` template, and every devkit command
  it names is the agent-facing ``uv run devkit ...``;
- an error's directive matches its fix: a ``BLOCKED`` or ``MAINTENANCE`` class does not tell the agent to retry, and a
  subclass of a public guardrail error declares ``guardrail`` itself instead of inheriting ``BLOCKED`` silently;
- every visible command takes ``--format`` and names its workspace option ``-w/--workspace-root``;
- the stdout sentinels of real read-only commands follow the sentinel grammar.

Fix strings are found in the sources (class attributes and ``fix=``/``what_to_report=`` keywords, f-string fields
read as ``{}``) and on the classes themselves, so a fix built from a module constant is checked too. A rule's own
``tests/`` under the sources hold fixtures only.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import pkgutil
import re
import shlex
from collections.abc import Iterator
from pathlib import Path

import click
import pytest
from click.testing import CliRunner
from devkit.advisory import AdvisoryError
from devkit.advisory.advisory import Advisory
from devkit.advisory.types import ActionMode
from devkit_dist.cli import cli

REPO = Path(__file__).resolve().parents[5]
PACKAGES = (
    "devkit.advisory",
    "devkit_cli",
    "devkit_core",
    "devkit_dist",
    "devkit_agt",
    "devkit_spec",
    "devkit_mcp",
    "devkit_viewer",
)
INSTALLED = tuple(name for name in PACKAGES if importlib.util.find_spec(name) is not None)
SOURCES = tuple(
    path
    for path in (
        REPO / "packages/devkit-advisory/src/devkit",
        REPO / "packages/devkit-cli/src/devkit_cli",
        REPO / "packages/devkit-core/src/devkit_core",
        REPO / "packages/devkit-dist/src/devkit_dist",
        REPO / "packages/devkit/src/devkit_agt",
        REPO / "packages/devkit-spec/src/devkit_spec",
        REPO / "packages/devkit-mcp/src/devkit_mcp",
        REPO / "packages/devkit-viewer/src/devkit_viewer",
    )
    if path.is_dir()
)

# A `<word>` template; `<<` (a heredoc) and `<-` never occur in a fix.
PLACEHOLDER = re.compile(r"<[A-Za-z][\w.:-]*(?: [\w.:-]+)*>")
# An option followed by an all-caps metavar, such as `--namespace NAME`; FETCH_HEAD and HEAD are Git literals.
METAVAR = re.compile(r"(?<![\w-])(--?[a-z][\w-]*)[ =]([A-Z][A-Z_]{2,})\b(?![\w-])")
GIT_LITERALS = {"HEAD", "FETCH_HEAD", "ORIG_HEAD", "MERGE_HEAD"}
RETRY_FIRST = re.compile(r"^\s*(?:re-?run|retry|try again|repeat)\b", re.IGNORECASE)

# A fragment of a fix whose placeholder stays: why. Keep this short.
PLACEHOLDER_ALLOWED: dict[str, str] = {}

# Class qualname: why its BLOCKED or MAINTENANCE fix starts with a retry. Keep this short.
RETRY_FIX_ALLOWED: dict[str, str] = {}


# --- fix strings ---------------------------------------------------------------------------------------------------


def _top_level_commands() -> set[str]:
    return set(cli.list_commands(click.Context(cli)))


def _text(node: ast.expr) -> str | None:
    """The literal text of ``node``: a string, an f-string with ``{}`` for its fields, or a concatenation of both."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(str(part.value) if isinstance(part, ast.Constant) else "{}" for part in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _text(node.left), _text(node.right)
        return None if left is None or right is None else left + right
    return None


def _modules() -> Iterator[tuple[str, ast.Module]]:
    for source in SOURCES:
        for path in sorted(source.rglob("*.py")):
            if "tests" in path.relative_to(source).parts:
                continue
            yield path.relative_to(REPO).as_posix(), ast.parse(path.read_text(encoding="utf-8"))


def _is_advisory_call(node: ast.Call) -> bool:
    name = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
    return name.endswith(("Error", "Warning", "Notice", "Problem")) or name in {
        "blocked",
        "interaction",
        "auto_fix",
        "defer",
        "halt",
        "maintenance",
        "input_error",
    }


def _literals() -> list[tuple[str, str, int, str]]:
    """Every literal ``(field, file, line, text)`` that becomes a ``[FIX]``, ``[REPORT]`` or ``[DETAIL]``."""
    found: list[tuple[str, str, int, str]] = []
    for file, tree in _modules():
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for statement in node.body:
                    if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                        target, value = statement.targets[0], statement.value
                    elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
                        target, value = statement.target, statement.value
                    else:
                        continue
                    if (
                        isinstance(target, ast.Name)
                        and target.id in {"fix", "what_to_report"}
                        and (text := _text(value)) is not None
                    ):
                        found.append((target.id, file, statement.lineno, text))
            elif isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if keyword.arg in {"fix", "what_to_report"} and (text := _text(keyword.value)) is not None:
                        found.append((keyword.arg, file, keyword.value.lineno, text))
                if _is_advisory_call(node):
                    for argument in node.args[1:]:
                        if (text := _text(argument)) is not None:
                            found.append(("details", file, argument.lineno, text))
    return found


def _bare_devkit(text: str, commands: set[str], *, quoted_only: bool) -> list[str]:
    """Each ``devkit <subcommand>`` in ``text`` not run through ``uv run``; with ``quoted_only``, only in backticks."""
    pattern = re.compile(rf"(?<![\w./-])devkit ({'|'.join(sorted(map(re.escape, commands)))})(?![\w-])")
    bare = []
    for match in pattern.finditer(text):
        if text[: match.start()].endswith("uv run "):
            continue
        if quoted_only and text[: match.start()].count("`") % 2 == 0:
            continue
        bare.append(match.group(0))
    return bare


def _templated(fix: str) -> bool:
    if any(fragment in fix for fragment in PLACEHOLDER_ALLOWED):
        return False
    return bool(PLACEHOLDER.search(fix) or {name for _, name in METAVAR.findall(fix)} - GIT_LITERALS)


def test_the_fix_scan_finds_the_fields() -> None:
    fields = {field for field, *_ in _literals()}
    assert fields == {"fix", "what_to_report", "details"}


def test_fixes_carry_no_placeholder() -> None:
    problems = {
        f"{file}:{line}": text for field, file, line, text in _literals() if field == "fix" and _templated(text)
    }
    assert problems == {}, "a [FIX] is the exact command or edit: fill the value in or name the command that lists it"


def test_class_fixes_carry_no_placeholder() -> None:
    problems = {
        f"{cls.__module__}.{cls.__qualname__}": cls.fix
        for cls in _advisory_classes()
        if "fix" in cls.__dict__ and isinstance(cls.fix, str) and _templated(cls.fix)
    }
    assert problems == {}


def test_devkit_commands_are_named_through_uv_run() -> None:
    commands = _top_level_commands()
    assert {"sync", "spec", "workflow"} <= commands  # the plugins are mounted
    problems = {
        f"{file}:{line}": text
        for field, file, line, text in _literals()
        if _bare_devkit(text, commands, quoted_only=field != "fix")
    }
    problems |= {
        f"{cls.__module__}.{cls.__qualname__}": str(cls.fix)
        for cls in _advisory_classes()
        if isinstance(cls.fix, str) and _bare_devkit(cls.fix, commands, quoted_only=False)
    }
    assert problems == {}, (
        "name devkit as the agent runs it: uv run devkit ... (ADR-keep-uv-run-as-the-agent-facing-...)"
    )


# --- modes ---------------------------------------------------------------------------------------------------------


def _import_all() -> None:
    for name in INSTALLED:
        package = importlib.import_module(name)
        for module in pkgutil.walk_packages(package.__path__, f"{name}."):
            if ".tests" in module.name or ".bundle." in module.name or module.name.endswith(".bundle"):
                continue
            importlib.import_module(module.name)


def _advisory_classes() -> list[type[AdvisoryError]]:
    _import_all()
    seen: dict[type[AdvisoryError], None] = {}
    pending = [AdvisoryError]
    while pending:
        for subclass in pending.pop().__subclasses__():
            if subclass not in seen and subclass.__module__.startswith(INSTALLED):
                seen[subclass] = None
                pending.append(subclass)
    return list(seen)


def _mode(cls: type[AdvisoryError]) -> ActionMode:
    return Advisory(
        level=cls.level, actor=cls.actor, retry=cls.retry, guardrail=cls.guardrail, input_error=cls.input_error
    ).mode


def test_the_class_scan_finds_every_package() -> None:
    owners = {cls.__module__.split(".")[0] for cls in _advisory_classes()}
    assert {"devkit_core", "devkit_dist", "devkit_agt"} <= owners


def test_blocked_and_maintenance_fixes_do_not_direct_a_retry() -> None:
    problems = {
        cls.__qualname__: cls.fix
        for cls in _advisory_classes()
        if _mode(cls) in {ActionMode.BLOCKED, ActionMode.MAINTENANCE}
        if isinstance(cls.fix, str) and RETRY_FIRST.search(cls.fix) and cls.__qualname__ not in RETRY_FIX_ALLOWED
    }
    assert problems == {}, "BLOCKED and MAINTENANCE tell the agent to stop: a [FIX] that is only a retry contradicts it"


def test_a_subclass_of_a_guardrail_error_declares_guardrail_itself() -> None:
    """``BLOCKED`` is a deliberate refusal: a subclass inherits it from a public error only by saying so.

    A private base named for its mode (``_Guardrail``) exists to give its subclasses that mode, so it is exempt.
    """
    problems = []
    for cls in _advisory_classes():
        owner = next(base for base in cls.__mro__ if "guardrail" in base.__dict__)
        if owner is not cls and owner.guardrail is True and not owner.__name__.startswith("_"):
            problems.append(f"{cls.__module__}.{cls.__qualname__} inherits guardrail=True from {owner.__qualname__}")
    assert problems == []


# --- the command surface -------------------------------------------------------------------------------------------

# Visible leaf commands without --format, and why.
FORMAT_EXEMPT = {
    "viewer serve": "a long-running local HTTP server; it prints the URL it serves and has no result to format",
}


def _leaves() -> Iterator[tuple[str, click.Command]]:
    def walk(command: click.Command, path: list[str], context: click.Context) -> Iterator[tuple[str, click.Command]]:
        if isinstance(command, click.Group):
            for name in command.list_commands(context):
                sub = command.get_command(context, name)
                assert sub is not None, name
                yield from walk(sub, [*path, name], click.Context(sub, parent=context, info_name=name))
        else:
            yield " ".join(path), command

    yield from walk(cli, [], click.Context(cli, info_name="devkit"))


def _visible_leaves() -> list[tuple[str, click.Command]]:
    leaves = [(name, command) for name, command in _leaves() if not command.hidden]
    assert {"sync", "spec policy", "workflow next", "worktree status"} <= {name for name, _ in leaves}
    return leaves


def test_every_visible_command_takes_format() -> None:
    problems = {}
    for name, command in _visible_leaves():
        option = next((param for param in command.params if "--format" in param.opts), None)
        if option is None:
            if name not in FORMAT_EXEMPT:
                problems[name] = "no --format"
            continue
        choices = set(getattr(option.type, "choices", ()))
        if choices not in ({"text", "json"}, {"json"}):
            problems[name] = f"--format choices {sorted(choices)}"
    assert problems == {}
    assert set(FORMAT_EXEMPT) <= {name for name, _ in _visible_leaves()}  # no stale exemption


def test_the_workspace_option_is_named_w_workspace_root() -> None:
    problems = {}
    for name, command in _leaves():
        if command.hidden:
            continue
        for param in command.params:
            names = [*param.opts, *getattr(param, "secondary_opts", [])]
            named = any("workspace" in option for option in names) or "-w" in names
            if named and sorted(names) != ["--workspace-root", "-w"]:
                problems[name] = names
    assert problems == {}


# --- sentinel grammar on real output -------------------------------------------------------------------------------

READ_ONLY = (
    "spec policy",
    "spec list spec",
    "spec list proposal",
    "spec resolve ARCH-08-1-agent-output",
    "rules check AGENTS.md",
    "workflow list",
    "workflow show sdd-spec-feature",
    "gate status",
    "worktree status",
    "generated list",
    "host status",
    "mcp status",
)
SENTINEL = re.compile(r"^\[([A-Z][A-Z0-9_]*)(?:: (.*))?\]$")
ADVISORY_NAMES = {"ERROR", "WARN", "WARNING", "NOTICE", "INFO", "ACTION", "WHEN", "TARGET", "FIX", "REPORT", "DETAIL"}
KEY = re.compile(r"[a-z][a-z0-9_]*=")
BARE_VALUE = re.compile(r'[^\s"\]]+')
_DECODER = json.JSONDecoder()


def _sentinel_problems(line: str) -> list[str]:
    """What breaks the sentinel grammar in ``line``: its shape, its kind, or a ``key=value`` token."""
    match = SENTINEL.match(line)
    if match is None:
        return ["not [KIND: ...]"]
    kind, body = match.group(1), match.group(2) or ""
    problems = [f"advisory name {kind} as a stdout kind"] if kind in ADVISORY_NAMES else []
    position = 0
    while position < len(body):
        if body[position] == " ":
            position += 1
            continue
        if body[position] == '"':  # a positional JSON string
            try:
                _, position = _DECODER.raw_decode(body, position)
            except json.JSONDecodeError:
                return [*problems, f"unterminated string at {position}"]
            continue
        key = KEY.match(body, position)
        end = body.find(" ", position)
        end = len(body) if end < 0 else end
        if key is None:  # free text
            position = end
            continue
        start = key.end()
        if body.startswith('"', start):
            try:
                value, position = _DECODER.raw_decode(body, start)
            except json.JSONDecodeError:
                return [*problems, f"{key.group(0)} value is not a JSON string"]
            if not isinstance(value, str):
                problems.append(f"{key.group(0)} value is not a string")
            continue
        value = body[start:end]
        if not BARE_VALUE.fullmatch(value):
            problems.append(f"{key.group(0)}{value!r} needs quoting")
        elif value in {"true", "false", "True", "False"}:
            problems.append(f"{key.group(0)}{value} is a boolean; use yes/no")
        position = end
    return problems


@pytest.mark.parametrize(
    ("line", "ok"),
    [
        ('[GIT_POLICY: worktree=required delete_branch=yes setup="just init"]', True),
        ('[DECISION_ERROR: decisions/01.yaml "bad record"]', True),
        ("[OK]", True),
        ("[PROBLEM: stages[0]: needs an id]", True),
        ("[GIT_POLICY: setup=just init]", True),  # `init` is free text: the grammar cannot tell it apart
        ('[GIT_POLICY: setup="just init]', False),
        ("[GIT_POLICY: delete_branch=true]", False),
        ('[RESULT: data={"a": 1}]', False),
        ("[WARN: something]", False),
        ("[lower: x]", False),
        ("[RESULT: x=1", False),
    ],
)
def test_the_sentinel_grammar_check(line: str, ok: bool) -> None:
    assert (_sentinel_problems(line) == []) is ok


@pytest.mark.parametrize("command", READ_ONLY)
def test_read_only_commands_print_grammatical_sentinels(command: str) -> None:
    result = CliRunner().invoke(cli, [*shlex.split(command), "-w", str(REPO)])
    assert result.exit_code in {0, 1}, result.output
    lines = [line for line in result.stdout.splitlines() if line.startswith("[")]
    assert lines, result.stdout
    problems = {line: found for line in lines if (found := _sentinel_problems(line))}
    assert problems == {}


@pytest.mark.parametrize("command", READ_ONLY)
def test_read_only_commands_print_one_json_object(command: str) -> None:
    result = CliRunner().invoke(cli, [*shlex.split(command), "-w", str(REPO), "--format", "json"])
    assert result.exit_code in {0, 1}, result.output
    assert isinstance(json.loads(result.stdout), dict)
