"""One bounded pass over a command's output: what an agent needs from it, without the rest.

Recognition matches output, never command names, so ``npm`` scripts, ``just``
recipes and other wrappers work. Summaries and warnings are copied, never
inferred from progress output. Every result has a size budget; what does not
fit is counted in ``Omitted`` and stays in the full log. Reads are bounded
too: a line longer than ``MAX_LINE`` is classified by its prefix only, and only
the last ``LINE_CAP`` characters of a line are kept.

Some output is filtered out of the excerpt, counted in ``Scan.filtered``, and
kept in the log. A carriage return starts a line over, as on a terminal, so a
progress bar leaves only its final state. Lines that only report progress or a
passing item (pytest's dots, ``PASSED`` lines, ``✓`` lines) are filtered, and
so are lines that carry nothing an agent acts on (pytest's session header, uv's
success messages) and pytest's warnings summary, whose warnings are already
reported; a run of blank lines keeps one. A line that names a failure is never
filtered.

Agent Advisory Protocol blocks that a nested ``devkit`` command printed are
taken out whole (a headline, then field and continuation lines), so they reach
the caller intact even when the rest of the output is cut to an excerpt.
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from devkit.advisory import Level

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
MAX_LINE = 1_000
SUMMARY_BUDGET = 2_000
WARNING_BUDGET = 2_000
WARNING_MESSAGE = 500
ADVISORY_BUDGET = 4_000
# Failures usually end with the most useful part (pytest's short test summary,
# a linter's last findings and counts), so the tail gets the larger share.
HEAD = 3_000
TAIL = 5_000
CHUNK = 8_192
LINE_CAP = 64_000

_OUTCOME = r"\d+ (?:passed|failed|skipped|deselected|xfailed|xpassed|errors?|warnings?|rerun)"
_SUMMARIES = tuple(
    re.compile(pattern)
    for pattern in (
        # pytest's normal/quiet terminal summary, including xdist and warning counts.
        rf"(?:{_OUTCOME}(?:, {_OUTCOME})*|no tests ran)(?: in \d+(?:\.\d+)?s(?: \([\d:]+\))?)?",
        # Vitest: preserve file counts separately from test counts.
        r"(?:Test Files|Tests)\s+\d+ (?:passed|failed|skipped|todo)"
        r"(?:\s*\|\s*\d+ (?:passed|failed|skipped|todo))*\s+\(\d+\)",
        # Playwright prints each outcome on its own line.
        r"\d+ (?:passed|failed|skipped|flaky|did not run)(?: \([\d.hms ]+\))?",
        # Ruff format/check, including --fix results.
        r"\d+ files? (?:reformatted|left unchanged|already formatted|would be reformatted)"
        r"(?:, \d+ files? (?:reformatted|left unchanged|already formatted|would be reformatted))*",
        r"All checks passed!",
        r"Found \d+ errors? \(\d+ fixed, \d+ remaining\)\.",
        # Pyright, svelte-check, and ESLint retain warning counts even on success.
        r"\d+ errors?, \d+ warnings?, \d+ informations?",
        r"svelte-check found \d+ errors? and \d+ warnings?(?: in \d+ files?)?",
        r"(?:✖\s+)?\d+ problems? \(\d+ errors?, \d+ warnings?\)",
        r"All matched files use Prettier code style!",
        # pytest-cov: labelled below so the standalone line remains understandable.
        r"TOTAL\s+\d+\s+\d+(?:\s+\d+\s+\d+)?\s+\d+(?:\.\d+)?%",
        # devkit rules check/fix.
        r"\[SUMMARY: [^\]]*\]",
    )
)
_WARNINGS = tuple(
    re.compile(pattern)
    for pattern in (
        # Python/pytest and Pyright include the location on the same line.
        r"(?P<location>.+?:\d+(?::\d+)?): (?P<message>[\w.]*Warning: .+)",
        r"(?P<location>.+?:\d+:\d+) - warning: (?P<message>.+)",
        # Node runtime warnings include a process ID, which is not part of identity.
        r"\(node:\d+\) (?P<message>(?:\[[\w-]+\] )?[\w.]*Warning: .+)",
        # Ruff/uv and svelte-check use a one-line warning prefix.
        r"(?:warning|Warning|WARNING|Warn): (?P<message>.+)",
    )
)
_SOURCE_LOCATION = re.compile(r".+\.(?:svelte|[cm]?[jt]sx?|vue)(?::\d+:\d+)?")
_ESLINT_WARNING = re.compile(r"(?P<position>\d+:\d+)\s+warning\s+(?P<message>.+)")
_PERCENT = r"\[\s*\d+(?:%|/\d+)\]"
_PROGRESS = tuple(
    re.compile(pattern)
    for pattern in (
        # pytest: an optional test file, one character per test, then [ 45%] (or [ 12/130]).
        rf"(?:\S+ )?[.sxXfFER]+\s*{_PERCENT}",
        # pytest -v: a test that passed, was skipped or xfailed; FAILED and ERROR lines stay.
        rf"\S+::\S.* (?:PASSED|SKIPPED|XFAIL|XPASS)(?: \(.*\))?\s*{_PERCENT}",
        # pytest-xdist -v, and the passed tests pytest -rA lists in its short summary.
        rf"(?:\[gw\d+\] {_PERCENT} )?PASSED \S+",
        rf"\[gw\d+\] {_PERCENT} (?:SKIPPED|XFAIL|XPASS) \S+",
        # Vitest, Playwright's list reporter (passed or skipped item), Jest (passed file).
        r"[✓√↓] .+",
        r"PASS \S+(?: \([\d.]+ ?m?s\))?",
        # Playwright's dot reporter, while every test passes.
        r"·+",
    )
)

# Lines that carry nothing an agent acts on: pytest's session header, uv's success messages.
_NOISE = tuple(
    re.compile(pattern)
    for pattern in (
        r"platform \S+ -- Python \S+.*",
        r"(?:rootdir|configfile|inifile|cachedir|testpaths|plugins): .*",
        r"(?:Resolved|Prepared|Installed|Uninstalled|Audited|Downloaded) \d+ packages? in [\d.]+m?s",
        r"(?:Building|Built|Downloading|Downloaded) \S+ (?:@ \S+|\([\d.]+ ?[KMG]i?B\))",
        r"[+~-] [A-Za-z0-9][\w.\[\],-]*(?:==\S+(?: \(from .+\))?| @ \S+)",
    )
)
# pytest's section banners. A filtered section ends at the next banner, at its closing line (the
# documentation link pytest prints last) or at a summary line: under -q the final summary has no banner,
# and the output of a command run after pytest must not be filtered with the section.
_BANNER = re.compile(r"={2,} (?P<title>.+?) ={2,}")
_SECTION_END = "-- Docs: "
_FILTERED_BANNERS = {"test session starts", "warnings summary"}
_FILTERED_SECTIONS = {"warnings summary"}

# The Agent Advisory Protocol block grammar (docs/advisory/protocol.md, section 3).
_HEADLINES = {"[ERROR]  ": Level.ERROR, "[WARN]   ": Level.WARNING, "[NOTICE] ": Level.NOTICE}
_FIELDS = ("[ACTION] ", "[WHEN]   ", "[TARGET] ", "[FIX]    ", "[REPORT] ", "[DETAIL] ", " " * 9)


@dataclass(frozen=True)
class ToolWarning:
    """A warning a tool printed: its message and the first location it named (``""`` when none)."""

    message: str
    location: str = ""


@dataclass(frozen=True)
class RelayedAdvisory:
    """An advisory block a nested ``devkit`` command printed, as it was printed."""

    level: Level
    text: str


@dataclass(frozen=True)
class Omitted:
    """What did not fit a budget: items per kind, characters of the excerpt."""

    summaries: int = 0
    warnings: int = 0
    advisories: int = 0
    output: int = 0

    def __bool__(self) -> bool:
        return any((self.summaries, self.warnings, self.advisories, self.output))


@dataclass(frozen=True)
class Scan:
    """The bounded view of one command's output.

    ``output`` is the excerpt: the output without the relayed advisory blocks,
    its head and its tail with a marker line where characters were left out,
    filtered lines removed.
    """

    summaries: tuple[str, ...] = ()
    warnings: tuple[ToolWarning, ...] = ()
    advisories: tuple[RelayedAdvisory, ...] = ()
    output: str = ""
    omitted: Omitted = field(default_factory=Omitted)
    filtered: int = 0  # lines filtered out of the excerpt, overwritten progress states included


def warning_message(line: str, source: str) -> tuple[str, str] | None:
    """Return message and first location for known one-line warning formats."""
    for pattern in _WARNINGS:
        if match := pattern.fullmatch(line):
            location = match.groupdict().get("location") or (source if line.startswith("Warn:") else "")
            return " ".join(match["message"].split()), location
    if source and (match := _ESLINT_WARNING.fullmatch(line)):
        return " ".join(match["message"].split()), f"{source}:{match['position']}"
    return None


@dataclass(frozen=True)
class _Line:
    text: str  # the last LINE_CAP characters, newline included
    head: str  # the first MAX_LINE characters
    cut: int = 0  # characters before ``text`` that were not kept
    cut_returns: int = 0  # carriage returns among them


def _read(stream: TextIO) -> Iterator[_Line]:
    """Each line, keeping its start and its last ``LINE_CAP`` characters."""
    while piece := stream.readline(CHUNK):
        head = piece[:MAX_LINE]
        parts, size, cut, returns = [piece], len(piece), 0, 0
        while not piece.endswith("\n") and (piece := stream.readline(CHUNK)):
            parts.append(piece)
            size += len(piece)
            if size > 2 * LINE_CAP:
                joined = "".join(parts)
                cut += len(joined) - LINE_CAP
                returns += joined[:-LINE_CAP].count("\r")
                parts, size = [joined[-LINE_CAP:]], LINE_CAP
        text = "".join(parts)
        if len(text) > LINE_CAP:
            cut += len(text) - LINE_CAP
            returns += text[:-LINE_CAP].count("\r")
            text = text[-LINE_CAP:]
        yield _Line(text, head, cut, returns)


def _visible(line: str) -> tuple[str, int]:
    """What a terminal ends up showing: the last non-blank segment after a carriage return, without ANSI
    sequences or the line ending; and how many segments it overwrote."""
    body = ANSI.sub("", line).removesuffix("\n").removesuffix("\r")
    if "\r" not in body:
        return body, 0
    segments = [segment for segment in body.split("\r") if segment.strip()]
    return (segments[-1], len(segments) - 1) if segments else ("", 0)


def is_filtered(line: str) -> bool:
    """Whether ``line`` (one visible line) only reports progress or a passing item, or carries nothing an
    agent acts on; pytest's filtered sections are decided by the scan, which follows the banners."""
    clean = line.strip()
    return bool(clean) and any(pattern.fullmatch(clean) for pattern in (*_PROGRESS, *_NOISE))


class _Excerpt:
    """The first ``HEAD`` and last ``TAIL`` characters of what it is given, in whole pieces."""

    def __init__(self) -> None:
        self.head: list[str] = []
        self.head_size = 0
        self.head_open = True
        self.tail: deque[str] = deque()
        self.tail_size = 0
        self.dropped = 0

    def add(self, piece: str) -> None:
        if self.head_open:
            if self.head_size + len(piece) <= HEAD:
                self.head.append(piece)
                self.head_size += len(piece)
                return
            self.head_open = False
        self.tail.append(piece)
        self.tail_size += len(piece)
        while self.tail_size > TAIL:
            left = self.tail.popleft()
            self.tail_size -= len(left)
            self.dropped += len(left)

    def text(self) -> str:
        head = "".join(self.head)
        if not self.dropped:
            return head + "".join(self.tail)
        if head and not head.endswith("\n"):
            head += "\n"
        return f"{head}[... {self.dropped} characters omitted ...]\n{''.join(self.tail)}"


class _Scanner:
    def __init__(self, notices: bool, base: tuple[str, ...]) -> None:
        self.notices = notices
        self.base = base
        self.summaries: list[str] = []
        self.summary_budget = SUMMARY_BUDGET
        self.warnings: list[ToolWarning] = []
        self.warning_budget = WARNING_BUDGET
        self.seen_warnings: set[str] = set()
        self.advisories: list[RelayedAdvisory] = []
        self.advisory_budget = ADVISORY_BUDGET
        self.block: list[str] = []
        self.excerpt = _Excerpt()
        self.omitted = {"summaries": 0, "warnings": 0, "advisories": 0}
        self.filtered = 0
        self.section = ""
        self.last_blank = False
        self.source = ""

    def feed(self, line: _Line) -> None:
        text, overwritten = _visible(line.text)
        cut = line.cut
        # A cut line without carriage returns is read from its start: that is where a tool puts what it means.
        prefix = text[:MAX_LINE] if overwritten or not cut else _visible(line.head)[0]
        if overwritten:
            overwritten += line.cut_returns
        self.filtered += overwritten
        complete = not cut and len(text) <= MAX_LINE
        if complete and text[:9] in _HEADLINES:
            self.close_block()
            self.block = [text]
            return
        if self.block and complete and text.startswith(_FIELDS):
            self.block.append(text)
            return
        self.close_block()
        summary = self.classify(prefix, oversized=not complete)
        clean = text.strip()
        banner = _BANNER.fullmatch(clean)
        # pytest prints a section's end unindented; an indented or cut line inside the section never ends it.
        ends = complete and text == clean
        closing = ends and clean.startswith(_SECTION_END)
        if banner:
            self.section = banner["title"]
        elif self.section in _FILTERED_SECTIONS and ends and (closing or summary):
            self.section = ""
            if closing:
                self.filtered += 1
                return
        if (banner and banner["title"] in _FILTERED_BANNERS) or self.section in _FILTERED_SECTIONS or is_filtered(text):
            self.filtered += 1
            return
        # Checked after filtering, so the blank lines around a filtered line collapse too.
        blank = not text.strip()
        if blank and self.last_blank:
            self.filtered += 1
            return
        self.last_blank = blank
        if not overwritten:  # what a carriage return overwrote is progress, not omitted output
            self.excerpt.dropped += cut
        chunks = [text[start : start + MAX_LINE] for start in range(0, len(text), MAX_LINE)] or [""]
        chunks[-1] += "\n"
        for chunk in chunks:
            self.excerpt.add(chunk)

    def close_block(self) -> None:
        if not self.block:
            return
        level = _HEADLINES[self.block[0][:9]]
        text = "\n".join(self.block)
        self.block = []
        if level is Level.NOTICE and not self.notices:
            return
        if len(text) + 1 > self.advisory_budget:
            self.omitted["advisories"] += 1
            self.advisory_budget = 0
            return
        self.advisories.append(RelayedAdvisory(level, text))
        self.advisory_budget -= len(text) + 1

    def classify(self, text: str, *, oversized: bool) -> bool:
        """Record ``text`` as a warning or a summary; return whether it is a summary line."""
        clean = text.strip().strip("=").strip()
        if not clean:
            self.source = ""
        elif _SOURCE_LOCATION.fullmatch(clean):
            self.source = clean
        if warning := warning_message(clean, self.source):
            self.add_warning(*warning)
            return False
        if oversized or not any(pattern.fullmatch(clean) for pattern in _SUMMARIES):
            return False
        if clean.startswith("TOTAL"):
            clean = f"Coverage: {clean}"
        if len(clean) + 1 > self.summary_budget:
            self.omitted["summaries"] += 1
            self.summary_budget = 0
            return True
        self.summaries.append(clean)
        self.summary_budget -= len(clean) + 1
        return True

    def add_warning(self, message: str, location: str) -> None:
        if message in self.seen_warnings:
            return
        for base in self.base:
            if location.startswith(base):
                location = location[len(base) :]
                break
        self.seen_warnings.add(message)
        if len(message) > WARNING_MESSAGE:
            message = message[:WARNING_MESSAGE] + "..."
        size = len(message) + len(location) + 1
        if size > self.warning_budget:
            self.omitted["warnings"] += 1
            self.warning_budget = 0
            return
        self.warnings.append(ToolWarning(message, location))
        self.warning_budget -= size

    def result(self) -> Scan:
        self.close_block()
        return Scan(
            summaries=tuple(self.summaries),
            warnings=tuple(self.warnings),
            advisories=tuple(self.advisories),
            output=self.excerpt.text(),
            omitted=Omitted(**self.omitted, output=self.excerpt.dropped),
            filtered=self.filtered,
        )


def scan(stream: TextIO, *, notices: bool = True, base: Sequence[str | Path] = ()) -> Scan:
    """Read ``stream`` once and return its bounded view.

    ``notices=False`` drops relayed ``[NOTICE]`` blocks. A warning location
    under one of the ``base`` directories is shown relative to it.
    """
    prefixes = tuple(dict.fromkeys(str(directory).rstrip("/") + "/" for directory in base))
    scanner = _Scanner(notices, prefixes)
    for line in _read(stream):
        scanner.feed(line)
    return scanner.result()
