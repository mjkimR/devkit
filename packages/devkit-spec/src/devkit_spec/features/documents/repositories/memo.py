"""The parse memo: each document's parse result kept on disk between processes.

An entry is the parse result of one workspace-relative path for one text, keyed
by the BLAKE2b digest of the UTF-8 encoding of the exact text the parser
received (``ADR-content-keyed-document-parse-memo``). It is reused only for
that path and digest, so it can never differ from a fresh parse. A whole memo
is valid only under the parser fingerprint it was written with: a changed
read, parse or codec module, PyYAML version, libyaml presence or Python
version discards it.

The memo is ``<root>/.devkit/transient/spec/document-index.json``, used only
when ``.devkit/transient/`` is a directory and no symbolic link is on the way
(``ADR-parse-memo-location-and-format``). It is JSON in which every list,
mapping, ``datetime`` and ``date`` of a frontmatter is a one-key tagged object
(``l``, ``m`` as key-value pairs, ``t``, ``d``), so every key type and every
value survives; a result holding any other value is stored as "unstorable"
and parsed on every load.

A memo that cannot be read or trusted counts as empty and an entry that cannot
be rebuilt as a miss; only a load that walks the workspace itself writes, only
when its entries changed, by atomic replace and without a lock, and nothing of
this is ever an advisory: one ``logging`` line each, visible under ``-v``
(``ADR-parse-memo-failure-and-write-policy``). Deleting the file is always
safe.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import pkgutil
import stat
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from functools import cache
from pathlib import Path
from typing import Any

import yaml
from devkit_core.core import atomic_write_bytes
from devkit_core.core.logs import get_logger

from devkit_spec.features.documents.models.ids import Kind, kind_of
from devkit_spec.features.documents.models.model import Document, Issue, Reference

_log = get_logger(__name__)

FORMAT_VERSION = 1
MEMO_PARTS = (".devkit", "transient", "spec", "document-index.json")
# The read, parse and codec path: every module of these packages, and these modules.
FINGERPRINT_PACKAGES = ("devkit_spec.features.documents.models", "devkit_spec.features.documents.repositories")
FINGERPRINT_MODULES = ("devkit_core.core.frontmatter", "devkit_core.base.errors")

DOCUMENT = "d"
NO_DOCUMENT = "n"
INVALID = "e"
UNSTORABLE = "u"

_LIST, _MAPPING, _DATETIME, _DATE = "l", "m", "t", "d"


class MemoError(ValueError):
    """A stored entry or value that cannot be rebuilt."""


class Unstorable(ValueError):
    """A parse result holding a value the codec cannot store."""


@dataclass(frozen=True, slots=True)
class Invalid:
    """A malformed frontmatter: ``reason`` is the ``SPEC_DOCUMENT_INVALID`` reason."""

    reason: str


Parsed = Document | Invalid | None
Entry = list[Any]


def digest(text: str) -> str:
    """The key of ``text``: BLAKE2b-128 of its UTF-8 encoding (a lone surrogate kept as is)."""
    return hashlib.blake2b(text.encode("utf-8", "surrogatepass"), digest_size=16).hexdigest()


# --- values ---------------------------------------------------------------------------------------------------------


def encode_value(value: object, active: set[int] | None = None) -> object:
    """``value`` as plain JSON with every list, mapping, ``datetime`` and ``date`` tagged; ``Unstorable`` for any
    other type, a non-finite float, a ``datetime`` whose zone is not a fixed offset, or a cycle."""
    kind = type(value)
    if value is None or kind is str or kind is bool or kind is int:
        return value
    if kind is float:
        if math.isfinite(value):  # type: ignore[arg-type]
            return value
        raise Unstorable("a non-finite float")
    if kind is datetime:
        zone = value.tzinfo  # type: ignore[union-attr]
        if zone is not None and type(zone) is not timezone:
            raise Unstorable("a datetime without a fixed offset")
        return {_DATETIME: value.isoformat()}  # type: ignore[union-attr]
    if kind is date:
        return {_DATE: value.isoformat()}  # type: ignore[union-attr]
    if kind is list or kind is dict:
        active = set() if active is None else active
        if id(value) in active:
            raise Unstorable("a cycle")
        active.add(id(value))
        try:
            if kind is list:
                return {_LIST: [encode_value(item, active) for item in value]}  # type: ignore[union-attr]
            items = value.items()  # type: ignore[union-attr]
            return {_MAPPING: [[encode_value(key, active), encode_value(item, active)] for key, item in items]}
        finally:
            active.discard(id(value))
    raise Unstorable(f"a {kind.__name__}")


def decode_value(value: object) -> Any:
    """The value ``encode_value`` encoded; ``MemoError`` for anything it cannot have produced."""
    kind = type(value)
    if value is None or kind is str or kind is bool or kind is int:
        return value
    if kind is float and math.isfinite(value):  # type: ignore[arg-type]
        return value
    if kind is dict and len(value) == 1:  # type: ignore[arg-type]
        ((tag, inner),) = value.items()  # type: ignore[union-attr]
        if tag == _LIST and type(inner) is list:
            return [decode_value(item) for item in inner]
        if tag == _MAPPING and type(inner) is list:
            return _decode_mapping(inner)
        if tag == _DATETIME and type(inner) is str:
            return _decode_time(datetime.fromisoformat, inner, datetime)
        if tag == _DATE and type(inner) is str:
            return _decode_time(date.fromisoformat, inner, date)
    raise MemoError(f"a stored value of type {kind.__name__} cannot be rebuilt")


def _decode_mapping(pairs: list[Any]) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for pair in pairs:
        if type(pair) is not list or len(pair) != 2:
            raise MemoError("a stored mapping item is not a key-value pair")
        key = decode_value(pair[0])
        try:
            if key in result:
                raise MemoError("a stored mapping repeats a key")
        except TypeError:
            raise MemoError("a stored mapping key is not hashable") from None
        result[key] = decode_value(pair[1])
    return result


def _decode_time(parse: Any, text: str, kind: type) -> Any:
    try:
        value = parse(text)
    except ValueError:
        raise MemoError(f"a stored {kind.__name__} cannot be read") from None
    if type(value) is not kind or value.isoformat() != text:
        raise MemoError(f"a stored {kind.__name__} is not in its stored form")
    return value


# --- entries --------------------------------------------------------------------------------------------------------


def encode_entry(text_digest: str, result: Parsed) -> Entry:
    """The memo entry of ``result`` for the text with ``text_digest``; an unstorable result keeps only its digest."""
    if result is None:
        return [text_digest, NO_DOCUMENT]
    if isinstance(result, Invalid):
        return [text_digest, INVALID, result.reason]
    try:
        return [text_digest, DOCUMENT, _encode_document(result)]
    except (Unstorable, RecursionError):
        return [text_digest, UNSTORABLE]


def _encode_document(document: Document) -> list[Any]:
    if kind_of(document.id) is not document.kind:
        raise Unstorable("a kind that is not the ID's")
    return [
        _string(document.id),
        str(document.kind),
        encode_value(document.frontmatter),
        [_encode_reference(document, reference) for reference in document.references],
        [_encode_reference(document, reference) for reference in document.provenance],
        [_encode_issue(issue) for issue in document.issues],
        [_string(alias) for alias in document.aliases],
        [[_integer(start), _integer(end)] for start, end in document.alias_spans],
        [_encode_issue(issue) for issue in document.alias_issues],
    ]


def _encode_reference(document: Document, reference: Reference) -> list[Any]:
    if reference.source != document.id or reference.path != document.path or type(reference.bracket) is not bool:
        raise Unstorable("a reference that is not the document's own")
    return [
        _string(reference.target),
        _string(reference.field),
        _integer(reference.line),
        _integer(reference.column),
        _integer(reference.start),
        _integer(reference.end),
        reference.bracket,
    ]


def _encode_issue(issue: Issue) -> list[Any]:
    return [_integer(issue.line), _string(issue.message)]


def _string(value: object) -> str:
    if type(value) is not str:
        raise Unstorable("a field that is not a string")
    return value


def _integer(value: object) -> int:
    if type(value) is not int:
        raise Unstorable("a field that is not an integer")
    return value


class _Unstorable:
    """The decoded "unstorable" entry: parse the text again."""


UNSTORABLE_RESULT = _Unstorable()


def decode_entry(relative: str, entry: Entry) -> Parsed | _Unstorable:
    """The parse result of ``entry``, stored for ``relative``; ``UNSTORABLE_RESULT`` for an unstorable entry and
    ``MemoError`` for one that cannot be rebuilt. The caller has matched the digest."""
    tag = entry[1] if len(entry) >= 2 else None
    if tag == NO_DOCUMENT and len(entry) == 2:
        return None
    if tag == UNSTORABLE and len(entry) == 2:
        return UNSTORABLE_RESULT
    if tag == INVALID and len(entry) == 3 and type(entry[2]) is str:
        return Invalid(entry[2])
    if tag == DOCUMENT and len(entry) == 3:
        try:
            return _decode_document(relative, entry[2])
        except (TypeError, ValueError, RecursionError) as exc:
            raise MemoError(f"a stored document cannot be rebuilt: {exc}") from None
    raise MemoError("a stored entry has no known shape")


def _decode_document(relative: str, payload: object) -> Document:
    if type(payload) is not list or len(payload) != 9:
        raise MemoError("a stored document is not a nine-item list")
    document_id, kind, frontmatter, references, provenance, issues, aliases, spans, alias_issues = payload
    if type(document_id) is not str or type(kind) is not str or kind_of(document_id) is not Kind(kind):
        raise MemoError("a stored document has no well-formed ID and kind")
    data = decode_value(frontmatter)
    if type(data) is not dict:
        raise MemoError("a stored frontmatter is not a mapping")
    document = Document(id=document_id, path=relative, kind=Kind(kind), frontmatter=data)
    document.references = [_decode_reference(document, item) for item in _items(references)]
    document.provenance = [_decode_reference(document, item) for item in _items(provenance)]
    document.issues = [_decode_issue(item) for item in _items(issues)]
    document.aliases = tuple(_require_str(item) for item in _items(aliases))
    document.alias_spans = tuple(_decode_span(item) for item in _items(spans))
    document.alias_issues = [_decode_issue(item) for item in _items(alias_issues)]
    return document


def _items(value: object) -> list[Any]:
    if type(value) is not list:
        raise MemoError("a stored field is not a list")
    return value  # type: ignore[return-value]


def _decode_reference(document: Document, item: object) -> Reference:
    if type(item) is not list or len(item) != 7:
        raise MemoError("a stored reference is not a seven-item list")
    target, field, line, column, start, end, bracket = item
    if not (
        type(target) is str
        and type(field) is str
        and type(line) is int
        and type(column) is int
        and type(start) is int
        and type(end) is int
        and type(bracket) is bool
    ):
        raise MemoError("a stored reference has a field of the wrong type")
    return Reference(target, document.id, document.path, field, line, column, start, end, bracket)


def _decode_issue(item: object) -> Issue:
    if type(item) is not list or len(item) != 2 or type(item[0]) is not int or type(item[1]) is not str:
        raise MemoError("a stored issue is not a line and a message")
    return Issue(item[0], item[1])


def _decode_span(item: object) -> tuple[int, int]:
    if type(item) is not list or len(item) != 2 or type(item[0]) is not int or type(item[1]) is not int:
        raise MemoError("a stored alias span is not two offsets")
    return (item[0], item[1])


def _require_str(item: object) -> str:
    if type(item) is not str:
        raise MemoError("a stored alias is not a string")
    return item


# --- fingerprint ----------------------------------------------------------------------------------------------------


def fingerprint_modules() -> tuple[str, ...]:
    """The modules whose source is part of the fingerprint, sorted."""
    names: set[str] = set(FINGERPRINT_MODULES)
    for package in FINGERPRINT_PACKAGES:
        spec = importlib.util.find_spec(package)
        locations = spec.submodule_search_locations if spec is not None else None
        if locations is None:
            raise ImportError(f"{package} is not a package")
        names.add(package)
        names.update(info.name for info in pkgutil.walk_packages(locations, prefix=f"{package}."))
    return tuple(sorted(names))


@cache
def fingerprint() -> str | None:
    """The parser fingerprint of this process; ``None`` when a module's source cannot be read (no memo is used)."""
    hasher = hashlib.blake2b(digest_size=16)
    libyaml = bool(getattr(yaml, "__with_libyaml__", False))
    hasher.update(f"{FORMAT_VERSION}\0{yaml.__version__}\0{libyaml}\0{sys.version}\0".encode())
    try:
        for name in fingerprint_modules():
            spec = importlib.util.find_spec(name)
            origin = spec.origin if spec is not None else None
            if origin is None or not origin.endswith(".py"):
                raise OSError(f"no source file for {name}")
            source = Path(origin).read_bytes()
            hasher.update(f"{name}\0{len(source)}\0".encode())
            hasher.update(source)
    except (OSError, ImportError, ValueError) as exc:
        _log.info("document memo not used: the parser fingerprint cannot be computed: %s", exc)
        return None
    return hasher.hexdigest()


# --- the file -------------------------------------------------------------------------------------------------------


def memo_path(root: Path) -> Path | None:
    """The memo of the resolved ``root``, or ``None`` when ``.devkit/transient/`` is not a directory, a symbolic link
    is on the way, or the path resolves outside ``root``."""
    transient = root / MEMO_PARTS[0] / MEMO_PARTS[1]
    if transient.is_symlink() or not transient.is_dir():
        return None
    path = transient.joinpath(*MEMO_PARTS[2:])
    if path.parent.is_symlink() or path.is_symlink():
        _log.info("document memo not used: a symbolic link at %s", path)
        return None
    try:
        inside = path.resolve().is_relative_to(root)
    except (OSError, RuntimeError):
        inside = False
    if not inside:
        _log.info("document memo not used: %s resolves outside %s", path, root)
        return None
    return path


class ParseMemo:
    """The memo of one load: the entries read from the file and the entries the load keeps.

    ``writes`` marks a load that walks the workspace with the default reader: it reads the file at once and
    ``save`` replaces it when the kept entries differ from those read. Any other load reads the file on the first
    ``stored`` call and never writes.
    """

    def __init__(self, path: Path, fingerprint: str, *, writes: bool) -> None:
        self.path = path
        self._fingerprint = fingerprint
        self._writes = writes
        self._stored: dict[str, Any] | None = None
        self._kept: dict[str, Entry] = {}
        self._changed = False
        self._writable = True
        self._unusable = 0

    @classmethod
    def open(cls, root: Path, *, writes: bool) -> ParseMemo | None:
        """The memo of the resolved ``root``, or ``None`` when it has none (``memo_path``, ``fingerprint``)."""
        path = memo_path(root)
        if path is None:
            return None
        current = fingerprint()
        if current is None:
            return None
        memo = cls(path, current, writes=writes)
        if writes:
            memo._read()
        return memo

    def stored(self, relative: str) -> Any:
        """The raw entry read for ``relative``, or ``None``."""
        if self._stored is None:
            self._read()
        assert self._stored is not None
        return self._stored.get(relative)

    def unusable(self) -> None:
        """Count a stored entry whose digest matched but that could not be rebuilt."""
        self._unusable += 1

    def keep(self, relative: str, entry: Entry) -> None:
        """Keep ``entry`` for ``relative``; a writing load notes whether it differs from the entry read."""
        self._kept[relative] = entry
        if self._writes and not self._changed:
            assert self._stored is not None
            stored = self._stored.get(relative)
            if stored is not entry and stored != entry:
                self._changed = True

    def save(self) -> None:
        """Replace the file with the kept entries when this is a writing load and they changed; log any failure."""
        if self._unusable:
            _log.info("document memo %s: %d stored entries could not be rebuilt", self.path, self._unusable)
        if not self._writes or not self._writable:
            return
        assert self._stored is not None
        if not self._changed and self._stored.keys() == self._kept.keys():
            return
        payload = {"version": FORMAT_VERSION, "fingerprint": self._fingerprint, "entries": self._kept}
        try:
            data = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("ascii")
            atomic_write_bytes(self.path, data)
        except (OSError, ValueError) as exc:
            _log.info("document memo %s not written: %s", self.path, exc)

    def _read(self) -> None:
        self._stored = {}
        try:
            mode = os.lstat(self.path).st_mode
        except FileNotFoundError:
            self._changed = True
            return
        except OSError as exc:
            self._discard(f"cannot be read: {exc}")
            return
        if not stat.S_ISREG(mode):
            self._writable = False
            _log.info("document memo %s not used: not a regular file", self.path)
            return
        try:
            loaded = json.loads(self.path.read_bytes().decode("utf-8"), parse_constant=_no_constant)
        except (OSError, ValueError, RecursionError) as exc:
            self._discard(f"cannot be read: {exc}")
            return
        problem = self._problem(loaded)
        if problem is not None:
            self._discard(problem)
            return
        self._stored = loaded["entries"]

    def _problem(self, loaded: object) -> str | None:
        if type(loaded) is not dict or set(loaded) != {"version", "fingerprint", "entries"}:
            return "not the expected shape"
        if type(loaded["version"]) is not int or loaded["version"] != FORMAT_VERSION:
            return "another version"
        if loaded["fingerprint"] != self._fingerprint:
            return "another parser fingerprint"
        if type(loaded["entries"]) is not dict:
            return "not the expected shape"
        return None

    def _discard(self, reason: str) -> None:
        self._changed = True
        _log.info("document memo %s discarded: %s", self.path, reason)


def _no_constant(name: str) -> Any:
    raise ValueError(f"{name} is not a stored value")
