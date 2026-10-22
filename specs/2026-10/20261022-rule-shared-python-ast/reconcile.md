---
reconcile_id: REC-rule-shared-python-ast
status: pending
targets:
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
---

# Reconcile: `SPEC-rule-shared-python-ast`

## Living Spec changes

- `CAP-GOV-rule-authoring` §2 lists `ctx.cache.get_python_ast(path)`: one parse per file and run from the file's
  bytes as CPython reads source, under the workspace-relative name; the shared tree that a rule MUST NOT modify (a
  rule that needs a changed tree parses its own copy); a fresh `SyntaxError` or `ValueError` of the same type and
  arguments on every call from one parse; `FileNotFoundError` for a missing file; each rule's own report-or-skip
  decision; and that a rule reading Python source parses through the accessor (AC-01, AC-02, AC-06, AC-07;
  `ADR-share-one-read-only-parsed-tree-per-python-file`, `ADR-parse-cached-bytes-once-and-memoize-the-outcome`).
- `CAP-GOV-evaluation-lifecycle` §2 "Cache invalidation" names parsed Python and every remembered path resolution
  among what a fixer's returned paths invalidate (AC-03, AC-04; `ADR-resolve-rule-paths-once-per-run`).
- `CAP-GOV-rules-engine`: principle 3 says the session cache also holds parsed Python (one shared, read-only tree or
  remembered syntax error per file) and resolves each path argument once until an invalidation; the layout comment
  for `cache.py` names parsed Python and per-run path resolution (`review-01.yaml` finding 1).

- Entrypoints (`spec-entrypoints`): `CAP-GOV-rule-authoring` gains
  `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`, the doorway to the workspace cache
  API its §2 documents. Rejected candidates: `cache.py` for `CAP-GOV-evaluation-lifecycle` and `CAP-GOV-rules-engine`
  (they mention the cache only in passing; `CAP-GOV-rules-engine` keeps the package `__init__.py`), `contracts.py`
  (models), the tests, the bundle rule directories (they belong to their own bundles) and `.devkit/installation.json`
  (generated).

## No-impact documents

- `ctx.relative_path` in `CAP-GOV-rule-authoring` §2: the lazy resolution in `RuleContext._relative` returns the same
  value for every input whose resolution succeeds (AC-05); only an in-workspace symlink loop now gets its lexical name
  instead of failing, which the capability does not describe.
- `ctx.cache.write_text` in `CAP-GOV-rule-authoring` §2 still resolves the path (symlinks followed) at write time, as
  stated; it does not use the resolution memo.
- Rules references (`docs/development/reference/rules.md`, `rules-library.md`): they list no `WorkspaceCache` method
  and no CLI output changes; `devkit rules check` stdout and JSON are byte-identical (AC-09).
- `docs/architecture/`: no constraint names how rules read or parse files; `ARCH-08-1-agent-output` holds because no
  output changes.
- Bundle-owned guidance outside `docs/`: the `spec-rule` skill already tells rules to read only through `ctx.cache`;
  the `architecture`, `usecase-boundaries` and `unique_code` guides describe findings, not parsing, and are unchanged.
- The accepted edge-case changes (a BOM, PEP 263 cookie or invalid UTF-8 file; the `usecase-boundaries` abort message
  naming the file) are recorded in `ADR-parse-cached-bytes-once-and-memoize-the-outcome`, Consequences; no capability
  states the earlier behavior.

## Deferred work and source feedback

None: the spec carries no source feedback, and nothing was deferred.
