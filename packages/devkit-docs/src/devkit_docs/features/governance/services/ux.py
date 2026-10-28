"""The UX documents and use case steps that ``RULE-ux-links`` and ``RULE-ux-coverage`` read
(``ADR-ux-screen-documents``, ``ADR-ux-step-links-and-coverage``).

A use case's steps are the ``N.`` list items under its ``Main Success Scenario`` H2 and the ``- **<key>.**`` bullets
under its ``Extensions`` H2 (``2a``, ``*a``, written ``\\*a`` too). A line indented by at least one space continues the
current item; a non-indented line that opens no item ends it, so an intro paragraph, free prose inside Extensions and
the acceptance scenarios' ``Covers`` lines belong to no step. A step cites a screen when one of its lines holds a body
reference (``CAP-DOCS-document-model`` section 3.3) whose canonical target is a ``UX`` ID, so aliases and the
bracket form count and code blocks never do. Main steps open at column 0, so a nested numbered list continues its
step. An extension resumes at the step named by ``resumes at [step] <key>`` (``resumes at the same step`` names the
step it branches from); without that phrase, or for ``*a`` at the same step, it ends the use case.

A UX document's ``element`` is ``screen``, ``modal`` or ``panel``; its ``Interactions`` H2 holds a table whose header
is ``Trigger | Step | From | To | Target | Capability | Feedback``. A Step cell is empty (``-`` and dashes count as
empty) or one or more `` `UC-<slug>` <key> `` pairs separated by commas or semicolons; a Target cell is empty (the
interaction stays on the element), a UX ID, ``close``, ``back`` or ``end``. A panel is named by an element whose
``Content`` H2 cites the panel's UX ID.

The flow graph is computed per use case: its entries are the elements cited by the first main step, by a main step
whose preceding step cites none and by an extension; its edges are the interactions of the elements the use case's
steps cite and of the panels those elements' Content names. A step is terminal (the element it cites needs no exit)
when it is the last main step, an extension that ends the use case, or a step whose next step (an extension's being
the step it resumes at) cites no element.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field

from devkit_core.core import FrontmatterError
from devkit_core.core.frontmatter import locate

from devkit_docs.features.documents import Document, DocumentIndex, Kind, kind_of, visible_lines
from devkit_docs.features.governance.services.documents import is_material

ELEMENTS = ("screen", "modal", "panel")
COLUMNS = ("trigger", "step", "from", "to", "target", "capability", "feedback")
EXITS = ("close", "back", "end")
MODAL_EXITS = ("close", "back")
EMPTY_CELLS = frozenset({"", "-", chr(0x2013), chr(0x2014)})  # empty, a hyphen, an en dash or an em dash

_H2 = re.compile(r"^##[ \t]+(.+?)[ \t#]*$")
_NUMBERED = re.compile(r"^(?:\d+(?:\.\d+)*\.?[ \t]+)?")
_STEP = re.compile(r"^(\d+)\.[ \t]")
_EXTENSION = re.compile(r"^ {0,3}[-*+][ \t]+\*\*(\\?\*|\d+)([a-z]+)\.\*\*")
_RESUMES = re.compile(
    r"\bresumes?[ \t]+at[ \t]+(?:step[ \t]+)?(\\?\*[a-z]+|\d+[a-z]*|the[ \t]+same[ \t]+step)", re.IGNORECASE
)
_STEP_PAIR = re.compile(r"`(UC-[A-Za-z0-9][A-Za-z0-9_-]*)`[ \t]+(\\?\*[a-z]+|\d+[a-z]*)")
_SEPARATORS = re.compile(r"[\s,;]*")


@dataclass(frozen=True, slots=True)
class Step:
    """One main-scenario step or extension of a use case: ``key`` (``3``, ``2a``, ``*a``), its first and last body
    line, ``resumes`` (the key an extension resumes at, ``None`` when it ends the use case or for a main step) and the
    canonical UX IDs its lines cite, in order."""

    key: str
    line: int
    end: int
    extension: bool
    resumes: str | None
    screens: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UseCase:
    """A use case with its parsed steps, main steps first in document order."""

    document: Document
    steps: tuple[Step, ...]

    def step(self, key: str) -> Step | None:
        return next((step for step in self.steps if step.key == key), None)

    @property
    def main(self) -> tuple[Step, ...]:
        return tuple(step for step in self.steps if not step.extension)

    def citing(self, screen: str) -> list[Step]:
        return [step for step in self.steps if screen in step.screens]

    def cited(self) -> set[str]:
        return {screen for step in self.steps for screen in step.screens}

    def next_step(self, step: Step) -> Step | None:
        """The step after ``step``: the next main step, or the step an extension resumes at."""
        if step.extension:
            return self.step(step.resumes) if step.resumes is not None else None
        main = self.main
        position = main.index(step)
        return main[position + 1] if position + 1 < len(main) else None

    def terminal(self, step: Step) -> bool:
        """Whether the element ``step`` cites needs no exit for it."""
        following = self.next_step(step)
        return following is None or not following.screens

    def entries(self) -> set[str]:
        """The elements a person reaches the use case's screens from."""
        found: set[str] = set()
        previous: Step | None = None
        for step in self.main:
            if previous is None or not previous.screens:
                found.update(step.screens)
            previous = step
        for step in self.steps:
            if step.extension:
                found.update(step.screens)
        return found


@dataclass(frozen=True, slots=True)
class StepRef:
    """One `` `UC-<slug>` <key> `` pair of a Step cell: the canonical use case ID and the normalized key."""

    usecase: str
    key: str


@dataclass(frozen=True, slots=True)
class Interaction:
    """One row of the Interactions table: its line, the Step cell (raw, its pairs and whether it parses) and the
    Target cell (raw, and the canonical UX ID or exit word it names; ``""`` when empty or invalid)."""

    line: int
    step_cell: str
    steps: tuple[StepRef, ...]
    step_valid: bool
    target_cell: str
    target: str

    @property
    def step_empty(self) -> bool:
        return self.step_cell.strip() in EMPTY_CELLS

    @property
    def target_valid(self) -> bool:
        return self.target_cell.strip().strip("`").strip() in EMPTY_CELLS or bool(self.target)


@dataclass(slots=True)
class UxDocument:
    """A UX document as the rules read it: ``element`` as written (``None`` when absent), ``section`` the line of
    its Interactions heading (0 when there is none), ``table`` the line of a well-formed header (0 when there is
    none), the rows, the panels its Content cites and the ``usecases`` entries with their lines."""

    document: Document
    element: object
    section: int = 0
    table: int = 0
    rows: list[Interaction] = field(default_factory=list)
    content: set[str] = field(default_factory=set)
    usecases: list[tuple[str, int]] = field(default_factory=list)

    @property
    def id(self) -> str:
        return self.document.id

    def lists(self, usecase: str) -> bool:
        return any(listed == usecase for listed, _ in self.usecases)

    def targets(self) -> set[str]:
        return {row.target for row in self.rows if row.target and row.target not in EXITS}

    def has_exit(self) -> bool:
        return any(row.target in EXITS or (row.target and row.target != self.id) for row in self.rows)

    def closes(self) -> bool:
        return any(row.target in MODAL_EXITS for row in self.rows)


@dataclass(frozen=True, slots=True)
class Model:
    """Every current UX document and use case of the index, by canonical ID."""

    screens: dict[str, UxDocument]
    usecases: dict[str, UseCase]

    def reachable(self, usecase: UseCase) -> set[str]:
        """The elements reachable from ``usecase``'s entries over its edges."""
        cited = usecase.cited()
        seen: set[str] = set()
        expand: set[str] = set()
        queue = sorted(usecase.entries())
        while queue:
            current = queue.pop()
            if current in seen:
                continue
            seen.add(current)
            screen = self.screens.get(current)
            if screen is None or (current not in cited and current not in expand):
                continue
            panels = {name for name in screen.content if self.element(name) == "panel"}
            expand.update(panels)
            queue.extend(sorted((screen.targets() | panels) - seen))
        return seen

    def element(self, screen_id: str) -> object:
        screen = self.screens.get(screen_id)
        return screen.element if screen is not None else None


def _body(text: str) -> tuple[int, int]:
    """The offset and first line number of the body after the frontmatter."""
    try:
        block = locate(text)
    except FrontmatterError:
        return 0, 1
    return (block.end, block.body_line) if block is not None else (0, 1)


def _lines(text: str) -> Iterator[tuple[int, str]]:
    """``(number, raw text)`` of each prose line of the body: code blocks and comments are skipped."""
    start, first = _body(text)
    for line in visible_lines(text, start=start, first_line=first, mask_links=False, keep_id_spans=True):
        yield line.number, text[line.offset : line.offset + len(line.text)]


def _heading(line: str) -> str | None:
    """The H2 title of ``line`` without a leading section number, lower-cased; ``None`` for any other line."""
    match = _H2.match(line)
    return _NUMBERED.sub("", match.group(1)).strip().lower() if match else None


def _ux_targets(index: DocumentIndex, document: Document, first: int, last: int) -> list[str]:
    """The canonical UX IDs ``document``'s body cites on lines ``first`` to ``last``."""
    found: list[str] = []
    for ref in document.references:
        if ref.field != "body" or not first <= ref.line <= last:
            continue
        target = index.canonical_id(ref.target)
        if kind_of(target) is Kind.UX and target not in found:
            found.append(target)
    return found


def _key(written: str) -> str:
    return written.replace("\\", "")


@dataclass(slots=True)
class _Item:
    key: str
    first: int
    last: int
    extension: bool
    raw: list[str]


def use_case(index: DocumentIndex, document: Document, text: str) -> UseCase:
    """The steps of a use case document."""
    items: list[_Item] = []
    section = ""
    item: _Item | None = None
    for number, raw in _lines(text):
        title = _heading(raw)
        if title is not None or raw.startswith("#"):
            item = None
            if title is not None:
                section = "main" if "main success scenario" in title else "extensions" if "extension" in title else ""
            continue
        if not section:
            continue
        opened = _STEP.match(raw) if section == "main" else _EXTENSION.match(raw)
        if opened is not None:
            key = opened.group(1) if section == "main" else _key(opened.group(1)) + opened.group(2)
            item = _Item(key, number, number, section == "extensions", [raw])
            items.append(item)
        elif item is not None and raw[:1] in (" ", "\t"):
            item.last = number
            item.raw.append(raw)
        else:
            item = None
    steps: list[Step] = []
    for found in items:
        resumes = None
        if found.extension:
            match = _RESUMES.search(" ".join(line.strip() for line in found.raw))
            resumes = _key(match.group(1)) if match else None
            if resumes is not None and resumes.lower().startswith("the"):
                # "resumes at the same step": the step the extension branches from; ``*a`` has none, so it ends.
                stem = found.key.rstrip("abcdefghijklmnopqrstuvwxyz")
                resumes = stem if stem.isdigit() else None
        screens = tuple(_ux_targets(index, document, found.first, found.last))
        steps.append(Step(found.key, found.first, found.last, found.extension, resumes, screens))
    return UseCase(document, tuple(steps))


def _cells(line: str) -> list[str]:
    """The cells of a Markdown table row; ``\\|`` is a literal bar."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", body)]


def _step_refs(index: DocumentIndex, cell: str) -> tuple[tuple[StepRef, ...], bool]:
    if cell.strip() in EMPTY_CELLS:
        return (), True
    pairs = tuple(StepRef(index.canonical_id(m.group(1)), _key(m.group(2))) for m in _STEP_PAIR.finditer(cell))
    rest = _SEPARATORS.fullmatch(_STEP_PAIR.sub("", cell)) is not None
    return pairs, bool(pairs) and rest


def _target(index: DocumentIndex, cell: str) -> str:
    value = cell.strip().strip("`").strip()
    if value in EMPTY_CELLS:
        return ""
    if value in EXITS:
        return value
    canonical = index.canonical(value)
    if canonical is not None and canonical[0].kind is Kind.UX:
        return canonical[0].id
    return ""


def ux_document(index: DocumentIndex, document: Document, text: str) -> UxDocument:
    """A UX document's element, Interactions table, Content citations and ``usecases`` entries."""
    screen = UxDocument(document, document.frontmatter.get("element"))
    screen.usecases = [
        (index.canonical_id(ref.target.strip()), ref.line) for ref in document.references if ref.field == "usecases"
    ]
    section = ""
    content: tuple[int, int] | None = None
    header_seen = False
    in_table = False
    last = 0
    for number, raw in _lines(text):
        last = number
        title = _heading(raw)
        if title is not None:
            if section == "content" and content is not None:
                content = (content[0], number - 1)
            section = (
                "interactions" if title.startswith("interactions") else "content" if title.startswith("content") else ""
            )
            if section == "interactions" and not screen.section:
                screen.section = number
            elif section == "content" and content is None:
                content = (number, number)
            in_table = False
            continue
        if section != "interactions" or screen.section == 0:
            continue
        is_row = raw.lstrip().startswith("|")
        if not header_seen:
            if is_row:
                header_seen = True
                if [cell.lower() for cell in _cells(raw)] == list(COLUMNS):
                    screen.table = number
                    in_table = True
            continue
        if not in_table:
            continue
        if not is_row:
            in_table = False
            continue
        cells = _cells(raw)
        if all(set(cell) <= set(":- ") for cell in cells):
            continue  # the delimiter row
        cells += [""] * (len(COLUMNS) - len(cells))
        steps, valid = _step_refs(index, cells[1])
        screen.rows.append(Interaction(number, cells[1], steps, valid, cells[4], _target(index, cells[4])))
    if content is not None:
        end = content[1] if section != "content" else last
        screen.content = set(_ux_targets(index, document, content[0], max(end, content[0])))
    return screen


def current(index: DocumentIndex, kind: Kind) -> list[Document]:
    """The current documents of ``kind`` outside materials, each canonical ID once, in path order."""
    found: dict[str, Document] = {}
    for document in sorted(index.documents, key=lambda d: d.path):
        if document.kind is kind and not is_material(document) and not index.is_historical(document):
            canonical = index.canonical(document.id)
            if canonical is not None and canonical[0] is document:
                found.setdefault(document.id, document)
    return list(found.values())


def model(index: DocumentIndex, read: Callable[[str], str | None]) -> Model:
    """Every current UX document and use case; ``read(path)`` returns a file's text or ``None``."""
    screens: dict[str, UxDocument] = {}
    for document in current(index, Kind.UX):
        text = read(document.path)
        if text is not None:
            screens[document.id] = ux_document(index, document, text)
    usecases: dict[str, UseCase] = {}
    for document in current(index, Kind.USECASE):
        text = read(document.path)
        if text is not None:
            usecases[document.id] = use_case(index, document, text)
    return Model(screens, usecases)
