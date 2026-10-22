---
id: PROP-rule-shared-python-ast
title: Parse each Python file once per rules run
summary: "Adds a parsed-AST accessor to the rules workspace cache so every rule that inspects Python source shares one parse per file and run, removing about 1,000 repeated parses and their garbage collection from devkit rules check."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - packages/devkit/tests/integration/features/rules/
    - tools/devkit-dev/src/devkit_dev/bundle/rules/
    - packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/
    - packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/
    - docs/capabilities/governance/
    - .devkit/installation.json
  excludes:
    - docs/decisions/
    - packages/devkit/src/devkit_agt/features/workflow/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-rule-shared-python-ast] Parse each Python file once per rules run

## 1. Background & Hypothesis

`devkit rules check` takes 4.0-4.4 s on this repository (median 4.29 s; evidence in `materials/measurements.md`).
Three rules in this repository's run parse Python source themselves: the advisory `unique_code` rule and the
devkit-dev `architecture` and `usecase-boundaries` rules make 1,526 `ast.parse` calls for about 540 files, 0.82 s of
parsing, and the objects they allocate drive 0.49 s of cyclic garbage collection. They are also the three slowest
rules (0.90 s, 0.80 s and 0.69 s). The catalog `cli_tool` rules `layers`, `heavy_imports`, `command_boundary` and
`library_output` parse the same way where a project selects them. The rules `WorkspaceCache` (`RuleContext.cache`)
already shares bytes, text, frontmatter and Markdown links per run, but not parsed Python. `cli_contract`, named in
the draft, checks CLI citations in Markdown and parses no Python; it is out of scope.

Hypothesis, confirmed by a prototype: one parse per file and run, shared through the cache, makes the run about
0.6 s (14 %) faster with byte-identical output (median 4.29 s to 3.68 s over 7 interleaved runs).

## 2. Technical Spike Questions

- **Q1**: Is a shared `ast.Module` safe to hand to several rules, or does the cache need copies or a read-only view?
  - **Answer**: Share the same object, read-only by contract (`PADR-share-one-read-only-parsed-tree-per-python-file`).
    No rule mutates a node (source review), all 490 shared trees equalled a fresh parse after a full prototype run,
    and deep-copying them costs 1.0 s against 0.4 s to parse them, so copies would erase the saving.
- **Q2**: How do rules loaded from `.devkit/managed` reach the cache API compatibly, and how are syntax errors
  reported once rather than per rule?
  - **Answer**: Rules call `ctx.cache.get_python_ast(path)` directly; `RuleContext.cache` is always a
    `WorkspaceCache` of the installed, lockstep-released engine, and no fallback shim is added
    (`PADR-parse-cached-bytes-once-and-memoize-the-outcome`). A syntax error is parsed once and memoized, then raised
    to every rule that asks; each rule keeps its own reporting (`architecture` reports the file, `usecase-boundaries`
    aborts, the others skip), because a central report would change rule output and the language linters already
    report syntax errors.

## 3. Planning Decisions

- **D1 — Shared read-only trees**: `PADR-share-one-read-only-parsed-tree-per-python-file`.
- **D2 — Accessor contract**: `PADR-parse-cached-bytes-once-and-memoize-the-outcome`: parse the cached bytes under the
  workspace-relative name, memoize the tree or the `SyntaxError`/`ValueError`, drop both on invalidation, call
  directly from every rule.
- **D3 — Only the parse moves**: the two devkit-dev rules keep enumerating their declared package roots
  (`Path.rglob`), and every rule keeps its file selection; only the parse (and with it the read) goes through
  `ctx.cache`. Which rules run for a targeted run is `PROP-lint-clean-target-scoped-rules`, developed after this one.
- **D4 — Per-run lifetime, real-CLI timing**: the trees live on the run's `WorkspaceCache` and need no release step;
  a simulation on that cache gave 4.25 s to 3.69 s. The acceptance measurement times the real CLI process, because an
  in-process timer misses interpreter shutdown.
- **D5 — Memory accepted**: retained trees cost about 40 times the parsed source for the rest of the run; projects
  whose selected rules streamed before (catalog `cli_tool` without devkit-dev) now hold every parsed tree
  (`PADR-share-one-read-only-parsed-tree-per-python-file`, Consequences).
- **Pending question — byte identity on unusual encodings**: the approved goal says byte-identical rule results.
  Parsing bytes keeps them identical for UTF-8 source without a BOM (every file of this repository) but changes
  results for a BOM, invalid UTF-8 or a PEP 263 cookie, and the `usecase-boundaries` abort message names the file
  instead of `<unknown>` (`PADR-parse-cached-bytes-once-and-memoize-the-outcome`, Consequences). Full identity is
  possible instead with trees keyed by decoded source text, each rule keeping its own decoding and the devkit-dev rules
  reading outside `ctx.cache`.
- **Pending question — path resolution**: the profile also shows about 0.4 s of repeated `Path.resolve` in
  `WorkspaceCache._key` and `RuleContext._relative`, in the same module but outside the approved goal. The user decides
  whether this proposal takes it (prototype with both: 4.29 s to 3.23 s, byte-identical) or a separate draft does.

## 4. Proposed Design & Impact

### Accessor

`WorkspaceCache.get_python_ast(path) -> ast.Module` in
`packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`:

- parses `read_bytes(path)` once per resolved path and run, with the resolved workspace-relative POSIX path as the
  file name;
- memoizes a `SyntaxError` or `ValueError` and raises it again on every later call; a missing file raises
  `FileNotFoundError` like `read_bytes`;
- drops the tree or error in `invalidate` (so also after `write_text` and `invalidate_many`) and `invalidate_all`.

### Migrated rules

| Rule | Source | Change |
| --- | --- | --- |
| `RULE-architecture` | `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py` | `inspect_architecture(root, config_path, *, cache=None)` parses through the cache; the rule passes `ctx.cache` |
| `RULE-usecase-boundaries` | `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/rule.py` | `Index` and `inspect_usecases(..., *, cache=None)` parse through the cache |
| `RULE-advisory-unique-code` | `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/` | `parse_module` indexes a tree from `ctx.cache.get_python_ast` |
| catalog `layers`, `heavy_imports`, `command_boundary`, `library_output` | `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/` | replace `ast.parse(ctx.cache.read_text(path), ...)` with the accessor |

`cache=None` defaults to a fresh `WorkspaceCache(root)`, so the bundled tests and
`tools/devkit-dev/tests/integration/test_architecture.py` keep calling the inspectors with a root only.
`usecase-boundaries` keeps its `ast.parse(..., mode="eval")` of string annotations, which is not a file parse.
After changing the bundle sources, `devkit sync` refreshes `.devkit/managed/` and the tracked
`.devkit/installation.json`.

### Living Spec

- `CAP-GOV-rule-authoring` (§2 Rule Context and Workspace Cache) lists `ctx.cache.get_python_ast(path)`, its
  read-only contract and its error behavior, and tells Python-source rules to use it.
- `CAP-GOV-evaluation-lifecycle` names parsed Python among the data a fixer's invalidation drops.
- `CAP-GOV-rules-engine` lists parsed Python in the `cache.py` responsibilities.

### Acceptance outcomes

1. `devkit rules check --format json` on this repository prints the same bytes before and after the change, and for
   UTF-8 source without a BOM every migrated rule reports the same findings and messages as before.
2. A whole-workspace run makes at most one exec-mode `ast.parse` call per distinct Python file the rules read (about
   540 instead of 1,526), measured by wrapping `ast.parse` as `materials/measurements.md` describes.
3. The median wall time of 7 interleaved runs of `.venv/bin/devkit rules check --format json` is at least 0.4 s
   below main's (prototype: 0.61 s), with both numbers recorded in the change report.
4. The cache tests named in the two PADRs' Confirmation sections pass, and each migrated rule's tests build
   `RuleContext(workspace_root=root, cache=WorkspaceCache(root))`, call `rule.check(ctx)` and assert that the trees
   it read equal a fresh parse; the `testing` harness API stays unchanged.
5. The migrated rules' existing tests and the catalog rule tests pass; `just test-affected`, `just lint` and
   `just check` are clean.

### Non-Goals

- Selecting which rules a targeted run executes (`PROP-lint-clean-target-scoped-rules`).
- Changing which files any rule scans, or its findings and messages for valid source.
- Sharing or merging the rules' own `ast.walk` traversals (about 0.5 s, rule-internal).
- A central syntax-error report, a persistent cross-run cache, or CLI startup time.
- Path-resolution changes, unless the pending question adds them.

## 5. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr rule-shared-python-ast "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept rule-shared-python-ast --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff rule-shared-python-ast.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
