# The two fingerprinted memos at ba3bcce4

Side-by-side reading of the two persistent memos X-9 names, as of the Planning base `ba3bcce4`. Sources:

- docs parse memo: `packages/devkit-docs/src/devkit_docs/features/documents/repositories/memo.py` (520 lines;
  contract `CAP-DOCS-document-model` 3.4.3-3.4.5, decisions `ADR-document-system`).
- agt rule facts memo: `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/facts.py` (203 lines;
  `FactsStore`, `memo_path`, `facts_fingerprint`), driven by `workspace/file_facts.py` (`FileFactsCache`); contract
  `CAP-GOV-rules-engine` section 5, decision `ADR-rules-run-workspace-cache`.

## What is the same

| Concern | docs parse memo | agt facts memo |
| --- | --- | --- |
| Location root | `<root>/.devkit/transient/` must already be a directory | same |
| Envelope | JSON object `{version, fingerprint, entries}`, `entries` a mapping | same |
| Envelope check | `version` an `int` equal to `FORMAT_VERSION = 1`; fingerprint equal; `entries` a `dict` | same |
| Write | `devkit_core.core.atomic_write_bytes`, no lock, skipped when nothing changed | same; also skipped when the serialized bytes equal those read |
| Failure policy | every read or write failure is a silent miss, never an advisory | same |
| Key | content digest (BLAKE2b) of the exact parsed input, per logical path | same idea (BLAKE2b-512 of cached bytes plus canonical context) |

## What differs (must stay apart or be decided)

| Concern | docs parse memo | agt facts memo |
| --- | --- | --- |
| Extra top-level keys | file discarded (exact key set, `memo.py:504`) | tolerated (`value.get`, `facts.py:131-136`) |
| Path | one file `docs/document-index.json` | one file per rule `rules/facts/<RULE-id>.json`; rule ID validated by regex |
| Directory creation | `docs/` created by `atomic_write_bytes` (parents) | `rules/` and `facts/` created only for a writer (`create=True`) |
| Symlink rejection | at `transient/`, `docs/` and the file; then the file must resolve inside the root | at every component from `.devkit/` down, plus `resolve() != here` for each directory |
| Non-regular file at the path | read as "not used", never written, never removed (`CAP-DOCS-document-model` 3.4.5) | path refused (`None`): no read, no write |
| Malformed JSON constants | `NaN`/`Infinity` rejected for the whole file (`parse_constant`) | accepted by `json.loads`; an entry whose payload fails `canonical_json` aborts the whole load (the `ValueError` is caught around the loop) |
| Entry validation | per entry at use: an entry that cannot be rebuilt is a miss, counted and logged once | per entry at load: wrong shape, digest or non-canonical context skipped; payload decoded at use, failure drops the entry |
| Serialization | compact, insertion order, ASCII | canonical: `sort_keys`, ASCII, no NaN |
| Fingerprint inputs | format version, PyYAML version, libyaml presence, `sys.version`, source of every module of two packages plus four named modules, found by `importlib.util.find_spec` at import | format version, descriptor `schema_version`, Python implementation and `sys.version`, source captured at import of four framework files plus each descriptor's `source_dependencies` |
| Fingerprint hash | `name\0len\0source` streamed into BLAKE2b-128 | name plus BLAKE2b digest of each source into BLAKE2b-512 |
| Logging | one `info` line per event (visible under `-v`, `CAP-DOCS-document-model` 3.4.5) | `debug` with `exc_info` only for caught exceptions; shape, version, fingerprint and path refusals log nothing |
| Writer authority | only a load that walks the workspace with the default reader | only an explicit writer after successful evaluation; pruning by complete path set |
| Readers elsewhere | none | snapshot runs borrow the originating worktree's memo directory read-only |

## Package placement (Q1)

- `devkit-docs` already depends on `devkit-agt`, `devkit-dist` and `devkit-core`
  (`packages/devkit-docs/pyproject.toml`); `devkit_docs.features.documents` already declares the feature edge to
  `devkit_agt.features.rules` (`.devkit/architecture.toml`).
- `devkit-agt` depends on `devkit-core` and `devkit-dist`; it cannot import `devkit_docs`.
- `ARCH-05-2-components` gives `devkit_core.core` "generic filesystem, Git, parsing and plugin primitives";
  `atomic_write_bytes` and `devkit_core.core.paths` already live there and both memos use the former.
- Therefore both `devkit_core.core` and `devkit_agt.features.rules` are reachable from both memos without a new
  package or feature edge. `devkit_core.core` is the only home that is not a rule-engine internal; it needs no new
  third-party dependency (stdlib `json`, `os`, `stat`, `pathlib`).

## Consequences for the helper

- Shareable: the transient-root check, symlink and non-regular rejection given the path parts, and the envelope
  shape check returning a reason; each holds two strictness levels today, so sharing one rule is decision D1.
- Local by contract: the file name and directory layout, the fingerprint inputs, entry shape and validation, the
  serialization order, logging level and wording, writer authority and pruning.
- Path safety is the one point where a single implementation either keeps two policies behind a parameter or
  converges on one; converging changes, slightly, when the docs memo is used (contract wording in
  `CAP-DOCS-document-model` 3.4.3) and needs the user's choice. Challenger round 1 (`envelopes/challenger-01.yaml`)
  narrowed the helper to the path check and the envelope shape check: reads, serialization and writes differ in
  ordering, skip rule and logging and already share `atomic_write_bytes`.
