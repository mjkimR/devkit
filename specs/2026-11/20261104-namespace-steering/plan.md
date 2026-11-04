---
id: PLAN-namespace-steering
spec: SPEC-namespace-steering
---

# Technical Plan: `SPEC-namespace-steering` Namespace steering documents checked and listed beside the global ones

## 1. Constitution & Invariant Review

- `ADR-steering-documents` is superseded in part by `ADR-namespace-steering-directories` (accepted at handoff, pointer
  already written); the root directory's contract stays unchanged.
- `ARCH-05-2-components`: `devkit_dist` imports no application package and its tests run with `devkit-agt` absent.
  The provider is loaded through a new public entry-point group `devkit.context_documents`, added to the group list
  in that document at reconcile. No feature edge changes in `.devkit/architecture.toml`: the provider in
  `devkit_docs.features.documents.services` uses `devkit_docs.features.documents.repositories.config` and
  `namespaces`; `RULE-architecture` must stay clean.
- `CAP-DIST-sync-and-transactions`: `[tool.*]` passes through unread; `devkit-dist` never reads `[tool.docs]`.
- `ARCH-08-1-agent-output`: `get-context` keeps one JSON object on stdout; warnings go to stderr as advisory blocks
  with the stable code `CONTEXT_DOCUMENTS_EXTENSION_FAILED`; exit `1` only under `--strict`.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `devkit_docs.features.governance.usecases.steering_documents` | Checks one directory at a time over `docs_roots(namespaces(ctx))` with `<root>/steering`; per-directory early return and over-cap report; messages name the directory; glossary files reported in a namespace directory. |
| `devkit_docs.features.governance.usecases.document_reference` | `_is_steering` and the steering find-and-fix passes generalized over the same steering directories; the glossary Owner pass stays root-only. |
| `devkit_docs.features.documents.services.context_documents` (new) | The `devkit.context_documents` provider: namespace mirrors to list and to mention, selected by `detect`. |
| `packages/devkit-docs/pyproject.toml` | Entry point `docs = "devkit_docs.features.documents.services.context_documents:provide"` under `devkit.context_documents`. |
| `devkit_dist.features.distribution.services.bundles.context_documents` | Provider loading and validation (`load_providers`, `provided_directories`), merge and de-duplication, `count_documents` for the hint. |
| `devkit_dist.features.distribution.models.results` | `ContextElsewhere(path, files)`; `ContextResult` gains `documents_elsewhere` and `notices`. |
| `devkit_dist.features.distribution.models.errors` | `ContextDocumentsExtensionFailedNotice` (`CONTEXT_DOCUMENTS_EXTENSION_FAILED`, warning). |
| `devkit_dist.features.distribution.usecases.context` | `GetContext.execute(start, bundle, working=None)`: validates `working`, calls the providers, lists and merges, carries notices. |
| `devkit_dist.features.distribution.cli.context` | `--for <dir>` option; default working directory; prints the JSON object, then the notices, `exit_on_warnings`. |
| `docs` bundle text (`AGENTS.md`, `instructions/living-spec-writing.md`, `rules/steering_documents/guide.md`) | Names the namespace directory, `documents_elsewhere` and `--for`. |

No new dependency. The `documents` feature of `devkit-docs` already depends on `devkit_dist.features.project`; the
provider does not import `devkit_dist.features.distribution`.

## 3. Component & Interface Design

### Provider contract (`devkit-dist`, the owner)

```python
# devkit_dist.features.distribution.services.bundles.context_documents
PROVIDER_GROUP = "devkit.context_documents"
type ProviderResult = tuple[Sequence[str], Sequence[str]]      # (to list, to mention), workspace-relative dirs
type Provider = Callable[[Path, Path, str], ProviderResult]   # (root, working, declared directory)

@dataclass(frozen=True)
class ProvidedDirectories:
    listed: tuple[str, ...]
    mentioned: tuple[str, ...]

def provided_directories(root: Path, working: Path, directory: str) -> tuple[ProvidedDirectories, list[AdvisoryError]]:
    """Call every provider in entry-point name order; each item validated with ``seed_target``; a provider that
    fails to load, raises or returns anything else is left out with one CONTEXT_DOCUMENTS_EXTENSION_FAILED."""

def count_documents(root: Path, directory: str) -> int | None:
    """The number of files ``list_documents`` would list; ``None`` when the directory is absent or unsafe."""
```

`GetContext.execute(start, bundle, working: Path | None = None)`:

1. `working` given: must be an existing directory (no symlink in its resolved form required beyond `existing_directory`)
   whose resolved path is the root or under it, else `ArgumentError(target_files=["--for"])`; `None` means the root.
2. After the receipt reads, `directory = declared_directory(...)`; when it is `None`, no provider runs and both lists
   are empty.
3. `provided, notices = provided_directories(root, working, directory)`; `documents` = `list_documents` of the
   declared directory and each `listed` directory, de-duplicated by path, sorted by path; `documents_elsewhere` =
   `ContextElsewhere(str(root / d), count)` for each `mentioned` directory not already listed with a non-`None`
   count, sorted by path.
4. `ContextResult(bundle, constitution, instructions, documents, documents_elsewhere, notices)`.

`to_dict()` adds `"documents_elsewhere": [{"path", "files"}]` and `"notices": [notice.to_dict()]`, as `SyncResult`
serializes its notices.

### CLI

```text
devkit get-context BUNDLE_NAME [--for DIR] [-w ROOT] [--format json] [--strict]
```

`--for DIR` (`click.Path(path_type=Path)`, resolved against the cwd) is passed as `working`; otherwise the CLI passes
`Path.cwd()` when it lies inside the resolved root, else the root. The command prints the JSON object, then
`echo_notices(result.notices)` and `exit_on_warnings(result.notices)` (the `_report_change` pattern); errors keep the
JSON-only boundary.

### `devkit-docs` provider

```python
# devkit_docs.features.documents.services.context_documents
def provide(root: Path, working: Path, directory: str) -> tuple[list[str], list[str]]:
    """Namespace mirrors of a docs/-rooted ``directory``: the one ``detect`` selects to list, the other registered
    namespaces' to mention; nothing without registered namespaces or for another directory. Raises
    DocsConfigError (DOCS_CONFIG_INVALID) on a malformed registry."""
```

`mirror(namespace, directory)` = `f"{namespace.docs}/{rest}"` where `directory == "docs/" + rest`; the mention list
holds every registered namespace's mirror except the listed one, in registry order (devkit-dist sorts the result).

### Rules

`SteeringDocumentsRule.check`: `registered = namespaces(ctx)` (the governance helper that reads the registry through
the cache); `directories = [f"{root}/steering" for root in docs_roots(registered)]`; for each directory run the
existing body with `DIRECTORY` replaced by the directory, returning the concatenated findings; the early return and
the `max_files` slice are per directory. In a namespace directory: `glossary.md` → message naming
`docs/packages/<name>/glossary.md`, `glossary.yaml` → "holds only Markdown files" with the root-synonyms remediation;
neither counted. Root behavior and messages are byte-for-byte unchanged.

`DocumentReferenceRule`: `_steering_files(ctx)` yields `(path)` for every Markdown file directly in any steering
directory of `docs_roots(namespaces(ctx))` other than `README.md`; `_steering` and the fix pass iterate it;
`_quick_references` excludes them; `_glossary` keeps `GLOSSARY` (root).

## 5. Error Handling & Edge Cases

- A provider failure, an unsafe or non-string item, a non-pair result: that provider is dropped with one warning; the
  others and the declared directory stay. `DocsConfigError` from the provider is such a failure.
- A listed directory that is absent or symlinked lists nothing (existing `_directory` rules); a mentioned directory
  that does not exist is dropped; a mentioned directory also listed is not mentioned.
- `--for` validation runs before the receipt read so a bad option never takes the lock.
- A registry without namespaces: the provider returns `([], [])`; the result equals today's.
- `test_context.py` "nested equals root": kept for `constitution` and `instructions`, since `documents` may now
  differ by working directory.

## 6. Verification & Test Plan

| Scenario | Test | Command |
| --- | --- | --- |
| AC-01, AC-02, AC-03 | `rules/steering_documents/tests/test_rule.py` (namespace fixtures via `.devkit/config.toml`) | `just rules-test RULE-steering-documents` after `uv run devkit sync`; `just test devkit-docs` |
| AC-04 | `rules/document_reference/tests/test_rule.py` | `just rules-test RULE-document-reference` |
| AC-05, AC-06, AC-07 | `packages/devkit-dist/tests/integration/features/distribution/test_context_documents.py` with a provider double through `monkeypatch` of `metadata.entry_points` | `just test devkit-dist`; `just test-dist` |
| AC-08, AC-09 | `packages/devkit-docs/tests/integration/test_context_documents.py` (provider unit calls; end-to-end monorepo fixture through the installed entry point) | `just test devkit-docs` |
| AC-10 | `packages/devkit-docs/tests/integration/bundles/...` guidance test and `packages/devkit-spec/tests/integration/bundles/spec/test_steering_guidance.py` | `just test devkit-docs`, `just test devkit-spec` |
| Layering | `RULE-architecture`, `just lint`, `just check` | `just rules-check`, `just lint`, `just check` |

The whole: `just test-affected` (fallback `mode=full`), `just test-dist`, `just lint-check`, `just check`,
`uv run devkit rules check`. Entry-point changes in `pyproject.toml` need `uv sync` before the installed provider test.
