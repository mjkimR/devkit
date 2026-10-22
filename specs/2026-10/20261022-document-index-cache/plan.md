---
id: PLAN-document-index-cache
spec: SPEC-document-index-cache
---

# Technical Plan: `SPEC-document-index-cache` Reuse the document index between commands

## 1. Constitution & Invariant Review

- The memo implements `ADR-content-keyed-document-parse-memo`, `ADR-parse-memo-location-and-format` and
  `ADR-parse-memo-failure-and-write-policy` as decided; no new ADR is needed.
- `CAP-DOCS-document-model` lists "a persistent cache or database of documents" as a Non-Goal. The accepted ADRs
  restate it as "a persistent source of truth": the memo holds derived parse results only and never decides which
  files exist. This Unit edits the capability accordingly (`SPEC-document-index-cache` AC-11).
- `ARCH-08-1-agent-output`: the memo adds no stdout, advisory, code or exit status; its diagnostics are `logging`
  lines visible under `-v`.
- Layering: the memo lives in `features/documents/repositories/` beside `index.py`; it imports `models` and
  `devkit_core.core`, never a use case or adapter. No new dependency (`hashlib`, `json`, `importlib` and `pkgutil`
  are standard library; PyYAML is already one).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `features/documents/repositories/memo.py` (new) | The memo: tagged JSON codec of stored parse results, the parser fingerprint, the location checks, reading and validation, and the atomic write. |
| `features/documents/repositories/index.py` | `DocumentIndex.load` digests each text, takes the in-process result, else the stored one, else parses; a walk load with the default reader writes the memo when its entries changed. The in-process memo now also keeps the malformed-frontmatter reason and the encoded entry. Module docstring restated. |
| `docs/capabilities/documents/CAP-DOCS-document-model.md` | Section 1 sentence, the Non-Goal, section 3.4 (memo, key, location, silence, safe deletion). |
| `docs/capabilities/documents/CAP-DOCS-document-lookup.md` | One sentence: the lookups load the index through the memo. |

No other caller of `DocumentIndex.load` changes: walk loads (`list`, `search`, `resolve`, `refs`, proposal and
hygiene use cases) gain the memo; the spec rules (`governance/services/documents.py`) pass a file list and a reader
and only read it.

## 3. Component & Interface Design

```text
DocumentIndex.load(root, files=None, read=_read)
  memo = ParseMemo.open(root, writes=files is None and read is _read)   # None when the location is unusable
  for each file: text = read(path); digest = blake2b(text)
     result, entry = _parsed[(relative, text)]            # in-process
                  or memo.reuse(relative, digest)          # persisted, decoded and validated
                  or parse + encode                        # fresh
     memo.keep(relative, entry)
  memo.save()   # writes only for a walk load whose entries differ from those read
```

Normative interface of the new module (internal to the documents feature, not exported from the package):

```python
FORMAT_VERSION: int = 1
MEMO_PARTS = (".devkit", "transient", "spec", "document-index.json")

@dataclass(frozen=True, slots=True)
class Invalid:            # a malformed frontmatter: the SPEC_DOCUMENT_INVALID reason
    reason: str

Parsed = Document | Invalid | None
Entry = list[object]      # [digest, "d", payload] | [digest, "n"] | [digest, "e", reason] | [digest, "u"]

CODEC_FIELDS: dict[type, tuple[str, ...]]  # the Document, Reference and Issue fields the codec stores

def digest(text: str) -> str
def encode_entry(text_digest: str, result: Parsed) -> Entry  # "u" when a value cannot be stored
def decode_entry(relative: str, entry: Entry) -> Parsed | _Unstorable  # caller matched the digest;
                                                             # UNSTORABLE_RESULT for "u"; MemoError when not rebuildable
def encode_value(value: object, active: set[int] | None = None) -> object  # raises Unstorable
def decode_value(value: object) -> Any                       # raises MemoError
def fingerprint_modules() -> tuple[str, ...]
def fingerprint() -> str | None    # computed once at import; None when a module's source cannot be read
def memo_path(root: Path) -> Path | None

class ParseMemo:
    @classmethod
    def open(cls, root: Path, *, writes: bool) -> ParseMemo | None
    def stored(self, relative: str) -> Any                   # the raw entry read for the path, or None
    def unusable(self) -> None                               # count an entry whose digest matched but did not decode
    def keep(self, relative: str, entry: Entry) -> None
    def save(self) -> None
```

Codec tags: `{"l": [...]}` list, `{"m": [[key, value], ...]}` mapping (any key type, order kept),
`{"t": "<isoformat>"}` `datetime` (checked before `date`, offset kept), `{"d": "<isoformat>"}` `date`. Exact types
only: `str`, `bool`, `int`, finite `float` and `None` stay plain; a set, tuple, bytes, non-finite float, any other
type or a cycle is unstorable. A document payload is
`[id, kind, frontmatter, references, provenance, issues, aliases, alias_spans, alias_issues]`, a reference
`[target, field, line, column, start, end, bracket]` whose `source` and `path` are the document's (an encoder that
finds otherwise stores the entry as unstorable).

Fingerprint: computed once when the memo module is imported, right after the modules it covers; BLAKE2b over the
format version, the name and source bytes of every module of
`devkit_spec.features.documents.models` and `devkit_spec.features.documents.repositories` (enumerated with
`pkgutil`), `devkit_core.core.frontmatter` and `devkit_core.base.errors`, `yaml.__version__`,
`yaml.__with_libyaml__` and `sys.version`.

Choices made inside the agreed design:

- Entries are a JSON object keyed by path with compact list values, which keeps the file small and lets a load
  decode only the entries it reuses. Reason: the decision fixes the tags and the key, not the entry layout.
- The memo is read lazily for loads with a supplied file list: a rule run whose files all hit the in-process memo
  never reads it. A walk load always reads it, because its write decision compares against it. Reason: no behavior
  difference, fewer reads in a rule run.
- Change detection compares the raw entry read with the entry the load keeps, so a malformed entry, a new digest, a
  new path or a removed path all count as a change, and an unchanged unstorable entry does not.
- The JSON is written ASCII-escaped (`ensure_ascii=True`), so a frontmatter string holding a lone surrogate from a
  YAML escape stays storable. Reason: a valid UTF-8 file in every case; size grows only for non-ASCII text.

## 4. Storage & State Management

- `<root>/.devkit/transient/spec/document-index.json`, Git-ignored through `.devkit/.gitignore`, one per worktree.
  `spec/` is created on the first write. Deleting the file is always safe.
- The in-process memo `_parsed` stays keyed by `(path, text)` with its size limit; it now maps to the parse result and
  its encoded entry.

## 5. Error Handling & Edge Cases

| Case | Behavior |
| --- | --- |
| No `.devkit/transient/` directory; a symbolic link at `transient/`, `spec/` or the memo; memo resolving outside `<root>` | No memo: no read, no write, no file or directory created. |
| A module's source unreadable for the fingerprint | No memo. |
| Memo missing, unreadable, not UTF-8 JSON, wrong shape, other `version` or `fingerprint` | Treated as empty; one `-v` log line; a walk load rewrites it. |
| An entry that cannot be rebuilt (wrong shape, unknown tag, bad types, digest mismatch) | A miss: the file is parsed; a walk load rewrites the memo. |
| A directory or other non-regular file at the memo path | Not read, never removed or written; one `-v` log line. |
| `OSError` while writing (permissions, full disk, `spec` a file) | Logged under `-v` and ignored; `atomic_write_bytes` leaves the target unchanged. |
| Concurrent writers | No lock; each writes a complete memo by rename; the last one wins. |

## 6. Verification & Test Plan

- Unit (`packages/devkit-spec/tests/unit/features/documents/test_memo.py`): codec round trips and unstorable values
  (AC-03); entry decoding refuses each malformed shape; fingerprint coverage under `sys.settrace` of a read, a parse
  of valid and malformed documents, an encode and a decode (AC-09).
- Integration (`packages/devkit-spec/tests/integration/features/documents/test_memo_index.py`): with-memo versus
  fresh loads after every AC-01 change, a Git branch switch in a fixture repository, CLI `list`, `search`, `resolve`
  and `refs` stdout and exit codes (AC-01); CRLF, lone-CR and BOM documents through a walk and a supplied reader in
  both orders, and `devkit rules check` and `devkit rules fix` with and without a memo (AC-02); corrupt memos through
  the CLI with stderr checked (AC-04); directory and unwritable paths (AC-05); concurrent threads (AC-06);
  no-transient and symbolic-link cases (AC-07); unchanged bytes and modification time, supplied-list loads (AC-08).
- Recorded runs (`specs/2026-10/20261022-document-index-cache/materials/speed.md`): the AC-10 timing script and the
  AC-06 multi-process run, executed from the ignored `scratch/` directory.
- Checks: `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `uv run devkit rules check`,
  `git diff --check` (AC-11).
