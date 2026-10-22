---
id: PROP-persistent-python-facts-cache
title: Persist per-file rule facts between runs
summary: "Lets Python-source rules declare a per-file facts function whose results persist between runs keyed by content digest, so a rules run parses and walks only changed files."
status: accepted
created_at: 2026-10-22
target_area: governance/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/
    - tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/
    - packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/
    - packages/devkit/tests/
    - docs/capabilities/governance/
    - docs/capabilities/advisory/
    - docs/development/reference/rules-library.md
    - docs/glossary.md
  excludes:
    - packages/devkit-spec/src/devkit_spec/features/documents/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-persistent-python-facts-cache] Persist per-file rule facts between runs

## 1. Background & Hypothesis

Repeated CLI processes discard `WorkspaceCache`'s shared Python AST and node index. The baseline in
`docs/materials/2026-10/20261022-persistent-python-facts-cache/measurements.md` identifies extraction as a candidate
cost, but does not measure an implemented persistent facts path. Its 0.84 ms number is synthetic JSON decoding,
not total lookup latency. Separately cold rule measurements can double-count AST work shared in a real evaluation;
the claimed 6.0 s to 1.8–2.0 s reduction is not established by the measured 2.5 s difference.

Hypothesis: persist rule-owned, per-file facts while rerunning file discovery, configuration and cross-file judgment.
Every finding, location, ordering, severity, fix behavior, advisory and exit code must match cache-disabled execution.
`PADR-pull-per-file-python-facts` defines the extraction boundary;
`PADR-persist-python-facts-and-reuse-in-snapshots` defines storage and snapshot reuse.

## 2. Technical Spike Results

- **Q1 — Contract and consumers**: use an opt-in pull accessor on `WorkspaceCache`, with a rule-owned extractor and
  codec descriptor. Do not add an evaluator lifecycle hook or require `BaseRule` inheritance. Migrate
  `RULE-architecture`, `RULE-advisory-unique-code` and `RULE-usecase-boundaries` in this work. Their facts must preserve
  unresolved imports, expression/scope structure and source locations; the original measurements' import/class
  summaries are insufficient for advisory inheritance and usecase callback/alias checks. The rule-owned records
  represent the syntax each existing judgment consumes; they contain no live AST nodes. See `materials/design.md`.
- **Q2 — Identity and storage**: use relative POSIX path plus digest of exact bytes read by `WorkspaceCache.read_bytes`,
  an explicit canonical extraction-context key, and a source-derived fingerprint. UTF-8 text hashing would lose
  Python coding-cookie/BOM behavior. Keep one validated JSON memo per rule. Rule module bytes and a distribution
  version alone do not cover helper modules or editable installs; dependencies must be declared and hashed.
- **Q3 — Snapshots**: the use case injects the originating worktree's memo directory as a read-only source into the
  snapshot cache, including staged in-place evaluation. Reuse requires the executing snapshot rule descriptor's
  fingerprint and the snapshot bytes, never the unstaged rule or source bytes. This is only a cache read exception;
  snapshot policy, receipt verification and rule discovery keep their existing authority.

## 3. Proposed Design & Impact

### Scope and choices

1. Add a typed descriptor and `WorkspaceCache.get_file_facts(path, descriptor, *, context_key=...)` pull API. The
   descriptor owns rule ID, schema version, source dependencies, extractor and JSON encoder/decoder. The extractor
   receives the logical relative path, explicit immutable context and the cache's shared AST/node access. It must
   not read settings, other files, environment or time. Resolve every outside dependency during judgment or include
   its canonical value in the context key. The engine does not persist judgments or final violations.
2. Persist under `.devkit/transient/rules/facts/<rule-id>.json`, only inside an existing safe transient directory.
   Working-tree checks and fixes may update this derived memo; snapshots, dry runs and library calls without an
   explicitly enabled writer are read-only. This differs intentionally from document-memo writers in
   `ADR-parse-memo-failure-and-write-policy`; it does not change that document contract. No rule output changes.
3. Retain loaded stores separately from computed judgments. `invalidate`, `invalidate_many`, `invalidate_all` and
   `write_text` must invalidate affected in-memory facts before recheck; a disk entry still needs a fresh byte digest.
   A store may flush only after successful evaluation/recheck using entries for the bytes actually consumed.
4. Migrate each rule's extraction and judgment together, preserving its existing file enumeration and ordering.
   Preserve unseen entries by default. Full untargeted working-tree evaluations can prune only after the rule
   explicitly supplies its descriptor's complete logical path set following enumeration. A normal return is not
   completion evidence; caught source/parse failures issue no completion marker. Partial runs retain unseen paths.
5. Update `CAP-GOV-rules-engine`, `CAP-GOV-rule-authoring`, `CAP-GOV-evaluation-lifecycle`,
   `CAP-ADV-agent-advisory-protocol`, the rules library reference and affected rule guides. Register per-file rule facts in
   the glossary. PADRs become ADRs at handoff; no existing ADR is rewritten by Planning.

### Development verification criteria

- **AC1 — Fresh-run equivalence**: compare enabled and disabled evaluation for all three migrated rules on fixtures
  exercising imports/re-exports, dynamic imports, relative imports, package layout, advisory inherited codes,
  imported constants, scoped lazy imports, usecase constructors/annotations/aliases and raw callbacks. Compare
  full violation values/order and CLI advisories/exit codes, including settings and exclusions changes with warm facts.
- **AC2 — Identity**: edit with restored mtime and same size, rename, delete, change branch and return, change context
  and rule/helper/framework/codec source, schema or Python version; every result equals a disabled run. BOM,
  PEP 263 source, invalid bytes and syntax errors preserve existing rule behavior. Extraction failures propagate as
  before and are never persisted as a successful empty result.
- **AC3 — Extraction reuse**: in separate processes, a fully warm run invokes none of the three migrated extractors
  and makes no AST/node requests for their fact acquisition. Editing one source re-extracts only that source for
  each consuming descriptor. Other rules may still parse it; no global zero-AST claim is made.
- **AC4 — Safe persistence**: corrupt or wrong-shaped JSON/entries, mismatched fingerprints, unsupported schema,
  unreadable sources and unwritable/non-regular/symlink memo locations fall back without changed results, new
  advisories or exit status. Test atomic concurrent writers, no steady-state write, partial-run preservation and
  bounded full-run pruning. Warm several files, abort enumeration early through a caught source error, and verify
  unseen entries survive; only an explicitly completed path set permits pruning. Invalid encoder values bypass
  persistence; extractor errors retain prior semantics.
- **AC5 — Snapshot isolation**: warm the host memo, then run materialized and in-place staged and CI snapshots with
  different unstaged source and rule/helper code. Hits require snapshot identities; misses compute from the snapshot.
  Assert the host memo and temporary snapshot memo paths are unchanged or absent. Run the existing receipt-tamper
  and snapshot-scoping tests to prove reuse did not bypass rule loading checks.
- **AC6 — Rechecks and mutation**: warm facts, apply fixes/dry-run fixes and explicit invalidations, then compare
  rechecks against disabled execution; neither facts nor cross-file judgments retain the previous bytes/context.
- **AC7 — Performance evidence**: before refactoring, record a reproducible baseline on the Development branch.
  Compare disabled, cold-store and warm-store fresh processes using identical policy/inputs and at least five timed
  samples per mode. Report median end-to-end time, extraction counts, source read/hash, fingerprint, JSON load,
  judgment, write time and memo size for a full check, one-file edit and snapshot check. Target a warm full-check
  median at least 20% below disabled execution; if unmet, revisit the design before claiming the hypothesis proved.
  Neither <1 ms total load nor 1.8–2.0 s full execution is an accepted performance claim.

### Boundaries and Non-Goals

The expanded boundaries include the actual rule owners and their co-located tests. Engine tests belong in
`packages/devkit/tests/`; rule-specific tests stay with each rule. Add only the tiers needed beneath these parents.
The governance/advisory capability owners are updated during Development, not in this Planning branch.

Scope excluded: persistent AST objects or pickle, cached final judgments, automatic import-graph dependency discovery,
stat/mtime fast paths, shared caches across worktrees, document-memo changes, new CLI flags/configuration, and
migration of other Python rules. Cache-disabled execution is an internal test/library control. No changes to
`devkit.advisory` or `devkit_cli` public runtime APIs are required.

## 4. Planning Decisions and Delivery Shape

- Recommend the pull descriptor over a lifecycle hook: current rules control their own file sets and cross-file
  composition; a hook would add scheduling and inheritance constraints without replacing that work.
- Recommend explicit source dependency declarations plus conservative framework hashing. Missing or unreadable
  fingerprint inputs disable reuse; a manual facts version alone is not sufficient.
- Recommend JSON, atomic replacement without locks, working-tree warming and read-only snapshot borrowing.
  Concurrent lost updates cost extraction only. The document memo's tagged-container codec is not reused: each rule
  defines a strict JSON-compatible schema and reconstructs its typed records.
- Development remains `medium`: all state is disposable, contracts have no external consumers, and no user-data
  migration or release is included. The three rule rewrites require independent code review and cross-component
  reconciliation review under the normal medium procedure.
- Suggested implementation order: baseline and descriptor/store; engine invalidation and writer wiring; architecture
  facts; advisory facts; usecase facts; snapshot isolation and equivalence/performance checks; Living Spec reflection.
  Handoff creates the feature spec, technical plan and independently verifiable tasks; Planning changes no production code.

## 5. Lifecycle & Retirement Criteria

Planning is ready for `plan-accept` after Scout evidence, Challenger findings and closures, proposal boundary checks,
feedback coverage and a committed worker record. Acceptance approves the two PADRs and expanded Development scope.
Development requires the separate `proposal-handoff` approval. If benchmarks do not validate the hypothesis, return
with evidence and revise the direction instead of substituting synthetic JSON timing for an implemented result.
