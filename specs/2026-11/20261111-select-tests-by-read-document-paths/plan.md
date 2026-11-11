---
id: PLAN-select-tests-by-read-document-paths
spec: SPEC-select-tests-by-read-document-paths
---

# Technical Plan: `SPEC-select-tests-by-read-document-paths` Select tests by the repository paths they read

## 1. Constitution & Invariant Review

- `ADR-literal-read-test-selection` decides the design; this plan implements its outcome clauses.
- `ADR-test-selection-and-ci` keeps the selector static and stateless: the scan parses files, never imports them,
  and stores nothing between runs.
- `ARCH-07-deployment` §1.3 keeps every full trigger, explicit data, structural and frontend check; read discovery only
  adds tests, so no MUST changes. §1.3 gains the read-discovery clauses the ADR traces to it.
- No capability documents the selector; no feature edge, package source or managed file changes.

## 2. Architecture Overview & Impact

- Target Area: `scripts/affected_tests.py` (repository tooling), its e2e test, `docs/development/ci-cd.md` and
  `ARCH-07-deployment`.
- No new dependency: the scan uses `ast`, `fnmatch` and `pathlib` from the standard library.

## 3. Component & Interface Design

Read discovery lives in `scripts/affected_tests.py` beside `Workspace`:

- `Workspace._direct(path) -> tuple[frozenset[str], tuple[Path, ...]]`: one file's import nodes and the local helper
  files it reaches, cached per file. `Workspace.imports` becomes a traversal over it with the same results; the
  per-file cache also stops re-walking shared helpers for every test module.
- `Read` (frozen dataclass): `base: str` (repository-relative, never empty) and `pattern: str | None` (a literal glob
  pattern relative to `base`). An exact read, `iterdir`, a runtime join and a non-literal glob are `pattern=None` reads
  of `base`, which select `base` and every path under it.
- `_ReadScanner(root, path, tree).reads() -> set[Read]`: evaluates every maximal anchored expression in one file.
  - Anchor: `Path(__file__)` (also `pathlib.Path`); steps `.resolve()`, `.absolute()`, `.parent`, `.parents[N]`,
    `/ <segment>`, `.joinpath(<segments>)` and `Path(<anchored>, <segments>)`.
  - Segments: string literals, f-strings whose parts resolve, entries of a literal dict and names bound once to such
    strings. A loop variable over a literal tuple or list, a name bound to one, or a literal dict's `keys()`,
    `values()` or `items()` (statement or comprehension, tuple targets included) yields one value per element.
  - Names: resolved in the innermost function scope that binds them, else the module scope, only when bound exactly
    once there. A function parameter takes the arguments (or default) of every call of its function in the same
    file when every use of the function name is such a call. Imports and repeated bindings stay unresolved.
  - A segment that does not resolve turns the value into its base directory (`pattern=None`), and later steps keep it.
  - Consumers: `.glob(<literal>)` and `.rglob(<literal>)` record the pattern (`rglob(p)` is `**/p`); a non-literal
    pattern and `.iterdir()` read the base.
  - Dropped: a value outside the root, equal to the root, or equal to the scanned file itself; the right-hand side of a
    simple name binding (its uses are reads).
- `Workspace.readers(changed: Iterable[str]) -> dict[str, set[str]]`: changed path → test modules (repository
  relative) whose attributed reads match it.
  - Inventory: every `*.py` under a `tests` directory of `packages/*` and `tools/*`, `__pycache__` excluded.
  - Attribution: a test module (`test_*.py`) owns its reads; a `conftest.py` gives them to every test module under its
    directory; any other file gives them to the test modules whose import discovery reaches it. Importers are resolved
    only for files with reads: candidate files whose text names the target's module segment are checked with
    `_direct`, and a reached non-test file becomes a target in turn.
  - Matching: `pattern=None` matches the base or a path under it. A pattern matches when the path below the base or one
    of its ancestors below the base matches segment by segment; `**` matches zero or more segments and other segments
    use `fnmatch.fnmatchcase`.
- `_select`: the per-path loop is unchanged, so full triggers and the unknown-path fallback keep precedence. After the
  loop, `workspace.readers(changed)` adds its tests; a path with no other cause that gains readers adds the cause
  `reads`. A frontend path keeps `frontend=True` and the cause `frontend`.
- `DATA`: `scripts/release.sh` and `justfile` rows add `packages/devkit/tests/integration/package/test_version_script.py`
  (AC-08); the stale comment on `HANDBOOK_TESTS`, the `FRONTEND_PREFIXES` and `UNTESTED_PREFIXES` comments are updated
  to say what still holds.

## 4. Error Handling & Edge Cases

- A test-tree file that does not parse raises `UnsafeGraph` (full selection), as an unparseable imported helper does
  today. Planning measured every test-tree file as parseable.
- A deleted changed path matches by string; a deleted reader no longer exists and is dropped by the existing
  existence filter.
- `tmp_path` literals and unanchored strings have no `Path(__file__)` anchor and are never reads.

## 5. Verification & Test Plan

- `packages/devkit/tests/e2e/package/test_affected_tests.py`:
  - AC-01: one parametrized case per miss group at the repository head.
  - AC-02: a parametrized subset check comparing `select` with read discovery disabled (monkeypatched
    `Workspace.readers`) and enabled, on full-trigger, unknown, `DATA`, source, test and untested paths.
  - AC-03, AC-07: fixture workspaces in `tmp_path` for each read form, attribution and negative case.
  - AC-04: the changed existing assertions; AC-08: `scripts/release.sh` and `justfile`.
- AC-05: `uv run devkit rules check --ci --base main` and `git diff --check`.
- AC-06: a probe under the ignored `tmp/probe/` timing `select(ROOT, ["docs/x.md"])` best of 3 with and without read
  discovery at this head.
- Repository checks: `just lint`, `just check` (Pyright), `just test-affected` (with its `mode=full` fallback),
  `uv run devkit sync --check`.
