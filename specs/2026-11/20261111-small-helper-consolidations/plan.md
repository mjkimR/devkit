---
id: PLAN-small-helper-consolidations
spec: SPEC-small-helper-consolidations
---

# Technical Plan: `SPEC-small-helper-consolidations` Consolidate the remaining duplicated runtime helpers

## 1. Constitution & Invariant Review

None. The helpers land in packages every caller already depends on: `devkit_cli` (a devkit-dist dependency,
exact pin) and `devkit_core.core` (imported by every probe site). devkit-cli keeps depending on click and
devkit-advisory only (`CAP-CLI-agent-cli-toolkit`); devkit-dist imports neither devkit_agt nor the MCP SDK; no
feature edge or ADR is needed. `CAP-DIST-agent-projections` keeps holding: the description stays a double-quoted
scalar with escaped line breaks.

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `devkit_cli.boundary` | `_utf8_output` becomes public `utf8_output()` (same body and docstring); `Boundary` calls it. |
| `devkit_cli` (package root) | Exports `utf8_output` in `__all__`; the public-name pin in `tests/integration/test_lazy_and_package.py` adds it. |
| `devkit_dist.adapters.cli` | Re-exports `utf8_output` beside the other `devkit_cli` names. |
| `devkit_dist.features.host.cli` | `hook` calls the re-exported `utf8_output`; the local copy and its `contextlib`/`io` imports go. |
| `devkit_core.core.frontmatter` | `scalar(value, *, quote="'", always_quote=False)`. |
| `devkit_dist...bundles.subagents` | `_render_markdown` renders `description` through `scalar(quote='"', always_quote=True)`; `_yaml_scalar` keeps the identifier-only plain gate (`_YAML_PLAIN`, `_YAML_RESERVED`) for `name`, string settings and flow-list items and writes every value with `scalar(quote='"', always_quote=not plain)`; `_yaml_quote` removed. |
| `devkit_core.core.git` | `tracked_paths` and `ignored_paths`. |
| Five devkit-dist sites | `host/usecases/registrations.py`, `shared/repositories/local.py`, `distribution/services/installation/local_render.py`, `distribution/repositories/projection_git.py`, `distribution/usecases/sync.py` call the helpers and keep their own policies. |

## 3. Component & Interface Design

```python
# devkit_cli.boundary (exported from devkit_cli)
def utf8_output() -> None: ...

# devkit_core.core.frontmatter
def scalar(value: str, *, quote: str = "'", always_quote: bool = False) -> str:
    """Plain when it reads back and always_quote is false; else quoted with ``quote`` ("'" or '"'),
    double-quoted whenever it holds a line break; ValueError for any other quote."""

# devkit_core.core.git
def tracked_paths(cwd: Path, paths: Collection[str], *, deadline: Deadline | None = None) -> set[str]:
    """The given paths that are tracked or hold tracked files: one ``ls-files -z -- :(literal)<path>...`` call."""

def ignored_paths(
    cwd: Path, paths: Collection[str], *, no_index: bool = False, deadline: Deadline | None = None
) -> set[str]:
    """The given paths Git ignores: one ``check-ignore [--no-index] --stdin -z`` call; exit 1 is the empty set."""
```

Design choices (inside the agreed design):

- `scalar` validates `quote` with `ValueError`, a programming error as elsewhere in `devkit_core.core`.
- `tracked_paths` uses the `:(literal)` pathspec magic per path, not `--literal-pathspecs`, so the Git label in
  errors and deadline messages stays `git ls-files`. It matches each given path against Git's output exactly or as a
  directory prefix (`name == path or name.startswith(path.rstrip("/") + "/")`), which is what host registrations do
  today. Paths are encoded and decoded with UTF-8 `surrogateescape`, matching `os.fsdecode` in `projection_git`.
- `ignored_paths` intersects Git's echoed names with the given paths, so a trailing-slash path (shared storage's
  `.devkit/.shared/`) comes back as given.
- Plain gate: `scalar`'s read-back check is block-context and YAML 1.1 only, so the identifier-only gate stays in
  front of it (spec assumption 2, after review-01).

Site mapping:

| Site | New call | Kept policy |
| --- | --- | --- |
| registrations `_tracked` / `_Eligibility.tracked` | `tracked_paths(root, [relative])` / `tracked_paths(root, relatives)` | Git failure raises |
| registrations `_ignored` / `_Eligibility.ignored` | `ignored_paths(root, [relative])` / `ignored_paths(root, relatives)` | any `AdvisoryError` means not ignored; the batch falls back path by path |
| shared `_eligible` | `RELATIVE in tracked_paths(root, [RELATIVE], deadline=budget)` | `ExclusionError("tracked shared storage cannot be hidden")`; the `--others` query stays |
| shared `_initialize` | `ignored_paths(root, [RELATIVE + "/"], deadline=budget)` | a `GitError` or a missing answer raises `ExclusionError` |
| `local_render.require_ignored` | `tracked_paths(root, [name])`, `ignored_paths(root, [name], no_index=True)` | other `GitError` raised |
| `projection_git_notices` | `tracked_paths(root, sorted(owned))`, `ignored_paths(root, candidates, no_index=True)` | exit-128 skip, otherwise the failure notice |
| sync locked check | `tracked_paths(root, changes)` | `GitError` raised |

## 4. Error Handling & Edge Cases

- `tracked_paths`/`ignored_paths` with no paths return `set()` without Git (`ls-files --` with no pathspec would list
  everything).
- `ignored_paths` accepts exit `0` and `1`; exit `128` (not a repository) and every other status raise `GitError`
  through `run_git_result`; an expired deadline raises `deadline.exceeded(...)`.
- PyYAML's double style escapes NEL, LS, PS and non-printable characters and uses short escapes for seven C0
  controls (spec assumption 1); every rendered value still loads as the original string.

## 5. Verification & Test Plan

- AC-01: new `test_utf8_output_*` in `packages/devkit-cli/tests/integration/test_boundary.py`; the pin in
  `test_lazy_and_package.py`; a re-export assertion in `packages/devkit-dist/tests/integration/adapters/test_cli.py`;
  `rg -n "def _utf8_output" packages/devkit-cli/src packages/devkit-dist/src`.
- AC-02: existing UTF-8 locale tests (devkit-cli `test_boundary.py`, devkit-dist `adapters/test_cli.py`,
  `features/host/test_hooks.py`) unchanged.
- AC-03: new parametrized cases in `packages/devkit-core/tests/unit/core/test_frontmatter.py`; the existing scalar
  table unchanged.
- AC-04: the probe `tmp/probe/bytes.py` (ignored) hashes all 78 renderings before and after; result recorded in
  `reconcile.md`; `uv run devkit sync --check`.
- AC-05: new test in `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py` with
  the literal expected header bytes.
- AC-06: new tests in `packages/devkit-core/tests/integration/core/test_git_helpers.py`.
- AC-07: existing tests of the five sites (`features/host/test_mcp_onboarding.py`, `features/shared/test_shared.py`,
  `features/distribution/test_local_config.py`, `test_execution_rendering.py`, `test_projection_git.py`, sync tests).
- Repository checks: `just lint`, the type check of `docs/development/setup.md`, `just test-affected` (with its
  `mode=full` fallback), `just test-dist`, `uv run devkit sync --check`, `uv run devkit rules check --ci --base main`.
