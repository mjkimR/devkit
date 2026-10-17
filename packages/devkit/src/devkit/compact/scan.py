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
reported; a run of blank lines keeps one, and a run of identical lines keeps
the first with a count. A line that names a failure is never filtered.

The tests a pytest run names as failed or errored and the excerpt cuts out are
listed apart (``Scan.failures``), so the caller learns what failed, and can
rerun it, even when the excerpt is cut, without a test the excerpt shows
being repeated.

The excerpt's omission markers name the log lines they stand for, so the
caller can read exactly those. The last lines of the output are kept apart
(``Scan.last_lines``): a tool whose summary is not recognized usually ends with
its verdict.

Agent Advisory Protocol blocks that a nested ``devkit`` command printed are
taken out whole (a headline, then field and continuation lines, up to an empty
line), so they reach the caller intact even when the rest of the output is cut
to an excerpt; a block that does not fit its budget stays in the excerpt.
"""

from __future__ import annotations

import re
from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TextIO

from devkit.advisory import CONTINUATION, FIELDS, HEADLINE, Level

# Escape sequences a terminal does not show: CSI (colour, cursor), OSC (hyperlinks, titles), charset selection.
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()][0-9A-B]")
MAX_LINE = 1_000
SUMMARY_BUDGET = 2_000
WARNING_BUDGET = 2_000
WARNING_MESSAGE = 500
FAILURE_BUDGET = 2_000
FAILURE_MESSAGE = 200
FAILURES_KEPT = 10_000  # failed tests remembered with their message until the excerpt is known
FAILURES_COUNTED = 100_000  # failed tests beyond those remembered without it, so each is counted once
ADVISORY_BUDGET = 4_000  # for errors, and again for warnings and notices: errors are never crowded out
# Failures usually end with the most useful part (pytest's short test summary,
# a linter's last findings and counts), so the tail gets the larger share.
HEAD = 3_000
TAIL = 5_000
# The output's last lines, shown in place of a summary when none was recognized.
LAST_LINES = 5
LAST_BUDGET = 500
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
        # tsc (and ruff without fixes), with the file forms tsc prints; mypy adds the files it checked.
        r"Found \d+ errors?(?: in (?:\d+ files?(?: \(checked \d+ source files?\))?|the same file, starting at: \S+"
        r"|\S+:\d+))?\.?(?: Watching for file changes\.)?",
        r"Success: no issues found in \d+ source files?",
        # Jest.
        r"(?:Test Suites|Tests):\s+(?:\d+ (?:failed|passed|skipped|todo|pending), )*\d+ total",
        # cargo test, once per test binary.
        r"test result: (?:ok|FAILED)\. \d+ passed; \d+ failed;.*",
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
# A pytest node ID: a test file, then classes and the test, a parameter set in brackets (it may contain spaces).
# No part matches a ":", so a run of "::" splits one way only, never exponentially many.
_NODE_ID = r"[^\s:]+\.py(?:::[^\s\[:]+(?:\[[^\]]*\])?)*"
_PERCENT = r"\[\s*\d+(?:%|/\d+)\]"
_FAILURES = tuple(
    re.compile(pattern)
    for pattern in (
        # pytest's short test summary (FAILED for a failed test, ERROR for a setup, teardown or collection
        # error), also as pytest-xdist -v prints it.
        rf"(?:\[gw\d+\] {_PERCENT} )?(?P<kind>FAILED|ERROR) (?P<test>{_NODE_ID})(?: - (?P<message>.+))?",
        # pytest -v.
        rf"(?P<test>{_NODE_ID}) (?P<kind>FAILED|ERROR)(?: .*?)?\s*{_PERCENT}",
    )
)
_SOURCE_LOCATION = re.compile(r".+\.(?:svelte|[cm]?[jt]sx?|vue)(?::\d+:\d+)?")
_ESLINT_WARNING = re.compile(r"(?P<position>\d+:\d+)\s+warning\s+(?P<message>.+)")
_PROGRESS = tuple(
    re.compile(pattern)
    for pattern in (
        # pytest: an optional test file, one character per test, then [ 45%] (or [ 12/130]). A line with
        # F or E records which file failed, for a run that ends without its failures section: it stays.
        rf"(?:\S+ )?[.sxXR]+\s*{_PERCENT}",
        # pytest-xdist may end a run with the percentage alone.
        _PERCENT,
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
        # pytest-xdist starting its workers, and the worker's platform line above each failure.
        r"created: \d+/\d+ workers?",
        r"bringing up nodes\.\.\.",
        r"scheduling tests via \w+",
        r"\[gw\d+\] \S+ -- Python \S+ .*",
        r"(?:Resolved|Prepared|Installed|Uninstalled|Audited|Downloaded) \d+ packages? in [\d.]+m?s",
        r"(?:Building|Built|Downloading|Downloaded) \S+ (?:@ \S+|\([\d.]+ ?[KMG]i?B\))",
        r"[+~-] [A-Za-z0-9][\w.\[\],-]*(?:==\S+(?: \(from .+\))?| @ \S+)",
    )
)
# pytest's section banners. A filtered section ends at the next banner, at its closing line (the
# documentation link pytest prints last), at a summary line or at any other line that cannot be part of it:
# under -q the final summary has no banner, and the output of a command run after pytest must not be
# filtered with the section.
_BANNER = re.compile(r"={2,} (?P<title>.+?) ={2,}")
_SECTION_END = "-- Docs: "
# The unindented lines of pytest's warnings summary: where each warning was raised (node IDs, "<file>: N
# warnings", "<file>:<line>"); a warning without a location prints its warning line unindented. Any other
# unindented line ends the section, so output after a section without its closing line is never filtered.
_SECTION_HEADER = re.compile(r"\S+\.\w+::\S.*|\S+: \d+ warnings?|\S+:\d+")
_FILTERED_BANNERS = {"test session starts", "warnings summary"}
_FILTERED_SECTIONS = {"warnings summary"}

_FILTERS = (*_PROGRESS, *_NOISE)
# pytest-xdist -v names each test as it starts: the node ID and one space. Matched before stripping, since a
# --collect-only listing, which is the result, prints node IDs without the space.
_STARTED = re.compile(rf"{_NODE_ID} ")
# A count is shorter than this many repeats of any line (two characters each, newline included).
_REPEATS_KEPT = 64

# The Agent Advisory Protocol block grammar (docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md, section 3). A rendered block has no
# empty lines, so an empty line ends one.
_HEADLINES = {sentinel: level for level, sentinel in HEADLINE.items()}
_FIELDS = (*FIELDS, CONTINUATION)
# The lines the scan writes into the excerpt in place of output it left out.
_MARKER = re.compile(r"\[\.\.\. .+ \.\.\.\]")


@dataclass(frozen=True)
class ToolWarning:
    """A warning a tool printed: its message and the first location it named (``""`` when none)."""

    message: str
    location: str = ""


@dataclass(frozen=True)
class Failure:
    """A test the output names as failed: its node ID, ``failed`` or ``error`` (setup, teardown or
    collection), and the message printed with it (``""`` when none)."""

    test: str
    kind: str
    message: str = ""


@dataclass(frozen=True)
class RelayedAdvisory:
    """An advisory block a nested ``devkit`` command printed, as it was printed."""

    level: Level
    text: str


@dataclass(frozen=True)
class Omitted:
    """What did not fit a budget: items per kind, characters of the excerpt."""

    summaries: int = 0
    failures: int = 0
    warnings: int = 0
    advisories: int = 0
    output: int = 0

    def __bool__(self) -> bool:
        return any((self.summaries, self.failures, self.warnings, self.advisories, self.output))


@dataclass(frozen=True)
class Scan:
    """The bounded view of one command's output.

    ``output`` is the excerpt: the output without the relayed advisory blocks,
    its head and its tail with a marker line where characters were left out,
    filtered lines removed.
    """

    summaries: tuple[str, ...] = ()
    failures: tuple[Failure, ...] = ()  # failed tests no line of the excerpt names
    warnings: tuple[ToolWarning, ...] = ()
    advisories: tuple[RelayedAdvisory, ...] = ()
    output: str = ""
    omitted: Omitted = field(default_factory=Omitted)
    filtered: int = 0  # lines filtered out of the excerpt, overwritten progress states included
    last_lines: tuple[str, ...] = ()  # the excerpt's last non-blank lines, within LAST_LINES and LAST_BUDGET
    read: int = 0  # characters read, the whole output


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
    return bool(clean) and (any(pattern.fullmatch(clean) for pattern in _FILTERS) or bool(_STARTED.fullmatch(line)))


class _Excerpt:
    """The first ``HEAD`` and last ``TAIL`` characters of what it is given, in whole pieces, each piece with
    the log line it came from."""

    def __init__(self) -> None:
        self.head: list[str] = []
        self.head_size = 0
        self.head_open = True
        self.tail: deque[tuple[str, int, int]] = deque()
        self.tail_size = 0
        self.dropped = 0  # between head and tail, where the marker line goes
        self.first_dropped = 0  # the log lines the dropped characters came from, 1-based
        self.last_dropped = 0
        self.inline = 0  # inside over-long lines, marked where they were cut

    def add(self, piece: str, first: int, last: int = 0) -> None:
        """Add ``piece``, which stands for log lines ``first`` to ``last`` (``first`` alone by default)."""
        if self.head_open:
            if self.head_size + len(piece) <= HEAD:
                self.head.append(piece)
                self.head_size += len(piece)
                return
            self.head_open = False
        self.tail.append((piece, first, last or first))
        self.tail_size += len(piece)
        while self.tail_size > TAIL:
            left, start, end = self.tail.popleft()
            self.tail_size -= len(left)
            self.dropped += len(left)
            self.first_dropped = self.first_dropped or start
            self.last_dropped = end

    def ending(self) -> str:
        """The end of the excerpt, after the marker line when there is one."""
        tail = "".join(piece for piece, _, _ in self.tail)
        return tail if self.dropped else "".join(self.head) + tail

    def text(self) -> str:
        head = "".join(self.head)
        if not self.dropped:
            return self.ending()
        if head and not head.endswith("\n"):
            head += "\n"
        lines = _lines(self.first_dropped, self.last_dropped)
        return f"{head}[... {self.dropped} characters omitted, {lines} ...]\n{self.ending()}"


def _lines(first: int, last: int) -> str:
    return f"log line {first}" if first == last else f"log lines {first}-{last}"


def _last_lines(text: str) -> tuple[str, ...]:
    """The last non-blank lines of ``text``, newest last, within ``LAST_LINES`` and ``LAST_BUDGET``; a last
    line longer than the budget is cut."""
    found: list[str] = []
    budget = LAST_BUDGET
    for line in reversed(text.splitlines()):
        clean = line.strip()
        if not clean or _MARKER.fullmatch(clean):  # the scan's own marker lines are not output
            continue
        if len(clean) + 1 > budget:
            if not found:
                found.append(clean[: budget - 4] + "...")
            break
        found.append(clean)
        budget -= len(clean) + 1
        if len(found) == LAST_LINES:
            break
    return tuple(reversed(found))


class _Scanner:
    def __init__(self, notices: bool, base: tuple[str, ...]) -> None:
        self.notices = notices
        self.base = base
        self.summaries: list[str] = []
        self.summary_budget = SUMMARY_BUDGET
        # Every failed test, keyed by kind and test in order of appearance, with the first and last log lines
        # naming it; past FAILURES_KEPT only those lines, so it is counted once; past FAILURES_COUNTED, only
        # the number of lines naming one.
        self.failures: dict[tuple[str, str], tuple[Failure, int, int]] = {}
        self.counted: dict[tuple[str, str], tuple[int, int]] = {}
        self.uncounted = 0
        self.warnings: list[ToolWarning] = []
        self.warning_budget = WARNING_BUDGET
        self.seen_warnings: set[str] = set()
        self.advisories: list[RelayedAdvisory] = []
        self.advisory_budget = {True: ADVISORY_BUDGET, False: ADVISORY_BUDGET}  # keyed by "is an error"
        self.block: list[tuple[str, int]] = []  # the advisory block being read, each line with its log line
        self.block_size = 0
        self.excerpt = _Excerpt()
        self.omitted = {"summaries": 0, "failures": 0, "warnings": 0, "advisories": 0}
        self.filtered = 0
        self.section = ""
        self.last_blank = False
        self.source = ""
        self.line = 0  # the log line being fed, 1-based
        self.read = 0
        self.previous = ""  # the last non-blank line the excerpt was given, "" when the last was blank or cut
        self.repeats = 0  # identical lines after it, held back
        self.repeat_lines: list[int] = []  # their log lines, as many as could be given back instead of a count
        self.last_repeat = 0

    def feed(self, line: _Line) -> None:
        self.line += 1
        self.read += line.cut + len(line.text)
        text, overwritten = _visible(line.text)
        cut = line.cut
        if overwritten:
            overwritten += line.cut_returns
        self.filtered += overwritten
        if not cut and text[:9] in _HEADLINES:
            self.close_block()
            self.block, self.block_size = [(text, self.line)], len(text) + 1
            return
        if self.block and not cut and text.strip() and text.startswith(_FIELDS):
            if self.block_size + len(text) + 1 <= ADVISORY_BUDGET:
                self.block.append((text, self.line))
                self.block_size += len(text) + 1
                return
            self.close_block(fits=False)  # longer than any budget: it can never be relayed whole
        self.close_block()
        # A cut line without carriage returns is read from its start: that is where a tool puts what it means.
        prefix = text[:MAX_LINE] if overwritten or not cut else _visible(line.head)[0]
        self.take(text, prefix, self.line, cut=cut, overwritten=bool(overwritten))

    def take(self, text: str, prefix: str, number: int, *, cut: int = 0, overwritten: bool = False) -> None:
        """Classify the visible line ``text`` of log line ``number``, then filter it or give it to the excerpt."""
        complete = not cut and len(text) <= MAX_LINE
        kind = self.classify(prefix, number, oversized=not complete)
        clean = text.strip()
        banner = _BANNER.fullmatch(clean)
        # pytest prints a section's lines unindented only where they start a warning; an indented or cut line
        # inside the section never ends it.
        ends = complete and bool(clean) and text == clean
        closing = ends and clean.startswith(_SECTION_END)
        if banner:
            self.section = banner["title"]
        elif (
            self.section in _FILTERED_SECTIONS
            and ends
            and (
                closing
                or kind in ("summary", "failure")
                or (kind != "warning" and not _SECTION_HEADER.fullmatch(clean))
            )
        ):
            self.section = ""
            if closing:
                self.filtered += 1
                return
        filtered = (banner and banner["title"] in _FILTERED_BANNERS) or self.section in _FILTERED_SECTIONS
        if kind != "failure" and (filtered or is_filtered(text)):  # a line that names a failure always stays
            self.filtered += 1
            return
        # Checked after filtering, so the blank lines around a filtered line collapse too.
        blank = not clean
        if blank and self.last_blank:
            self.filtered += 1
            return
        if not blank and not cut and text == self.previous:
            self.repeats += 1
            if len(self.repeat_lines) < _REPEATS_KEPT:
                self.repeat_lines.append(number)
            self.last_repeat = number
            self.filtered += 1
            return
        self.close_repeats()
        self.last_blank = blank
        self.previous = "" if blank or cut else text
        if cut and not overwritten:
            # Too long to keep: its start (where a tool puts what it means) and its end, marked in between.
            end = text[-MAX_LINE:]
            hidden = cut + len(text) - len(prefix) - len(end)
            self.excerpt.inline += hidden
            text = f"{prefix}\n[... {hidden} characters of {_lines(number, number)} omitted ...]\n{end}"
        chunks = [text[start : start + MAX_LINE] for start in range(0, len(text), MAX_LINE)] or [""]
        chunks[-1] += "\n"
        for chunk in chunks:
            self.excerpt.add(chunk, number)

    def close_repeats(self) -> None:
        """Give the excerpt the identical lines held back: as a count, unless the count is longer."""
        if not self.repeats:
            return
        times = "time" if self.repeats == 1 else "times"
        lines = _lines(self.repeat_lines[0], self.last_repeat)
        marker = f"[... previous line repeated {self.repeats} more {times}, {lines} ...]"
        if len(marker) < self.repeats * (len(self.previous) + 1):
            self.excerpt.add(marker + "\n", self.repeat_lines[0], self.last_repeat)
        else:
            self.filtered -= self.repeats
            for number in self.repeat_lines:
                self.excerpt.add(self.previous + "\n", number)
        self.repeats = self.last_repeat = 0
        self.repeat_lines = []

    def close_block(self, *, fits: bool = True) -> None:
        """Relay the advisory block read so far. A block that does not fit its budget is counted and its lines
        go to the excerpt, so nothing is dropped; a notice block is dropped under ``notices=False``."""
        if not self.block:
            return
        block, self.block, self.block_size = self.block, [], 0
        level = _HEADLINES[block[0][0][:9]]
        text = "\n".join(line for line, _ in block)
        error = level is Level.ERROR
        if fits and level is Level.NOTICE and not self.notices:
            return
        if fits and len(text) + 1 <= self.advisory_budget[error]:
            self.advisories.append(RelayedAdvisory(level, text))
            self.advisory_budget[error] -= len(text) + 1
            return
        self.omitted["advisories"] += 1
        for line, number in block:
            self.take(line, line[:MAX_LINE], number)

    def classify(self, text: str, number: int, *, oversized: bool) -> str:
        """Record ``text`` (log line ``number``) as a failure, a warning or a summary; return which (``""`` for
        none of them)."""
        clean = text.strip().strip("=").strip()
        for pattern in _FAILURES:
            if match := pattern.fullmatch(clean):
                self.add_failure(match["test"], match["kind"], match.groupdict().get("message") or "", number)
                return "failure"
        if not clean:
            self.source = ""
        elif _SOURCE_LOCATION.fullmatch(clean):
            self.source = clean
        if warning := warning_message(clean, self.source):
            self.add_warning(*warning)
            return "warning"
        if oversized or not any(pattern.fullmatch(clean) for pattern in _SUMMARIES):
            return ""
        if clean.startswith("TOTAL"):
            clean = f"Coverage: {clean}"
        if len(clean) + 1 > self.summary_budget:
            self.omitted["summaries"] += 1
            self.summary_budget = 0
            return "summary"
        self.summaries.append(clean)
        self.summary_budget -= len(clean) + 1
        return "summary"

    def add_failure(self, test: str, kind: str, message: str, number: int) -> None:
        kind = "failed" if kind == "FAILED" else "error"
        message = " ".join(message.split())
        if len(message) > FAILURE_MESSAGE:
            message = message[:FAILURE_MESSAGE] + "..."
        key = (kind, test)
        if known := self.failures.get(key):
            failure, first, _ = known
            if message and not failure.message:  # pytest -v names a test before its short summary does
                failure = Failure(test, kind, message)
            self.failures[key] = (failure, first, number)
        elif len(self.failures) < FAILURES_KEPT:
            self.failures[key] = (Failure(test, kind, message), number, number)
        elif key in self.counted or len(self.counted) < FAILURES_COUNTED:
            self.counted[key] = (self.counted.get(key, (number, 0))[0], number)
        else:
            self.uncounted += 1

    def unshown_failures(self) -> tuple[list[Failure], int]:
        """The failed tests no line of the excerpt names, within ``FAILURE_BUDGET``; and how many more."""
        first, last = self.excerpt.first_dropped, self.excerpt.last_dropped

        def cut_out(start: int, end: int) -> bool:  # every line naming it is in the dropped range
            return bool(first) and first <= start and end <= last

        listed: list[Failure] = []
        omitted = self.uncounted + sum(cut_out(start, end) for start, end in self.counted.values())
        budget = FAILURE_BUDGET
        for failure, start, end in self.failures.values():
            if not cut_out(start, end):
                continue
            size = len(failure.test) + len(failure.message) + 1
            if size > budget:
                omitted += 1
                budget = 0
                continue
            listed.append(failure)
            budget -= size
        return listed, omitted

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
        self.close_repeats()
        failures, self.omitted["failures"] = self.unshown_failures()
        return Scan(
            summaries=tuple(self.summaries),
            failures=tuple(failures),
            warnings=tuple(self.warnings),
            advisories=tuple(self.advisories),
            output=self.excerpt.text(),
            omitted=Omitted(**self.omitted, output=self.excerpt.dropped + self.excerpt.inline),
            filtered=self.filtered,
            last_lines=_last_lines(self.excerpt.ending()),
            read=self.read,
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
