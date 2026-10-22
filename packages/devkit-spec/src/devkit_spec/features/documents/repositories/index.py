"""The document index of a workspace: every ID-bearing Markdown file under ``docs/`` and ``specs/``.

Every load walks and reads the files; they are the only source of truth.
Symbolic links, directories starting with ``.``, ``README.md`` files and
templates (``*-template.md``, ``*_template.md``) are not documents. A file
that cannot be read or whose frontmatter is malformed is left out and reported
as a ``SPEC_DOCUMENT_INVALID`` warning, so one broken file never hides the
others. IDs and references are repository-wide.

Only the parse of each file is reused, and only for the same path and text:
within a process, so the rules of one run, which each load the index, parse
every file once, and between processes through the parse memo
(``repositories.memo``, ``.devkit/transient/spec/document-index.json``). The ID
and alias maps, ``historical``, the problems and the order are built on every
load.

A document may declare ``aliases``, previous or alternate IDs
(``ADR-document-id-aliases``). ``canonical`` is the one mapping from a written
target to its document: a declared ID always wins, and an alias resolves only
when exactly one document declares it and none has it as its ID. Every lookup
of the index goes through it.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from devkit_core.core import FrontmatterError

from devkit_spec.base.errors import DocumentInvalidWarning, DuplicateIdError, UnresolvedIdError
from devkit_spec.features.documents.models.ids import Kind
from devkit_spec.features.documents.models.model import Document, Reference
from devkit_spec.features.documents.models.parse import parse_document
from devkit_spec.features.documents.repositories.memo import (
    UNSTORABLE_RESULT,
    Entry,
    Invalid,
    MemoError,
    Parsed,
    ParseMemo,
    decode_entry,
    digest,
    encode_entry,
)

SOURCE_DIRECTORIES = ("docs", "specs")
COMPLETED = "completed"
_PARSED_LIMIT = 20_000


@dataclass(slots=True)
class _Parse:
    """The parse result of one path and text, and its memo entry once a memo needed it."""

    result: Parsed
    entry: Entry | None = None


_parsed: dict[tuple[str, str], _Parse] = {}


def is_document_file(name: str) -> bool:
    """Whether a file name can hold an indexed document."""
    return name.endswith(".md") and name != "README.md" and not name.endswith(("-template.md", "_template.md"))


def in_source_directory(relative: str) -> bool:
    """Whether a workspace-relative path lies under ``docs/`` or ``specs/`` outside directories starting with ``.``."""
    parts = relative.split("/")
    return len(parts) > 1 and parts[0] in SOURCE_DIRECTORIES and not any(part.startswith(".") for part in parts[1:-1])


def _parse(relative: str, text: str, memo: ParseMemo | None) -> Parsed:
    """The parse result of ``text`` at ``relative``: the in-process one, else the memo's, else a fresh parse."""
    key = (relative, text)
    found = _parsed.get(key)
    text_digest = None
    if found is None:
        if memo is not None:
            text_digest = digest(text)
            found = _reuse(relative, text, text_digest, memo)
        if found is None:
            found = _Parse(_fresh(relative, text))
        if len(_parsed) >= _PARSED_LIMIT:
            _parsed.clear()
        _parsed[key] = found
    if memo is not None:
        if found.entry is None:
            found.entry = encode_entry(text_digest or digest(text), found.result)
        memo.keep(relative, found.entry)
    return found.result


def _reuse(relative: str, text: str, text_digest: str, memo: ParseMemo) -> _Parse | None:
    """The memo's result for ``relative`` when its entry has ``text_digest`` and can be rebuilt."""
    stored = memo.stored(relative)
    if type(stored) is not list or not stored or stored[0] != text_digest:
        return None
    try:
        result = decode_entry(relative, stored)
    except MemoError:
        memo.unusable()
        return None
    if result is UNSTORABLE_RESULT:
        return _Parse(_fresh(relative, text), stored)
    return _Parse(result, stored)  # type: ignore[arg-type]


def _fresh(relative: str, text: str) -> Parsed:
    try:
        return parse_document(relative, text)
    except FrontmatterError as exc:
        return Invalid(exc.message)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _files(root: Path) -> Iterable[tuple[Path, str]]:
    """Yield ``(path, relative)`` for every document candidate under ``SOURCE_DIRECTORIES``.

    Walks with ``os.scandir``, skipping symbolic links and directories starting with ``.``.
    Directories and files within each directory are traversed in alphabetical order.
    """
    root_str = str(root)
    for directory in SOURCE_DIRECTORIES:
        base_str = os.path.join(root_str, directory)
        if os.path.islink(base_str) or not os.path.isdir(base_str):
            continue
        stack = [(base_str, directory)]
        while stack:
            current_path, current_rel = stack.pop()
            try:
                with os.scandir(current_path) as it:
                    dirs: list[tuple[str, str]] = []
                    files: list[tuple[Path, str]] = []
                    for entry in it:
                        name = entry.name
                        if name.startswith(".") or entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            dirs.append((entry.path, f"{current_rel}/{name}"))
                        elif entry.is_file(follow_symlinks=False) and is_document_file(name):
                            files.append((Path(entry.path), f"{current_rel}/{name}"))
            except OSError:
                continue
            stack.extend(sorted(dirs, key=lambda d: d[1], reverse=True))
            yield from sorted(files, key=lambda f: f[1])


def in_feedback(path: str) -> bool:
    """Whether the workspace-relative ``path`` is in a spec bundle's ``feedback/`` directory
    (``specs/<YYYY-MM>/<bundle>/feedback/...``): feedback stays current when its bundle completes."""
    parts = path.split("/")
    return len(parts) > 4 and parts[0] == "specs" and parts[3] == "feedback"


@dataclass
class DocumentIndex:
    """``documents`` in path order, ``by_id`` every document declaring an ID, ``by_alias`` every document declaring
    an alias, ``problems`` the files left out, ``historical`` the paths of the files of completed spec bundles (work
    history, no longer current), feedback aside: a feedback file stays current until a hygiene session settles it,
    whatever its bundle's status."""

    root: Path
    documents: list[Document] = field(default_factory=list)
    by_id: dict[str, list[Document]] = field(default_factory=dict)
    by_alias: dict[str, list[Document]] = field(default_factory=dict)
    problems: list[DocumentInvalidWarning] = field(default_factory=list)
    historical: set[str] = field(default_factory=set)

    @classmethod
    def load(
        cls, root: Path, *, files: Iterable[Path] | None = None, read: Callable[[Path], str] = _read
    ) -> DocumentIndex:
        """Index the documents under ``root``.

        ``files`` replaces the directory walk (absolute paths; anything that is not a document file under a source
        directory is skipped) and ``read`` the file reader (strict UTF-8; ``UnicodeDecodeError`` and ``OSError``
        become problems), so a rule run reads through its workspace cache.

        The load reuses the parse memo of ``root`` when there is one; only a load with neither ``files`` nor
        ``read`` writes it, and only when an entry changed.
        """
        index = cls(root=root.resolve())
        memo = ParseMemo.open(index.root, writes=files is None and read is _read)
        items: Iterable[tuple[Path, str]] = (
            _files(index.root) if files is None else ((path, path.relative_to(index.root).as_posix()) for path in files)
        )
        for path, relative in items:
            if files is not None and not (is_document_file(path.name) and in_source_directory(relative)):
                continue
            try:
                text = read(path)
            except (OSError, UnicodeDecodeError) as exc:
                index.problems.append(DocumentInvalidWarning(f"{relative}: {exc}", target_files=[relative]))
                continue
            document = _parse(relative, text, memo)
            if isinstance(document, Invalid):
                message = f"{relative}: {document.reason}"
                index.problems.append(DocumentInvalidWarning(message, target_files=[relative]))
            elif document is not None:
                index.add(document)
        if memo is not None:
            memo.save()
        index.documents.sort(key=lambda document: document.path)
        specs = {d.path: d for d in index.documents if d.path.endswith("/spec.md")}
        for document in index.documents:
            if document.kind is Kind.MILESTONE and document.status.lower() in {"done", "dropped"}:
                index.historical.add(document.path)
            bundle = _spec_bundle(document.path)
            spec = specs.get(f"{bundle}/spec.md") if bundle else None
            # Statuses compare case-insensitively, as the spec rules compare them (``RULE-spec-lifecycle``).
            if spec is not None and spec.status.lower() == COMPLETED and not in_feedback(document.path):
                index.historical.add(document.path)
        return index

    def add(self, document: Document) -> None:
        """Index ``document`` under its ID and its aliases (``documents`` keeps insertion order)."""
        self.documents.append(document)
        self.by_id.setdefault(document.id, []).append(document)
        for alias in document.aliases:
            self.by_alias.setdefault(alias, []).append(document)

    def is_historical(self, document: Document) -> bool:
        return document.path in self.historical

    def canonical(self, written: str) -> tuple[Document, str | None] | None:
        """The one document ``written`` names and the alias used (``None`` for a declared ID); ``None`` when no
        document or several match. A declared ID always wins over an alias."""
        found = self.by_id.get(written)
        if found:
            return (found[0], None) if len(found) == 1 else None
        declared = self.by_alias.get(written, [])
        return (declared[0], written) if len(declared) == 1 else None

    def canonical_id(self, written: str) -> str:
        """The ID of the document ``written`` names, or ``written`` itself when it names none or several."""
        found = self.canonical(written)
        return found[0].id if found is not None else written

    def declares(self, document_id: str) -> list[Document]:
        """Every document declaring ``document_id`` as its ID or as an alias, IDs first."""
        return [*self.by_id.get(document_id, []), *self.by_alias.get(document_id, [])]

    def alias_collisions(self) -> list[tuple[str, list[Document]]]:
        """Each alias another document declares as its ID or that several documents declare, with every document
        involved, in alias order."""
        return [
            (alias, self.declares(alias))
            for alias, declared in sorted(self.by_alias.items())
            if len(declared) > 1 or alias in self.by_id
        ]

    def _names(self, written: str, document: Document) -> bool:
        found = self.canonical(written)
        return found is not None and found[0] is document

    def lookup(self, written: str) -> tuple[Document, str | None]:
        """The one document ``written`` names and the alias used; ``UnresolvedIdError`` or ``DuplicateIdError``
        otherwise."""
        found = self.canonical(written)
        if found is not None:
            return found
        if written in self.by_id:
            declared = self.by_id[written]
            paths = [document.path for document in declared]
            raise DuplicateIdError(f"{len(paths)} documents declare the ID {written}", *paths, target_files=paths)
        declared = self.by_alias.get(written, [])
        if declared:
            paths = [document.path for document in declared]
            raise DuplicateIdError(f"{len(paths)} documents declare the alias {written}", *paths, target_files=paths)
        raise UnresolvedIdError(f"no document has the ID {written}", target_files=[written])

    def resolve(self, document_id: str) -> Document:
        """The one document ``document_id`` names, a declared ID or an alias; ``UnresolvedIdError`` or
        ``DuplicateIdError`` otherwise."""
        return self.lookup(document_id)[0]

    def outgoing(self, document: Document) -> dict[str, list[Reference]]:
        """``document``'s references grouped by canonical target ID (an alias with its document), in ID order."""
        return _grouped(document.references, lambda ref: self.canonical_id(ref.target))

    def incoming(self, document_id: str) -> dict[str, list[Reference]]:
        """References to the document ``document_id`` names, written with its ID or an alias that resolves to it,
        grouped by the ID of the referencing document, in ID order."""
        found = self.canonical(document_id)
        if found is None:
            names = {document_id}
        else:
            target = found[0]
            names = {target.id} | {alias for alias in target.aliases if self._names(alias, target)}
        refs = [ref for document in self.documents for ref in document.references if ref.target in names]
        return _grouped(refs, lambda ref: ref.source)


def _spec_bundle(path: str) -> str | None:
    """``specs/<month>/<bundle>`` for a file inside a spec bundle, else ``None``."""
    parts = path.split("/")
    return "/".join(parts[:3]) if len(parts) >= 4 and parts[0] == "specs" else None


def _grouped(refs: Iterable[Reference], key: Callable[[Reference], str]) -> dict[str, list[Reference]]:
    groups: dict[str, list[Reference]] = {}
    for ref in refs:
        groups.setdefault(key(ref), []).append(ref)
    return dict(sorted(groups.items()))
