---
id: PADR-parse-cached-bytes-once-and-memoize-the-outcome
title: Parse cached bytes once and memoize the outcome
summary: For a shared AST accessor on WorkspaceCache, we parse cached bytes under the workspace-relative name, memoize the tree or syntax error and call it directly from every rule, to parse once as CPython reads source, accepting changed results on non-UTF-8 files.
proposal: PROP-rule-shared-python-ast
status: draft
created_at: 2026-10-22
---

# [PADR-parse-cached-bytes-once-and-memoize-the-outcome] Parse cached bytes once and memoize the outcome

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Rules reach shared per-run data through `RuleContext.cache`, a `WorkspaceCache`; rules from `.devkit/managed/` run
inside the installed `devkit-agt`. Today the Python-source rules read their input three ways (`Path.read_text()`
outside the cache in the two devkit-dev rules, `ctx.cache.read_text` with replacement in `unique_code` and the
catalog rules) and handle a `SyntaxError` four ways (report per file, abort the rule, or skip). A shared parse needs
one input, one file name in error messages and one error outcome, without changing what each rule reports for valid
source.

## 2. Decision Drivers

- One parse per file and run, including for files that do not parse.
- Valid source yields the same tree for every rule; the file name in error messages stays workspace-relative.
- Results stay byte-identical for UTF-8 source without a BOM; changes on other encodings are acceptable (user).
- Each rule keeps its own reporting policy for unparsable files.
- No compatibility shim: no external consumer exists, and devkit-dist and devkit-agt are released in lockstep.
- Callers without a `RuleContext` (`inspect_architecture`, `inspect_usecases` in tests) keep working.

## 3. Considered Options

- **Input**: parse the cached bytes (CPython's own decoding: BOM and PEP 263 honored, invalid UTF-8 is a
  `SyntaxError`), or parse `read_text` (replacement decoding; a BOM fails to parse; invalid UTF-8 parses as U+FFFD).
- **Errors**: memoize the `SyntaxError`/`ValueError` and raise it on every call, report syntax errors centrally once
  per run, or return `None` for unparsable files.
- **Reaching the API**: call `ctx.cache.get_python_ast(path)` directly, or probe for it with `getattr` and fall back
  to a local parse on an older engine.

## 4. Decision Outcome

- **Accessor**: `WorkspaceCache.get_python_ast(path) -> ast.Module` parses `read_bytes(path)` with
  `ast.parse(data, filename=<name>)`, where `<name>` is the resolved path relative to the workspace root in POSIX form
  (the resolved absolute path for a file outside it), and caches the tree under the cache's resolved-path key.
  Bytes follow CPython's reading of source files (driver 2).
- **Errors**: a `SyntaxError` or `ValueError` from the parse is memoized under the same key without its traceback,
  and every later call raises a fresh, equal exception (same type and arguments), so no rule's frames stay referenced; a missing file raises `FileNotFoundError` like `read_bytes` and is not memoized. Each rule keeps its
  current handling (`architecture` reports, `usecase-boundaries` aborts, `unique_code` and the catalog rules skip), so
  there is no central syntax-error report: a run already reports syntax errors through the language linters, and a
  central report would change rule output (drivers 1 and 3).
- **Invalidation**: `invalidate` (and so `write_text` and `invalidate_many`) and `invalidate_all` drop the tree or
  error with the file's other derived data.
- **Reach**: rules call `ctx.cache.get_python_ast` directly; no `getattr` probe or fallback parse (driver 4). An
  engine without the method fails the rule as a rule execution error.
- **Rule-local entry points**: `inspect_architecture` and `inspect_usecases` take a keyword `cache` that defaults to
  a fresh `WorkspaceCache(root)`, and the rules pass `ctx.cache`; both keep enumerating their declared package roots
  as today, so only the parse moves (driver 5).

## 5. Consequences

- Positive: valid source parses once per run for every migrated rule, and an unparsable file is also parsed once.
- Negative (accepted by the user): on source the repository does not contain today (0 of 822 files), results
  change: a file with a UTF-8 BOM now parses in every rule; a PEP 263 coding cookie (`# coding: latin-1`) is
  honoured; a file with invalid UTF-8 is skipped by `unique_code` and the catalog rules instead of being analysed as
  replaced text; `architecture` reports a decode failure with the `SyntaxError` wording; and the
  `usecase-boundaries` abort message names the file instead of `<unknown>`.
- Risk: a rule enumerating a symlinked path inside the workspace sees the resolved name in a syntax-error message.
- Follow-up: none; a project installing mismatched devkit-catalog and devkit-agt versions sees a rule execution error
  until it upgrades devkit-agt.

## 6. Confirmation

- `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`: same object on repeated calls; a fresh
  parse after `invalidate`, `write_text` and `invalidate_all`; an unparsable file raises an equal `SyntaxError`
  with the workspace-relative name from a distinct exception object on every call while parsing once; a missing file raises `FileNotFoundError`; a BOM
  file parses.
- The migrated rules' existing tests pass unchanged, apart from expectations that name `<unknown>`.
- Review: no migrated rule calls `ast.parse` on a whole file or reads Python source outside `ctx.cache`.
