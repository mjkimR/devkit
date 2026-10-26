---
id: PLAN-foundation-documents
spec: SPEC-foundation-documents
---

# Technical Plan: `SPEC-foundation-documents` Steering documents for project-wide background

## 1. Constitution & Invariant Review

- `ARCH-05-1-containers` section 2.4 keeps `devkit-dist` SDD-agnostic: the context directory is a manifest
  declaration (`ADR-bundle-context-lists-project-documents`), so no steering path enters `devkit-dist`.
- `CAP-DIST-workspace-ownership` states that seeded files are not bundle context; it is amended as the ADR says: a
  declared context directory may list project files, seeded ones included, while seeded files are still never
  receipt-verified context files.
- `ADR-steering-documents-directory` amends the glossary paths that `ADR-spec-package-on-devkit` and
  `ADR-writing-and-terminology-guidance` fix; the ADR states it in its Consequences.
- No kind row (`SPEC-table-driven-document-kinds`): steering files have no ID, so the index, search and every
  kind-keyed rule leave them out unchanged.

## 2. Architecture Overview & Impact

- Target Area: `packages/devkit-dist/src/devkit_dist/features/distribution/` (manifest field, get-context),
  `packages/devkit-spec/src/devkit_spec/` (rules, search, bundle content), `packages/devkit-viewer/frontend/src/lib/`,
  `scripts/handbook.py`, `docs/`.

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/features/`
- `packages/devkit-spec/src/devkit_spec/base/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`
- `packages/devkit-spec/tests/`
- `packages/devkit-dist/src/devkit_dist/features/distribution/`
- `packages/devkit-dist/tests/`
- `packages/devkit-viewer/frontend/src/lib/`
- `packages/devkit-viewer/src/devkit_viewer/static/`
- `scripts/handbook.py`
- `tools/devkit-dev/tests/integration/`
- `docs/`
- `.devkit/installation.json`
- `guides/`

### Excluded Boundaries:
- `A new ID-bearing document kind`
- `Product, brand or style content of any particular project`
- `Changes to the glossary table format`
- `Changes to document search or the search ranker`
- `A namespace copy of the steering directory`
- `handbook/` (frozen for 0.1.4)
- `.devkit/managed/` (written only by `devkit sync`)

### Components

- **Manifest** (`services/bundles/manifest.py`): top-level `context_documents` accepted in `_load`, validated with
  `seed_target` (the seeded `target` grammar) under the context `context_documents`, exposed as
  `Bundle.context_documents: str | None`.
- **Context documents reader** (new `services/bundles/context_documents.py` in devkit-dist): reads the declaration
  from the receipt-verified managed `bundle.toml` bytes, then lists the workspace directory per the ADR read rules.
- **get-context** (`usecases/context.py`, `models/results.py`): `ContextResult.documents: list[ContextDocument]`,
  serialized as `documents` after `instructions`, always present.
- **`RULE-steering-documents`** (new `features/governance/usecases/steering_documents.py`, bundle folder
  `rules/steering_documents/` with `rule.py`, `guide.md`, `tests/test_rule.py`; manifest asset `steering-documents`
  in the presets that hold `document-summary`).
- **`RULE-document-reference`** (`document_reference.py`): `_glossary` reads `docs/steering/glossary.md`; a new
  `_steering` pass resolves backticked IDs in every Markdown file directly in `docs/steering/` and skips the
  (line, ID) pairs the Owner pass already examined.
- **Search** (`usecases/search.py`, `cli/search.py`, `base/errors.py`): `GLOSSARY_PATH = "docs/steering/glossary.yaml"`,
  the error text and help name it.
- **Bundle content**: constitution line in `AGENTS.md.jinja` section 2; `bundle.toml` declaration; role contracts
  `scout`, `challenger`, `reconcile-reviewer`, `development-worker`, `planning-worker` run `devkit get-context spec`;
  seed `docs/steering/glossary.{md,yaml}` (moved, frontmatter added), seed READMEs; instructions, skills, playbooks
  and rule guides with the new path.
- **Handbook script**: one `glossary_source(root, documents)` used by `collect_status` and `render_glossary`.
- **Viewer**: `bookGroup` and `bookGroups`, test in `HandbookMode.test.ts`; `just viewer build` output committed.
- **Living Spec**: glossary moved with frontmatter and the **Steering document** row; capabilities named in the
  spec's `related_capabilities`, `docs/README.md`, `docs/architecture/README.md`; ADR consequence line.

## 3. Component & Interface Design

```python
# devkit_dist.features.distribution.services.bundles.manifest
@dataclass(frozen=True)
class Bundle:
    ...
    context_documents: str | None = None  # workspace-relative directory, seeded-target grammar

# devkit_dist.features.distribution.models.results
@dataclass(frozen=True)
class ContextDocument:
    path: str            # absolute
    title: str | None
    summary: str | None

# devkit_dist.features.distribution.services.bundles.context_documents
HEADER_LIMIT = 4096
def declared_directory(manifest: bytes) -> str | None: ...           # BundleError on an invalid value
def list_documents(root: Path, directory: str | None) -> list[ContextDocument]: ...
```

```json
{"bundle": "spec", "constitution": "...", "instructions": [...],
 "documents": [{"path": "/abs/docs/steering/glossary.md", "title": "Glossary", "summary": "..."}]}
```

`RULE-steering-documents` settings: `max_files` (10), `max_body_bytes` (24576), `max_summary_length` (300), each a
positive integer. Messages:

| Finding | Message |
| --- | --- |
| subdirectory | `steering documents live directly in docs/steering/, not in <dir>/` |
| other file | `docs/steering/ holds only Markdown files and glossary.yaml` |
| id | `steering documents carry no id` |
| title | `steering document has no title` |
| summary | `steering document has no summary` / `summary must be English; it contains <letters>` / `summary has <n> characters (<max> at most)` |
| count | `docs/steering/ has <n> Markdown files; at most <max> are allowed` |
| body | `body has <n> bytes; at most <max> are allowed` |

## 4. Error Handling & Edge Cases

- get-context: a directory path component that is a symlink, absent or not a directory gives `[]`; an entry is
  listed only when `lstat` says regular file and its name ends in `.md` and is not `README.md`; it opens with
  `O_NOFOLLOW` where available and reads at most 4096 bytes; an `OSError`, a UTF-8 error (an incomplete trailing
  sequence of the prefix is dropped first), a missing or unclosed opener, or a `FrontmatterError` gives `null`
  values; a non-string value is `null`. `YAML_BINDING_UNAVAILABLE` still propagates, as for every YAML read.
- The managed `bundle.toml` is hash-verified by `read_owned`; an invalid declaration in it (only a corrupted receipt
  could hold one) is `BUNDLE_INVALID`.
- `RULE-steering-documents` reads files through the rules cache (`find_files`, `read_text_strict`), so staged
  snapshots, exclusions and symlink policy apply; a frontmatter YAML error is reported as missing title and summary
  through the parse of `devkit_core.core.frontmatter` (a `FrontmatterError` reports `steering document frontmatter
  is not valid YAML`).
- Handbook: when the commit lists neither path, `HandbookError(code="HANDBOOK_GLOSSARY_MISSING")`, exit `2`.

## 5. Storage & State Management

- The receipt changes by `devkit sync` only: new managed rule files, the moved seed paths under `seeded` (the seeded
  record follows the seed source), and the new bundle hashes.
- This repository's glossary moves with `git mv` so history follows it.

## 6. Verification & Test Plan

- devkit-dist: `packages/devkit-dist/tests/integration/features/distribution/test_context_documents.py` (AC-01 to
  AC-04), manifest validation cases in the existing manifest tests.
- devkit-spec: `rules/steering_documents/tests/test_rule.py` (AC-06, AC-07, staged commit),
  `rules/document_reference/tests/test_rule.py` (AC-08, AC-09), `tests/integration/features/documents/test_search.py`
  (AC-10), `tests/integration/bundles/spec/test_steering_guidance.py` (AC-05, AC-11, AC-12), the existing
  terminology and package e2e tests updated to the new path.
- Handbook: `tools/devkit-dev/tests/integration/test_handbook_script.py` both layouts and the missing case (AC-14).
- Viewer: `just viewer test`, `just viewer check`, `just viewer lint`, `just viewer build` (AC-15).
- Repository: `just lint`, `just check`, `just test-affected`, `uv run devkit rules check`, `uv run devkit sync
  --check`, `uv run devkit get-context spec` showing the moved glossary under `documents` (AC-13).
- Baseline: the spec names no measured outcome; the before state is base `26f7eb33`, where `get-context` has no
  `documents` key and the glossary is at `docs/glossary.md`.
