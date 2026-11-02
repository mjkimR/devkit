---
id: ADR-rules-run-workspace-cache
title: Share parsed sources, resolved paths and indexes once per rules run in WorkspaceCache
summary: "For rules runs that repeat parsing, path resolution, indexing and fact extraction, we share one read-only tree, node index, path key and DocumentIndex per run in WorkspaceCache and persist rule-owned Python facts, to do each once, accepting read-only contracts and retained memory."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-parse-cached-bytes-once-and-memoize-the-outcome
  - ADR-share-one-read-only-parsed-tree-per-python-file
  - ADR-index-python-ast-nodes-by-type-in-workspacecache
  - ADR-resolve-rule-paths-once-per-run
  - ADR-share-document-index-and-defer-catalog-build-in-rules-run
  - ADR-pull-per-file-python-facts
  - ADR-persist-python-facts-and-reuse-in-snapshots
---

# [ADR-rules-run-workspace-cache] Share parsed sources, resolved paths and indexes once per rules run in WorkspaceCache

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `WorkspaceCache`, `RuleContext`, the Python-source and Markdown rules,
  `CAP-GOV-rule-authoring`

---

## 1. Context & Problem Statement

Rules reach shared per-run data through `RuleContext.cache`, a `WorkspaceCache`; rules from `.devkit/managed/` run
inside the installed `devkit-agt`. Several kinds of per-run work are repeated across rules and calls:

- **Python parse and AST**: three Python-source rules in this repository's run (`architecture`, `usecase-boundaries`,
  `unique_code`) and four catalog `cli_tool` rules each parse every Python file they inspect: 1,526 parses of about
  540 files per `devkit rules check`, 0.82 s of parsing plus the garbage collection those objects cause. A per-run
  cache can parse each file once, but only if handing the same `ast.Module` to several rules cannot change any rule's
  result. The Python-source rules read their input three ways (`Path.read_text()` outside the cache in the two
  devkit-dev rules, `ctx.cache.read_text` with replacement in `unique_code` and the catalog rules) and handle a
  `SyntaxError` four ways (report per file, abort the rule, or skip). A shared parse needs one input, one file name in
  error messages and one error outcome, without changing what each rule reports for valid source. With one shared
  tree per file, multiple Python-source rules (`RULE-architecture`, `RULE-usecase-boundaries`,
  `RULE-advisory-unique-code`, `RULE-cli-tool-command-boundary`, `RULE-cli-tool-library-output`) still each walk the
  shared tree across all workspace files, taking about 1.75 million `ast.walk` steps and adding about 0.5 s to
  `devkit rules check`.
- **Path resolution**: a whole-workspace `devkit rules check` on this repository makes 22,962 `Path.resolve` calls.
  `WorkspaceCache._key` resolves its path argument on every cache access (14,727 calls; `read_bytes` resolves twice on
  a miss), and `RuleContext._relative` evaluates `absolute.resolve()` on every call even when the lexical form already
  lies inside the workspace (7,828 calls through `is_file_targeted` and `settings`). The 14,727 cache resolutions alone
  take 0.35 s unprofiled. Each call returns the same answer for the whole run, because the cache already assumes the
  workspace does not change outside it between invalidations.
- **Shared DocumentIndex**: evaluating Markdown rules during a rules run (such as `devkit workflow next` running
  `lint-clean` on targeted files) is bottlenecked by redundant indexing. Seven spec rules independently call
  `document_index(ctx)`, each triggering `DocumentIndex.load`, which scans, reads and hashes all ~690 Markdown files,
  totaling over 300 ms across the run even with a warm parse memo. `RULE-markdown-link` unconditionally constructs
  `DocumentCatalog` across the entire workspace upon evaluation, scanning every Markdown file even when all links in
  the targeted files are valid and no repair candidate lookup is needed.
- **Python facts**: Python rules retain ASTs in memory but start cold in every process. The three target rules own
  their discovery and cross-file judgments. Their AST use includes facade bindings, inherited advisory constants and
  transport callback scopes; a list of imports/classes cannot preserve all their behavior. Facts require a disposable
  memo that cannot change rule results. Document memo identity and safe storage are useful precedents, but its
  writers exclude rule runs. Python facts need deliberate working-tree warming and snapshot read-only borrowing to
  benefit commit gates without changing snapshot code or policy authority.

---

## 2. Decision Drivers

Drivers are listed per source decision; a "(driver N)" in Decision Outcome refers to the list of the clause's source.

### Python parse and AST

`ADR-parse-cached-bytes-once-and-memoize-the-outcome`:

1. One parse per file and run, including for files that do not parse.
2. Valid source yields the same tree for every rule; the file name in error messages stays workspace-relative.
3. Results stay byte-identical for UTF-8 source without a BOM; changes on other encodings are acceptable (user).
4. Each rule keeps its own reporting policy for unparsable files.
5. No compatibility shim: no external consumer exists, and devkit-dist and devkit-agt are released in lockstep.
6. Callers without a `RuleContext` (`inspect_architecture`, `inspect_usecases` in tests) keep working.

`ADR-share-one-read-only-parsed-tree-per-python-file`:

1. Rule results stay byte-identical to separate parses.
2. The saving survives: whatever the cache returns must cost much less than a parse.
3. The contract stays simple enough for a new rule author to follow.

`ADR-index-python-ast-nodes-by-type-in-workspacecache`:

1. Rule results remain byte-identical to individual tree walks.
2. Redundant AST traversals across rules are eliminated from `devkit rules check`.
3. Memory overhead for retained node indices remains minimal and predictable.
4. The accessor contract remains simple and composable for rule authors.

### Path resolution

`ADR-resolve-rule-paths-once-per-run`:

1. Rule results and cache keys stay identical for every path whose resolution succeeds, symlinked ones included.
2. The cache keeps one consistency contract: what it has read stays valid until `invalidate` or `invalidate_all`.
3. `write_text` keeps refusing a path that resolves outside the workspace or into a pinned directory at the moment
   it writes (`PATH_UNSAFE`, `RULES_PINNED_WRITE_REFUSED`).
4. The change stays inside the rules engine; no rule or caller changes.

### Shared DocumentIndex

`ADR-share-document-index-and-defer-catalog-build-in-rules-run`:

1. Rule findings remain identical for both whole-workspace and targeted runs.
2. Redundant file reads, hashes, and AST/catalog constructions across rules are eliminated from rules evaluation.
3. Package boundaries between `devkit-agt` (foundation harness) and `devkit-spec` (spec extension) remain strict and
   acyclic.
4. Invalidation upon autofix (`ctx.cache.write_text`) reliably purges cached indices before convergence rechecks.

### Python facts

`ADR-pull-per-file-python-facts`:

1. Results equal cache-disabled evaluation after source, configuration and cross-file edits.
2. Existing rule discovery, selection and direct library callers retain one evaluation path.
3. Helper edits and editable installations invalidate persisted extraction without manual release bumps.

`ADR-persist-python-facts-and-reuse-in-snapshots`:

1. Missing, corrupt or unwritable derived state never changes findings, advisories or exit status.
2. Staged and CI snapshots execute their own code and source identities.
3. No lock wait; unchanged runs write nothing; partial runs do not erase unseen entries.

---

## 3. Considered Options

### Python parse and AST

- **Input**: parse the cached bytes (CPython's own decoding: BOM and PEP 263 honored, invalid UTF-8 is a
  `SyntaxError`) (selected); parse `read_text` (replacement decoding; a BOM fails to parse; invalid UTF-8 parses as
  U+FFFD) (rejected in `ADR-parse-cached-bytes-once-and-memoize-the-outcome`).
- **Errors**: memoize the `SyntaxError`/`ValueError` and raise it on every call (selected); report syntax errors
  centrally once per run, or return `None` for unparsable files (rejected in
  `ADR-parse-cached-bytes-once-and-memoize-the-outcome`).
- **Reaching the API**: call `ctx.cache.get_python_ast(path)` directly (selected); probe for it with `getattr` and
  fall back to a local parse on an older engine (rejected in `ADR-parse-cached-bytes-once-and-memoize-the-outcome`).
- **Shared tree, read-only by contract** (selected): every caller receives the same cached object. Costs nothing per
  call; correctness depends on no rule mutating a tree.
- **Deep copy per call** (rejected in `ADR-share-one-read-only-parsed-tree-per-python-file`): isolates rules
  completely. Copying all 490 distinct trees takes 1.00-1.04 s against 0.38-0.40 s to parse them, so it is slower
  than repeated parsing.
- **Immutable view or frozen node classes** (rejected in `ADR-share-one-read-only-parsed-tree-per-python-file`): would
  enforce read-only access, but `ast` nodes are mutable stdlib classes; a proxy layer costs on every attribute access
  and breaks `isinstance` checks the rules rely on.
- **Keep per-rule parsing** (rejected in `ADR-share-one-read-only-parsed-tree-per-python-file`): no risk, no saving.
- **Per-run node index by type in `WorkspaceCache`** (selected): `WorkspaceCache.get_python_nodes(path, *types)` builds
  an index mapping node types to tuples of nodes lazily on first request. Costs about 9 MB RSS across 826 files and
  cuts repeated walks to under 2 ms.
- **Full syntax-tree and scope graph** (rejected in `ADR-index-python-ast-nodes-by-type-in-workspacecache`): index
  records lexical scopes, enclosing functions, and conditional blocks. Complex to maintain, higher memory footprint,
  and unneeded for most rules.
- **Keep per-rule `ast.walk`** (rejected in `ADR-index-python-ast-nodes-by-type-in-workspacecache`): no changes, but
  retains about 0.5 s of redundant traversals in every whole-workspace run.

### Path resolution

- **Lazy resolution in `_relative` and a per-run key memo in `WorkspaceCache`** (selected): resolve only when needed
  and only once per path argument between invalidations.
- **Lexical keys** (`os.path.normpath` instead of `resolve`) (rejected in `ADR-resolve-rule-paths-once-per-run`):
  cheapest, but a symlink and its target would get different keys, so a write through one name would not invalidate
  the other; rejected by driver 1.
- **Keep resolving on every call** (rejected in `ADR-resolve-rule-paths-once-per-run`): no risk, no saving.

### Shared DocumentIndex

- **Shared index in `WorkspaceCache` and deferred catalog in `markdown_link`** (selected): `WorkspaceCache` provides a
  run-scoped computed cache helper (`get_or_compute`), which `document_index(ctx)` uses to build and reuse
  `DocumentIndex` once per `RuleContext`. `markdown_link` defers calling `ctx.cache.get_catalog(root)` until a broken
  relative link is encountered.
- **Stat-based file skipping in parse memo** (rejected in
  `ADR-share-document-index-and-defer-catalog-build-in-rules-run`): skip reading and hashing files whose mtime/size
  have not changed since the memo write. Violates the correctness-by-construction driver of
  `ADR-document-system` due to clock skew and filesystem granularity risks.
- **Keep independent rule loads** (rejected in `ADR-share-document-index-and-defer-catalog-build-in-rules-run`): zero
  architectural changes, but retains over 300 ms of repeated index loads and whole-workspace catalog scans on every
  targeted workflow run.

### Python facts

- **Keep shared ASTs only** (rejected in `ADR-pull-per-file-python-facts`): lowest complexity, no extraction reuse
  across processes.
- **Add an evaluator lifecycle hook** (rejected in `ADR-pull-per-file-python-facts`): central scheduling, but the
  engine must learn rule-specific file sets and context.
- **Pull rule-owned facts from WorkspaceCache** (selected): preserves rule composition, requires explicit schemas and
  dependencies.
- **JSON per rule with atomic replace** (selected): simple safe decoding and independent invalidation; concurrent
  writers may lose hits.
- **Per-entry files** (rejected in `ADR-persist-python-facts-and-reuse-in-snapshots`): isolate writes but create many
  small filesystem operations.
- **Pickle or persisted ASTs** (rejected in `ADR-persist-python-facts-and-reuse-in-snapshots`): avoid record design
  but permit executable loading or couple storage to AST internals.
- **No snapshot sharing** (rejected in `ADR-persist-python-facts-and-reuse-in-snapshots`): simpler authority boundary
  but temporary snapshots always miss host facts.

---

## 4. Decision Outcome

Chosen: parse cached bytes once into one shared, read-only tree and node index per file; resolve each path once per
run; share one `DocumentIndex` per run and build the Markdown catalog only on demand; pull rule-owned Python facts
through `WorkspaceCache` and persist them per rule with read-only snapshot reuse.

### Python parse and AST

- `WorkspaceCache.get_python_ast(path) -> ast.Module` parses `read_bytes(path)` with
  `ast.parse(data, filename=<name>)`, where `<name>` is the resolved path relative to the workspace root in POSIX form
  (the resolved absolute path for a file outside it), and caches the tree under the cache's resolved-path key. Bytes
  follow CPython's reading of source files (driver 2). (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- A `SyntaxError` or `ValueError` from the parse is memoized under the same key without its traceback, and every later
  call raises a fresh, equal exception (same type and arguments), so no rule's frames stay referenced; a missing file
  raises `FileNotFoundError` like `read_bytes` and is not memoized. (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- Each rule keeps its current handling of an unparsable file (`architecture` reports, `usecase-boundaries` aborts,
  `unique_code` and the catalog rules skip), so there is no central syntax-error report: a run already reports syntax
  errors through the language linters, and a central report would change rule output (drivers 1 and 3).
  (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- `invalidate` (and so `write_text` and `invalidate_many`) and `invalidate_all` drop the tree or error with the file's
  other derived data. (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- Rules call `ctx.cache.get_python_ast` directly; there is no `getattr` probe or fallback parse (driver 4). An engine
  without the method fails the rule as a rule execution error. (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- `inspect_architecture` and `inspect_usecases` take a keyword `cache` that defaults to a fresh
  `WorkspaceCache(root)`, and the rules pass `ctx.cache`; both keep enumerating their declared package roots, so only
  the parse moves (driver 5). (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
- Every caller receives the same cached tree, read-only by contract. It is the only option that keeps the saving
  (drivers 2 and 1): the prototype run shared 490 trees across the three rules, produced byte-identical output and
  left all 490 trees equal to a fresh parse (`ast.dump(..., include_attributes=True)`).
  (ADR-share-one-read-only-parsed-tree-per-python-file)
- No current rule mutates a node: the source review found no attribute assignment, `setattr`, `NodeTransformer` or
  node-list mutation; per-module state lives on the rules' own dataclasses.
  (ADR-share-one-read-only-parsed-tree-per-python-file)
- `CAP-GOV-rule-authoring` states the contract: a tree from the cache is shared for the run and is never modified; a
  rule that needs a changed tree parses its own copy (driver 3). (ADR-share-one-read-only-parsed-tree-per-python-file)
- `WorkspaceCache.get_python_nodes(path, *types: type[ast.AST]) -> tuple[ast.AST, ...]` returns nodes matching any
  requested type in document traversal order (driver 4). (ADR-index-python-ast-nodes-by-type-in-workspacecache)
- The node index is built on the first node query for `path` from `get_python_ast(path)` and retained under the same
  invalidation cycle as the parsed AST. (ADR-index-python-ast-nodes-by-type-in-workspacecache)
- Rules querying flat node types (`architecture`, `usecase-boundaries`, `command_boundary`, `library_output`, and
  module-level `unique_code`) read through `get_python_nodes`; specialized scoped walks (`unique_code._calls` and
  `layers._imports`) remain rule-internal, optionally short-circuiting when target nodes are absent (driver 1).
  (ADR-index-python-ast-nodes-by-type-in-workspacecache)
- Returned tuples contain the shared AST node instances; callers must not modify them.
  (ADR-index-python-ast-nodes-by-type-in-workspacecache)

### Path resolution

- `RuleContext._relative` tries the lexically normalized path first and calls `resolve()` only when that path is
  outside the workspace root. The candidates and their order are unchanged, so it returns the same value for every
  input whose resolution succeeds; only the second, unused resolution disappears (driver 1).
  (ADR-resolve-rule-paths-once-per-run)
- An in-workspace symlink loop, whose `resolve()` raises `RuntimeError` on Python 3.12, gets its lexical name instead
  of failing the rule; a loop named as a CLI target still fails, because target expansion resolves it first.
  (ADR-resolve-rule-paths-once-per-run)
- `WorkspaceCache` memoizes the resolved path of each path argument; `_key` and `read_bytes` use the memo, so a path
  resolves once per run until an invalidation. `invalidate` (and so `write_text` and `invalidate_many`) and
  `invalidate_all` clear the whole memo, as `invalidate` already clears every file listing (driver 2).
  (ADR-resolve-rule-paths-once-per-run)
- `write_text` resolves its path afresh, without the memo, for the workspace-containment check, the pinned-directory
  check and the write destination (driver 3); writes are rare, so this costs nothing measurable.
  (ADR-resolve-rule-paths-once-per-run)
- The prototype (`docs/materials/2026-10/20261022-rule-shared-python-ast/measurements.md` §3, path resolution only)
  cut the median from 4.29 s to 3.87 s with byte-identical output, and to 3.23 s together with the shared parse.
  (ADR-resolve-rule-paths-once-per-run)

### Shared DocumentIndex

- `WorkspaceCache` has a generic per-run cache helper (`get_or_compute(key: str, factory: Callable[[], T]) -> T`),
  purged on `invalidate_all()` and file writes. (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
- `document_index(ctx)` retrieves or computes `DocumentIndex` via
  `ctx.cache.get_or_compute("spec.document_index", ...)`, ensuring exactly one build per `RuleContext`.
  (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
- When `ctx.cache.write_text` modifies a Markdown file, `spec.document_index` and `_catalog` are invalidated so
  convergence rechecks see updated content. (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
- `MarkdownLinkRule._broken_links` retrieves `ctx.cache.get_catalog(root)` lazily only when an invalid local target
  requires a repair candidate. (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
- Rules receiving the shared `DocumentIndex` do not modify it or its parsed documents (the risk accepted in
  Consequences). (ADR-share-document-index-and-defer-catalog-build-in-rules-run) → `CAP-GOV-rule-authoring` §2
  (MUST NOT)

### Python facts

- The pull descriptor in `docs/materials/2026-10/20261022-persistent-python-facts-cache/design.md` is chosen: the
  rule supplies a typed extractor/codec, schema version and source dependencies; `WorkspaceCache` owns identity and
  retention. (ADR-pull-per-file-python-facts)
- The key uses logical relative path, exact cached Python bytes, explicit canonical extraction context and a
  source-derived fingerprint. The fingerprint hashes the read/AST/codec framework path, actual extractor/helper
  sources and Python runtime; unreadable dependencies disable persistence. (ADR-pull-per-file-python-facts)
- Extractors produce immutable rule-owned syntax/scope records, never AST objects or resolved cross-file judgments.
  Configuration/settings resolution stays in judgment for the three migrated rules. (ADR-pull-per-file-python-facts)
- Shared ASTs remain read-only and nodes retain their existing order. Extraction preserves source positions, scope and
  declaration ordering. (ADR-pull-per-file-python-facts)
- Invalidation drops affected extracted facts and cross-file computed state; fresh byte/context validation guards
  later reuse. Extractor failures retain their existing behavior and are not saved as successful facts.
  (ADR-pull-per-file-python-facts)
- Facts persist as per-rule JSON memos with atomic working-tree updates and read-only snapshot borrowing, as detailed
  in `docs/materials/2026-10/20261022-persistent-python-facts-cache/design.md`, at
  `.devkit/transient/rules/facts/<rule-id>.json` under an existing safe transient directory.
  (ADR-persist-python-facts-and-reuse-in-snapshots)
- Reuse validates format, fingerprint, entry identity and rule codec. Symlink components and escaped or non-regular
  memo paths are rejected; obstructing files are never removed. Validated rule IDs determine safe filenames.
  (ADR-persist-python-facts-and-reuse-in-snapshots)
- Only explicitly enabled working-tree evaluations write, after fixes/rechecks; dry runs, library defaults and all
  snapshot paths are read-only. This is a Python-facts policy difference from
  `ADR-document-system`, which remains unchanged for documents.
  (ADR-persist-python-facts-and-reuse-in-snapshots)
- Full successful rule enumeration may prune; partial runs retain unseen paths. Writes use lock-free atomic
  replacement; failures log only and unchanged payloads do not rewrite. Cache I/O/validation errors are misses;
  extractor programming failures retain the existing evaluator failure semantics.
  (ADR-persist-python-facts-and-reuse-in-snapshots)
- A snapshot keeps its evaluation workspace root. The project use case injects only the originating worktree's
  storage root in read-only mode. Reuse matches snapshot source bytes and actual executing rule/helper fingerprints,
  after existing receipt checks, including in-place staged execution. A miss extracts from the snapshot and writes no
  memo anywhere. (ADR-persist-python-facts-and-reuse-in-snapshots)
- No cross-worktree cache is introduced. Deletion, rename and policy changes rebuild discovery and global judgment.
  (ADR-persist-python-facts-and-reuse-in-snapshots)

---

## 5. Consequences

- **Positive**:
  - Valid source parses once per run for every migrated rule, and an unparsable file is also parsed once.
    (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
  - One parse per file and run for every migrated rule; fewer AST allocations also cut cyclic GC time (0.49 s to
    0.15 s in the prototype). (ADR-share-one-read-only-parsed-tree-per-python-file)
  - Removes repeated `ast.walk` traversals, saving about 0.5 s on whole-workspace runs; rules querying multiple node
    kinds (e.g. `Import` and `ImportFrom`) can retrieve them in one query.
    (ADR-index-python-ast-nodes-by-type-in-workspacecache)
  - About 0.4 s less per whole-workspace run; `_relative` no longer touches the file system for paths inside the
    workspace. (ADR-resolve-rule-paths-once-per-run)
  - Cuts `DocumentIndex.load` invocations from up to 7 down to 1 per rules run, saving ~300 ms on targeted runs like
    `workflow next`; eliminates whole-workspace directory walks and basename catalog builds in `markdown_link` when
    all links in target files exist; preserves unidirectional layering: `devkit-agt` remains unaware of
    `DocumentIndex`. (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
  - Warm runs skip extraction; discovery, source reads/hashes and global judgments still run.
    (ADR-pull-per-file-python-facts)
  - Cache deletion, concurrent lost updates and schema mismatches cost extraction, without a new user action.
    (ADR-persist-python-facts-and-reuse-in-snapshots)
- **Negative / Risks**:
  - Accepted by the user: on source the repository does not contain (0 of 822 files), results change: a file with a
    UTF-8 BOM now parses in every rule; a PEP 263 coding cookie (`# coding: latin-1`) is honoured; a file with
    invalid UTF-8 is skipped by `unique_code` and the catalog rules instead of being analysed as replaced text;
    `architecture` reports a decode failure with the `SyntaxError` wording; and the `usecase-boundaries` abort message
    names the file instead of `<unknown>`. (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
  - A rule enumerating a symlinked path inside the workspace sees the resolved name in a syntax-error message.
    (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
  - A future rule that mutates a shared tree silently changes the input of every later rule in that run.
    (ADR-share-one-read-only-parsed-tree-per-python-file)
  - Accepted: trees stay alive for the rest of the run instead of one rule. Retained memory is about 40 times the
    parsed source (all 822 trees of this repository: +221 MB for 5.1 MB of source). Peak RSS is unchanged here
    because the devkit-dev rules already hold all their trees at once, but a project whose selected rules streamed
    before (the catalog `cli_tool` rules without devkit-dev) now holds every parsed tree; trigger to revisit: a
    project reports memory pressure in `devkit rules check`. (ADR-share-one-read-only-parsed-tree-per-python-file)
  - The node index adds about 9 MB of retained memory across 826 files during a full run; accepted: callers must
    observe the read-only contract for nodes returned by the accessor.
    (ADR-index-python-ast-nodes-by-type-in-workspacecache)
  - A symlink created, removed or retargeted outside the cache during a run, with no invalidation, keeps the key it
    resolved to first, so a read returns the old target's cached data where a fresh resolution would follow the new
    target. Writes are unaffected, because `write_text` resolves afresh. (ADR-resolve-rule-paths-once-per-run)
  - The cached `DocumentIndex` instance remains in memory for the duration of the `RuleContext` (negligible RSS
    impact, < 5 MB); accepted: rules receiving `DocumentIndex` must treat it and its parsed documents as strictly
    read-only. (ADR-share-document-index-and-defer-catalog-build-in-rules-run)
  - Advisory and usecase consumers require explicit scope/expression records and equivalence coverage, adding more
    refactoring than the synthetic benchmark assumes. Development remains medium with cross-component reviews.
    (ADR-pull-per-file-python-facts)
  - Dependency completeness and facts immutability are reviewable contracts, not runtime sandbox guarantees.
    (ADR-pull-per-file-python-facts)
  - No BaseRule requirement, new CLI flag, automatic import dependency walker or persistent final violation cache.
    (ADR-pull-per-file-python-facts)
  - Working-tree checks gain ignored transient writes; this behavior must be documented in governance contracts.
    (ADR-persist-python-facts-and-reuse-in-snapshots)
  - JSON schema validation provides safe loading, not authenticity of malicious well-shaped local edits. The memo is
    trusted local derived state, matching the document memo model; adversarial cache authentication is excluded.
    (ADR-persist-python-facts-and-reuse-in-snapshots)
  - Complete-process performance remains unverified until Development measures real records and snapshot overhead.
    (ADR-persist-python-facts-and-reuse-in-snapshots)
- **Follow-ups**:
  - None for the shared parse; a project installing mismatched devkit-catalog and devkit-agt versions sees a rule
    execution error until it upgrades devkit-agt. (ADR-parse-cached-bytes-once-and-memoize-the-outcome)
  - If a mutating rule is ever needed, it parses its own tree; revisit enforcement only when a mutation defect is
    observed. (ADR-share-one-read-only-parsed-tree-per-python-file)
  - None for path resolution. (ADR-resolve-rule-paths-once-per-run)

---

## 6. Confirmation

- `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`:
  - `get_python_ast`: same object on repeated calls; a fresh parse after `invalidate`, `write_text` and
    `invalidate_all`; an unparsable file raises an equal `SyntaxError` with the workspace-relative name from a
    distinct exception object on every call while parsing once; a missing file raises `FileNotFoundError`; a BOM file
    parses.
  - `get_python_nodes` returns nodes in document order matching direct AST traversals, and invalidation drops the
    index.
  - A path argument resolves once across repeated `read_bytes`, `read_text` and `get_python_ast` calls; after
    `invalidate`, `write_text` and `invalidate_all` a retargeted symlink yields its new key; a symlink and its target
    share one key; after a path is read, replacing its parent directory with a symlink to outside the workspace makes
    `write_text` raise `UnsafePathError` (`PATH_UNSAFE`).
- `packages/devkit/tests/integration/features/rules/engine/test_context.py`: its existing symlink and
  outside-workspace tests pass unchanged; a lexically inside path is made relative without calling `Path.resolve`; an
  absolute path through a symlinked alias of the workspace root maps to its relative form; a path through an
  in-workspace symlink to outside keeps its lexical name, and the same path through the root alias returns `None`;
  `toout/../docs/a.md` (with `toout` such a symlink) stays `docs/a.md`; an in-workspace symlink loop gets its lexical
  name.
- Each migrated rule's tests build `RuleContext(workspace_root=root, cache=WorkspaceCache(root))`, call
  `rule.check(ctx)` and assert that `ctx.cache.get_python_ast(p)` equals a fresh parse (`ast.dump` with attributes)
  for the files it scanned; the documented `testing` harness API stays unchanged. The migrated rules' existing tests
  pass unchanged, apart from expectations that name `<unknown>`. Rule unit and integration tests verify byte-identical
  output across this repository before and after the node-index migration.
- Unit tests in `packages/devkit/tests/unit/` and `packages/devkit-spec/tests/unit/` verify that `get_or_compute`
  caches results and invalidates properly on `write_text`; integration tests verify that `markdown_link` passes
  without building `DocumentCatalog` when no links are broken.
- `devkit rules check --format json` on this repository prints the same bytes as before; rule evaluation output on
  this repository remains identical before and after the shared `DocumentIndex`.
- Python facts: proposal AC1–AC3 and AC6 compare full judgments, source encodings, cross-file edits and invalidation
  against disabled execution. Unit tests assert each descriptor's expected source dependency set and changes to
  helpers invalidate it. Rule tests assert warm extraction makes no AST/node acquisition calls. Review matches every
  prior AST-consuming branch to a typed fact operation before migration is declared complete.
- Python facts storage: proposal AC4–AC5 exercise corruption, schema/fingerprint changes, path containment, symlinks,
  concurrent writers, partial/full pruning, no-op writes and materialized/in-place snapshots with divergent unstaged
  code and source. AC7 reports fresh-process disabled/cold/warm timings; synthetic JSON decoding is not completion
  evidence.
- Review: no migrated rule calls `ast.parse` on a whole file or reads Python source outside `ctx.cache`;
  `CAP-GOV-rule-authoring` names the read-only contract.
