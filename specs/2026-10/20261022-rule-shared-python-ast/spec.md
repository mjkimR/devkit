---
id: SPEC-rule-shared-python-ast
title: Parse each Python file once per rules run
summary: Adds a parsed-AST accessor to the rules workspace cache so Python-source rules share one parse per file and run, and resolves each rule path once per run, removing about 1,000 repeated parses, their garbage collection and most repeated path resolution from devkit rules check.
status: in-progress
created: 2026-10-22
related_capabilities: [CAP-GOV-rule-authoring, CAP-GOV-evaluation-lifecycle, CAP-GOV-rules-engine]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-rule-shared-python-ast] Parse each Python file once per rules run

## 1. Problem Statement & Motivation

Handed off from proposal PROP-rule-shared-python-ast on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-rule-shared-python-ast`
- **Accepted decisions**: `ADR-share-one-read-only-parsed-tree-per-python-file`,
  `ADR-parse-cached-bytes-once-and-memoize-the-outcome`, `ADR-resolve-rule-paths-once-per-run`.

`devkit rules check` takes about 4.0 s on this repository (median 4.29 s at Planning, 4.02 s on this unit's base
47993c48; evidence in `docs/materials/2026-10/20261022-rule-shared-python-ast/measurements.md`). Three rules in this
repository's run parse Python source themselves: the advisory `unique_code` rule and the devkit-dev `architecture`
and `usecase-boundaries` rules make 1,529 exec-mode `ast.parse` calls for 540 files on the base, about 0.8 s of
parsing, and the objects they allocate drive about 0.5 s of cyclic garbage collection. The catalog `cli_tool` rules
`layers`, `heavy_imports`, `command_boundary` and `library_output` parse the same way where a project selects them.
The rules `WorkspaceCache` (`RuleContext.cache`) already shares bytes, text, frontmatter and Markdown links per run,
but not parsed Python.

The same profile shows 22,962 `Path.resolve` calls: `WorkspaceCache._key` resolves on every cache access and
`RuleContext._relative` resolves even when the lexical path already lies inside the workspace.

A prototype that parsed each file once and resolved each path once cut the median from 4.29 s to 3.23 s with
byte-identical output.

### Design

- **Accessor** (`ADR-parse-cached-bytes-once-and-memoize-the-outcome`): `WorkspaceCache.get_python_ast(path) ->
  ast.Module` parses `read_bytes(path)` once per resolved path and run, under the resolved workspace-relative POSIX
  name (the resolved absolute path for a file outside the workspace). A `SyntaxError` or `ValueError` is memoized
  without its traceback and raised again as a fresh, equal exception on every call; a missing file raises
  `FileNotFoundError` like `read_bytes` and is not memoized. `invalidate` (and so `write_text` and
  `invalidate_many`) and `invalidate_all` drop the tree or error.
- **Shared trees** (`ADR-share-one-read-only-parsed-tree-per-python-file`): every caller receives the same cached
  object; a rule never modifies it and parses its own copy when it needs a changed tree.
- **Migrated rules**: `RULE-architecture` (`inspect_architecture(root, config_path, *, cache=None)`),
  `RULE-usecase-boundaries` (`Index` and `inspect_usecases(root, config_path, *, cache=None)`),
  `RULE-advisory-unique-code` (`parse_module` indexes a tree from the accessor) and the catalog `layers`,
  `heavy_imports`, `command_boundary` and `library_output` rules parse through the accessor. `cache=None` defaults
  to a fresh `WorkspaceCache(root)`; the rules pass `ctx.cache`. Every rule keeps its file selection and its handling
  of an unparsable file.
- **Path resolution** (`ADR-resolve-rule-paths-once-per-run`): `RuleContext._relative` resolves only when the
  lexically normalized path is outside the workspace; `WorkspaceCache` memoizes each path argument's resolved path
  until an invalidation clears the whole memo; `write_text` resolves its path afresh.

## 2. User Stories

- **US-1**: As an agent running `devkit rules check` or a commit gate, I want each Python file parsed once per run,
  so that the Python-source rules stop paying for repeated parses and the garbage collection they cause.
- **US-2**: As a rule author, I want one cache accessor that returns a file's parsed tree or its syntax error, so
  that a new Python-source rule needs no reading, decoding or parse handling of its own.
- **US-3**: As a maintainer, I want rule results unchanged for valid UTF-8 source, so that the speed-up changes no
  finding.

## 3. Non-Goals

1. **Scope Excluded**: selecting which rules a targeted run executes, and the `inputs` declarations
   (`SPEC-lint-clean-target-scoped-rules`, already on the base).
2. **Scope Excluded**: changing which files any rule scans, or its findings and messages for valid UTF-8 source
   without a BOM.
3. **Scope Excluded**: sharing or merging the rules' own `ast.walk` traversals (about 0.5 s, rule-internal).
4. **Scope Excluded**: a central syntax-error report, a persistent cross-run cache, or CLI startup time.
5. **Scope Excluded**: `Path.resolve` call sites outside `RuleContext._relative` and the `WorkspaceCache` key
   (`find_files`, target expansion, `DocumentCatalog`).
6. **Scope Excluded**: a compatibility probe or fallback parse for an engine without the accessor; devkit-dist,
   devkit-agt and the content packages release in lockstep.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The accessor returns one shared tree per file
- **Given** a workspace holding `pkg/mod.py` and a `WorkspaceCache` of it
- **When** `get_python_ast` is called with `pkg/mod.py` and again with its absolute path
- **Then** both calls return the same object, equal to `ast.parse` of the file's bytes (`ast.dump` with attributes)

### [AC-02] An unparsable file raises an equal error from one parse
- **Given** a file holding invalid Python and an `ast.parse` wrapper counting exec-mode calls
- **When** `get_python_ast` is called three times on it
- **Then** each call raises a distinct `SyntaxError` object of equal type and arguments whose `filename` is the
  workspace-relative path, and the file is parsed exactly once; a missing file raises `FileNotFoundError` on every
  call; a file starting with a UTF-8 BOM parses

### [AC-03] Invalidation drops the tree or error
- **Given** a parsed file
- **When** the file changes on disk and the cache runs `invalidate`, `invalidate_many`, `write_text` or
  `invalidate_all`
- **Then** the next `get_python_ast` call returns a new tree equal to a fresh parse of the new content

### [AC-04] A path resolves once between invalidations
- **Given** a `WorkspaceCache` and a counter on `Path.resolve`
- **When** the same path argument is passed to `read_bytes`, `read_text` and `get_python_ast` repeatedly
- **Then** it is resolved once; after `invalidate`, `write_text` or `invalidate_all` a retargeted symlink yields its
  new target's content; a symlink and its target share one key; and after a path is read, replacing its parent
  directory with a symlink to outside the workspace makes `write_text` raise `UnsafePathError` (`PATH_UNSAFE`)

### [AC-05] `RuleContext` resolves symlinks only for paths outside the workspace
- **Given** a workspace with `toout` (a symlink to a directory outside it), `loop` (a symlink to itself) and an alias
  path that is a symlink to the workspace root
- **When** `RuleContext.relative_path` maps `docs/a.md`, the alias form of `docs/a.md`, `toout/x.md`, the alias form
  of `toout/x.md`, `toout/../docs/a.md` and `loop`
- **Then** it returns `docs/a.md` without calling `Path.resolve`, `docs/a.md`, `toout/x.md`, `None`, `docs/a.md` and
  `loop`, and the existing context tests pass unchanged

### [AC-06] Migrated rules read Python through the shared accessor
- **Given** each migrated rule (`RULE-architecture`, `RULE-usecase-boundaries`, `RULE-advisory-unique-code` and the
  catalog `layers`, `heavy_imports`, `command_boundary`, `library_output`) and a fixture workspace
- **When** a test builds `RuleContext(workspace_root=root, cache=WorkspaceCache(root))` and calls `rule.check(ctx)`
- **Then** for each Python file the rule scanned, `ctx.cache.get_python_ast(path)` equals a fresh parse, the rule's
  existing tests pass, and the `testing` harness API is unchanged; no migrated rule calls `ast.parse` on a whole
  file or reads Python source outside `ctx.cache`

### [AC-07] Each rule keeps its handling of an unparsable file
- **Given** a fixture with a Python file that does not parse
- **When** each migrated rule checks it
- **Then** `RULE-architecture` reports `cannot parse source: ...` at that file, `RULE-usecase-boundaries` returns one
  `cannot inspect usecase boundaries: ...` finding whose message names the file, and `RULE-advisory-unique-code` and
  the catalog rules skip the file

### [AC-08] One parse per Python file in a whole-workspace run
- **Given** this repository and an `ast.parse` wrapper counting exec-mode calls
- **When** `devkit rules check --format json` runs on the whole workspace
- **Then** no file name is parsed more than once, and the total is at most the number of distinct Python files the
  rules read (540 on the base, against 1,529 parses)

### [AC-09] Byte-identical output on this repository
- **Given** this repository before and after the change
- **When** `devkit rules check --format json` runs on the whole workspace
- **Then** both runs exit 0 and print the same bytes; the comparison is recorded in the unit's evidence

### [AC-10] A whole-workspace run is at least 0.8 s faster
- **Given** one machine, main at or after 8240e402 without the change and with it
- **When** `.venv/bin/devkit rules check --format json` runs 7 times on each
- **Then** the median with the change is at least 0.8 s below the median without it; both numbers are recorded in the
  change report

### [AC-11] The unit stays within its boundaries
- **Given** the finished unit
- **When** `devkit rules check specs/2026-10/20261022-rule-shared-python-ast` runs and the diff from the handoff is
  listed
- **Then** the check exits 0 with no violation, and the diff touches no path under `docs/decisions/` or
  `packages/devkit/src/devkit_agt/features/workflow/`

## 5. Assumptions

1. `SPEC-lint-clean-target-scoped-rules` landed before this unit's Development (main 8240e402, merged into the base
   47993c48). Its `inputs` declarations and `opened_files` helper stay as they are; the migrated rules still open only
   files their `inputs` cover, because the accessor reads the same files through `read_bytes`.
2. AC-10 is measured in this worktree before and after the change, sequentially rather than interleaved, because a
   Development worker creates no second checkout; the Host repeats the measurement on main after integration.
3. `RULE-architecture` catches `SyntaxError` and `ValueError` (which includes the `UnicodeError` it caught before),
   the two errors the accessor memoizes, so a source the parser rejects with `ValueError` is reported like a syntax
   error instead of failing the rule. The catalog rules add `ValueError` to their skip for the same reason;
   `unique_code` already skipped both.
6. A `SyntaxError` prints only the base name of its file (`invalid syntax (broken.py, line 1)`), so the
   `usecase-boundaries` abort message names the file by its base name instead of `<unknown>`.
4. `parse_module(rel, tree)` of `unique_code` takes the parsed tree; the rule calls the accessor and skips a file that
   raises `SyntaxError` or `ValueError`, as before.
5. The catalog `layout` rule lists Python files without parsing them and is not migrated.
