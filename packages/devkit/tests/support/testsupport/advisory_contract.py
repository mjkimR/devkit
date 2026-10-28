"""Shared checks for literal and fully constructed agent advisory text."""

from __future__ import annotations

import re
from collections.abc import Collection

from devkit.advisory import AdvisoryError
from devkit.advisory.types import ActionMode

PLACEHOLDER = re.compile(r"<[A-Za-z][\w.:'|/-]*(?: [\w.:'|/-]+)*>")
METAVAR = re.compile(r"(?<![\w-])(--?[a-z][\w-]*)[ =]([A-Z][A-Z_]{2,})\b(?![\w-])")
GIT_LITERALS = {"HEAD", "FETCH_HEAD", "ORIG_HEAD", "MERGE_HEAD"}
RETRY_FIRST = re.compile(r"^\s*(?:re-?run|retry|try again|repeat)\b", re.IGNORECASE)


def templated(fix: str, *, allowed: Collection[str] = ()) -> bool:
    if any(fragment in fix for fragment in allowed):
        return False
    return bool(PLACEHOLDER.search(fix) or {name for _, name in METAVAR.findall(fix)} - GIT_LITERALS)


def bare_devkit(text: str, commands: set[str], *, quoted_only: bool) -> list[str]:
    """Find commands missing the agent invocation prefix; non-FIX prose only checks backticks."""
    pattern = re.compile(rf"(?<![\w./-])devkit ({'|'.join(sorted(map(re.escape, commands)))})(?![\w-])")
    bare = []
    for match in pattern.finditer(text):
        if text[: match.start()].endswith("uv run "):
            continue
        if quoted_only and text[: match.start()].count("`") % 2 == 0:
            continue
        bare.append(match.group(0))
    return bare


def assert_advisory_contract(error: AdvisoryError, commands: set[str]) -> None:
    """Check the instance after helpers and conditionals have supplied its actual fields."""
    advisory = error.advisory
    if advisory.fix:
        assert not templated(advisory.fix), f"{error.code} FIX contains a placeholder: {advisory.fix}"
        assert not bare_devkit(advisory.fix, commands, quoted_only=False), f"{error.code} FIX lacks uv run"
        if advisory.mode in {ActionMode.BLOCKED, ActionMode.MAINTENANCE}:
            assert not RETRY_FIRST.search(advisory.fix), f"{error.code} FIX contradicts {advisory.mode}"
    for field, text in [("REPORT", advisory.what_to_report), *(("DETAIL", text) for text in advisory.details)]:
        if text:
            assert not bare_devkit(text, commands, quoted_only=True), f"{error.code} {field} lacks uv run: {text}"
