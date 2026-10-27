"""Extraction of ``devkit ...`` citations from Markdown: inline code spans and lines of fenced code blocks."""

from __future__ import annotations

import shlex
from collections.abc import Iterator
from dataclasses import dataclass

from devkit_agt.features.rules.models.markdown import LineKind, code_spans, scan

PROGRAM = "devkit"
# Launchers written before the program name; ``uv run`` may carry its own options (``uv run --no-active devkit``).
_LAUNCHERS = (("uv", "run"), ("uvx",), ("python", "-m"), ("python3", "-m"))
# Shell syntax that ends the invocation: a pipe, a list operator, a redirection or a comment.
_SHELL_END = frozenset({"|", "||", "&&", ";", "&", ">", ">>", "<", "2>&1", "2>", "&>"})


@dataclass(frozen=True)
class Citation:
    """One invocation of the CLI: where it is written and its arguments after the program name."""

    line: int
    column: int
    text: str
    args: tuple[str, ...]


def extract_citations(text: str) -> list[Citation]:
    """The citations of a Markdown document in line order.

    A citation is an inline code span, or a line of a fenced code block (joined with the following lines of the
    same block while it ends in ``\\``), that invokes the program: ``devkit ...``, optionally after ``$ `` and a
    launcher such as ``uv run``. Arguments stop at ``--``, at shell syntax and at a ``#`` comment.
    """
    found: list[Citation] = []
    fenced: list[tuple[int, str]] = []
    # One scan serves both views: prose lines (``prose_lines``) and fenced code lines (``fenced_lines``).
    for scanned in scan(text):
        if scanned.kind is LineKind.CODE:
            fenced.append((scanned.number, scanned.line))
        elif scanned.kind is not LineKind.FENCE:
            for column, content in code_spans(scanned.line):
                if (args := _invocation(content)) is not None:
                    found.append(Citation(scanned.number, column, content, args))
    pending: tuple[int, str] | None = None
    previous = 0
    for number, line in fenced:
        body = line.strip()
        if pending is not None and number != previous + 1:
            # A fence ended: its last line's continuation does not reach into the next block.
            _add_fenced(found, *pending)
            pending = None
        previous = number
        if pending is not None:
            start, joined = pending
            body, pending = f"{joined} {body}", None
        else:
            start = number
        if body.endswith("\\"):
            pending = (start, body[:-1].rstrip())
            continue
        _add_fenced(found, start, body)
    if pending is not None:
        _add_fenced(found, *pending)
    return sorted(found, key=lambda citation: (citation.line, citation.column))


def _add_fenced(found: list[Citation], line: int, body: str) -> None:
    if (args := _invocation(body)) is not None:
        found.append(Citation(line, 1, body, args))


def _invocation(code: str) -> tuple[str, ...] | None:
    """The arguments after the program name when ``code`` invokes it, else ``None``."""
    code = code.strip().removeprefix("$").strip()
    if not code.startswith(PROGRAM) and not code.startswith(tuple(launcher[0] for launcher in _LAUNCHERS)):
        return None
    tokens = _split(code)
    for launcher in _LAUNCHERS:
        if tuple(tokens[: len(launcher)]) == launcher:
            tokens = tokens[len(launcher) :]
            while tokens and tokens[0].startswith("-") and launcher == ("uv", "run"):
                tokens = tokens[1:]
            break
    if not tokens or tokens[0] != PROGRAM:
        return None
    args: list[str] = []
    for token in tokens[1:]:
        if token == "--" or token in _SHELL_END or token.startswith("#"):
            break
        if token.endswith(";"):
            args.append(token[:-1])
            break
        args.append(token)
    return tuple(arg for arg in args if arg)


def _split(code: str) -> list[str]:
    """Shell words of ``code``; text a shell could not split (an unbalanced quote) is split on whitespace."""
    try:
        return shlex.split(code, comments=False)
    except ValueError:
        return code.split()


def iter_option_names(token: str) -> Iterator[str]:
    """The option names a usage token spells: ``--format``, ``-w``; ``[--staged|--ci]`` and ``--title/-t`` give both.

    Brackets, parentheses, a trailing ``...`` or comma and an ``=value`` are not part of a name. A token that is
    not an option (a value, a placeholder) gives nothing.
    """
    for piece in token.strip("[]()").removesuffix("...").rstrip(",").strip("[]()").split("|"):
        for name in piece.partition("=")[0].split("/"):
            long = name.startswith("--") and len(name) > 2 and name[2].isalpha()
            if long or (len(name) == 2 and name[0] == "-" and name[1].isalpha()):
                yield name
