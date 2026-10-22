---
id: ADR-resolve-rule-paths-once-per-run
title: Resolve rule paths once per run
summary: For rules runs that resolve the same paths thousands of times, we resolve symlinks in RuleContext only when the lexical form fails and memoize WorkspaceCache keys per run, to save about 0.4 s, accepting that a symlink changed outside the cache mid-run keeps its old key.
proposal: SPEC-rule-shared-python-ast
status: accepted
created_at: 2026-10-22
---

# [ADR-resolve-rule-paths-once-per-run] Resolve rule paths once per run

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

A whole-workspace `devkit rules check` on this repository makes 22,962 `Path.resolve` calls. `WorkspaceCache._key`
resolves its path argument on every cache access (14,727 calls; `read_bytes` resolves twice on a miss), and
`RuleContext._relative` evaluates `absolute.resolve()` on every call even when the lexical form already lies inside
the workspace (7,828 calls through `is_file_targeted` and `settings`). The 14,727 cache resolutions alone take 0.35 s
unprofiled. Each call returns the same answer for the whole run, because the cache already assumes the workspace does
not change outside it between invalidations.

## 2. Decision Drivers

- Rule results and cache keys stay identical for every path whose resolution succeeds, symlinked ones included.
- The cache keeps one consistency contract: what it has read stays valid until `invalidate` or `invalidate_all`.
- `write_text` keeps refusing a path that resolves outside the workspace or into a pinned directory at the moment
  it writes (`PATH_UNSAFE`, `RULES_PINNED_WRITE_REFUSED`).
- The change stays inside the rules engine; no rule or caller changes.

## 3. Considered Options

- **Lazy resolution in `_relative` and a per-run key memo in `WorkspaceCache`**: resolve only when needed and only
  once per path argument between invalidations.
- **Lexical keys** (`os.path.normpath` instead of `resolve`): cheapest, but a symlink and its target would get
  different keys, so a write through one name would not invalidate the other; rejected by driver 1.
- **Keep resolving on every call**: no risk, no saving.

## 4. Decision Outcome

Chosen: **lazy resolution and a per-run key memo**.

- `RuleContext._relative` tries the lexically normalized path first and calls `resolve()` only when that path is
  outside the workspace root. The candidates and their order are unchanged, so it returns the same value for every
  input whose resolution succeeds; only the second, unused resolution disappears (driver 1). An in-workspace symlink
  loop, whose `resolve()` raises `RuntimeError` on Python 3.12, now gets its lexical name instead of failing the
  rule; a loop named as a CLI target still fails, because target expansion resolves it first.
- `WorkspaceCache` memoizes the resolved path of each path argument; `_key` and `read_bytes` use the memo, so a path
  resolves once per run until an invalidation. `invalidate` (and so `write_text` and `invalidate_many`) and
  `invalidate_all` clear the whole memo, as `invalidate` already clears every file listing (driver 2).
- `write_text` resolves its path afresh, without the memo, for the workspace-containment check, the pinned-directory
  check and the write destination (driver 3); writes are rare, so this costs nothing measurable.
- The prototype (`docs/materials/2026-10/20261022-rule-shared-python-ast/measurements.md` §3, path resolution only) cut the median from 4.29 s to 3.87 s with
  byte-identical output, and to 3.23 s together with the shared parse.

## 5. Consequences

- Positive: about 0.4 s less per whole-workspace run; `_relative` no longer touches the file system for paths inside
  the workspace.
- Negative: a symlink created, removed or retargeted outside the cache during a run, with no invalidation, keeps the
  key it resolved to first, so a read returns the old target's cached data where a fresh resolution would follow the
  new target. Writes are unaffected, because `write_text` resolves afresh.
- Follow-up: none.

## 6. Confirmation

- `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`: a path argument resolves once across
  repeated `read_bytes`, `read_text` and `get_python_ast` calls; after `invalidate`, `write_text` and
  `invalidate_all` a retargeted symlink yields its new key; a symlink and its target share one key; after a path is
  read, replacing its parent directory with a symlink to outside the workspace makes `write_text` raise
  `UnsafePathError` (`PATH_UNSAFE`).
- `packages/devkit/tests/integration/features/rules/engine/test_context.py`: its existing symlink and outside-workspace
  tests pass unchanged; a lexically inside path is made relative without calling `Path.resolve`; an absolute path
  through a symlinked alias of the workspace root maps to its relative form; a path through an in-workspace symlink
  to outside keeps its lexical name, and the same path through the root alias returns `None`; `toout/../docs/a.md`
  (with `toout` such a symlink) stays `docs/a.md`; an in-workspace symlink loop gets its lexical name.
- `devkit rules check --format json` on this repository prints the same bytes as before.
