# Persistent Python facts: investigated design

## Alternatives

| Option | Cost and risk | Recommendation |
| --- | --- | --- |
| Keep shared in-process AST/node caches | No API change, no benefit across CLI invocations | Baseline and fallback |
| Evaluator extraction lifecycle | Engine must enumerate rule-specific inputs, settings and error paths; direct check callers need a second path | Reject for this work |
| Rule-owned pull descriptor | Each caller retains discovery and judgment; extraction schemas and dependency declarations need review | Recommended |

## Rule-owned records

A record is immutable once returned, by contract like the existing shared AST. Each descriptor defines a strict
JSON codec; dictionaries/lists are wire values, reconstructed domain records may use tuples/frozen dataclasses.
The cache and other consumers must not mutate returned records. Do not serialize arbitrary objects or ASTs.

- Architecture: preserve raw Import/ImportFrom level/module/aliases, attribute chains and locations, dynamic import
  candidates, string entrypoint candidates, and top-level facade imports/aliases. Resolve configured roots,
  namespace/module/package identity, relative imports, layout and dependency graphs against current configuration.
- Advisory unique code: preserve top-level class order/bases, constant string bindings, code assignment expressions,
  candidate calls with keyword values, nested function/class scope boundaries and scope-local imports. Keep source
  positions. Rebuild duplicate-module ownership in the existing sorted-path order, resolve inheritance, imported
  constants and per-path advisory base settings every run. An unchanged caller can change findings when a different
  file's constant changes; caller extraction must remain reusable in that case.
- Usecase boundaries: preserve declarations and bases, execute parameter/return annotation presence and expressions,
  constructor calls, ordered assignment/annotated-assignment operations, Name/Attribute/Call/Await/Subscript/string
  annotation expressions, decorators relevant to property checks, nested function/lambda/class scope boundaries,
  positional/keyword callback candidates and locations. Retain existing traversal ordering and the three assignment
  resolution passes. Rebuild module/definition indexes, binding propagation, instance resolution, exceptions and
  cross-file judgments each run. Development defines the concrete typed schema before production migration and
  verifies every existing AST-reading branch has an equivalent record operation. No fabricated AST reconstruction
  is used as a shortcut: the consumer operates on these rule-owned records.

The scope/expression records are a rule-owned intermediate representation, not a generic Python AST serialization.
Unknown syntax keeps the same ignored/unresolved behavior as the existing judgment. Test matching syntax before
removing each AST access. Existing rule tests are the minimum equivalence corpus, supplemented by cross-file edits.

## Descriptor and fingerprint

Proposed names are design-level; Development fixes signatures in its technical plan. A descriptor is generic in the
facts type and contains `rule_id`, `schema_version`, `source_dependencies`, extraction, encoding and decoding.
`get_file_facts` gets logical relative path and explicit context. Context is canonical strict JSON (string keys,
finite numbers, lists, booleans and null); unsupported context bypasses persistent reuse. Facts computation still
runs when persistence is disabled. Extractor context cannot hide callbacks or mutable workspace objects.

Default migrated extractors use raw syntax records and empty context; current settings/configuration affect judgment
only. If a future extractor needs resolved identity, its caller must include that identity in context. Extraction
can access only this file's cached AST/nodes; no access to another path, config, settings, clock or environment.

Fingerprint inputs: memo format and schema versions; descriptor implementation module and every explicitly declared
helper/codec dependency (the advisory `index.py` included); framework source modules for cached byte reads, AST/node
parsing, descriptor handling and memo codec; Python implementation and full version. Package versions may be included
but never substitute for source hashes. Hash module logical names plus source bytes, not absolute worktree paths.
A unit test names the expected dependency set for each migrated descriptor. Third-party dependencies, if extraction
uses any, need an explicit version/source identity. Missing module provenance disables persistence for that descriptor.
Fingerprint values must describe the loaded implementation, captured at module/descriptor load and retained for the
run, not freshly read from unstaged host paths while snapshot code runs.

Identity is `(relative_path, BLAKE2b(raw_bytes), canonical_context, fingerprint)`. Keep the logical enumerated name
for reporting; follow existing safe path resolution for reading. Reuse no entry when the source resolves outside
the evaluation workspace. Symlink aliases with distinct logical names do not share path-sensitive facts.
Syntax/decoding/read failures retain existing behavior and are not persisted as successful empty facts.

## Storage and lifecycle

One JSON object per rule: `version`, `fingerprint`, `entries`. Each path entry holds its byte digest, canonical context
and rule-codec payload. One current identity per path is enough; a context change can replace the old entry. Reject
invalid payloads using the rule decoder. Cache structural corruption is a miss; well-shaped malicious edits are
outside this trusted-local-derived-state model, as with the document memo. This is not authenticated execution state.

Enable persistence only under an existing `.devkit/transient/` directory. Reject symlinks at `.devkit`, transient,
rules, facts and memo components, escaped roots and non-regular memo files. Create rules/facts only on an eligible
working-tree flush. Derive a safe filename from a validated rule ID; never concatenate an unchecked caller path.

Working-tree project checks/fixes may write. Dry runs, all snapshots and default library caches cannot write.
An opt-in library writer uses the same safety checks. Flush at evaluation completion after all fixes/rechecks;
failed/incomplete rule enumeration cannot prune. Full runs replace that completed descriptor's retained path set;
partial runs keep unseen entries and update observed identities. Removed entries disappear at the next complete
rule enumeration. A rule skipped by inputs or policy changes neither writes nor prunes. Encode in deterministic
order and skip replacement if the resulting payload equals the loaded payload. An unsupported facts value stays
usable in memory but is omitted from persistent entries. Exceptions in extraction propagate normally; descriptor
programming errors must not be disguised as cache I/O failures.

Use `atomic_write_bytes`; readers see one complete object. No lock: last complete writer wins; lost entries merely
miss next time. Log storage/read/validation failures with logging, emit no notices, and preserve the evaluator's
existing result. A concurrent edit is governed by the existing WorkspaceCache read/invalidation model. Store only
identities computed from the cached bytes that produced the facts, never reread a digest after extraction.

Keep decoded memo stores loaded once per descriptor per evaluation, outside `get_or_compute` judgments which clear
on invalidation. Clear affected in-memory facts and judgments on invalidation; memo hits are still checked against
newly read bytes/context. `invalidate_all` clears in-memory extracted facts, not a disk-valid identity guarantee.
After fixes, only final consumed entries may be flushed; never retain obsolete dirty entries under a fresh digest.

## Snapshot provenance

`RunProjectRulesUseCase` owns a separate storage-root/read-only setting. `RuleContext` and `WorkspaceCache` keep their
existing evaluation root agreement. Materialized snapshots may borrow only their originating worktree's memo;
in-place staged snapshots receive the same read-only mode. Snapshot files, config and tracked rule code remain
snapshot-authoritative; receipt-verified managed fallback follows existing loading checks before cache lookup.
Fingerprints use the actual loaded extractor dependencies. Host cache bytes do not choose rule modules or file
membership. A host-cache miss computes in memory from snapshot source and creates no transient memo in the snapshot.
Git worktrees use distinct storage roots; never borrow the common Git directory or another worktree's cache.

## Evidence and incoming references

Scout examined these implementation locations:

- `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py:116,160,197,284,400` — bytes/text,
  parsing, shared nodes, computed-cache and invalidation behavior.
- `packages/devkit/src/devkit_agt/features/rules/services/evaluator.py:106,135,140` — evaluator selection and checks.
- `packages/devkit/src/devkit_agt/features/rules/usecases/project.py:224,341,355,377` — cache construction and snapshots.
- `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py:50,194,296,327,376` — context and facade imports.
- `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/rule.py:18,46,92,175,186` and
  `index.py:37,59,78,120,175` — helper dependency, scoped imports and cross-file advisory resolution.
- `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/rule.py:76,108,145,188,251,303` — expression/scopes.

Incoming-reference queries were run by Scout for `CAP-GOV-rules-engine`, `CAP-GOV-rule-authoring`,
`ADR-content-keyed-document-parse-memo`, `ADR-parse-memo-location-and-format`,
`ADR-parse-memo-failure-and-write-policy`, `ADR-share-one-read-only-parsed-tree-per-python-file`,
`ADR-index-python-ast-nodes-by-type-in-workspacecache`, and `ADR-scope-snapshot-runs-to-diff-paths-including-deletions`.
Active incoming contracts to inspect are `CAP-DLV-workflow-orchestration`, `CAP-GATE-commit-gates`,
`CAP-GOV-evaluation-lifecycle`, `CAP-GOV-rule-authoring`, `CAP-GOV-rules-engine`, `ARCH-08-2-resource-taxonomy`,
`CAP-DIST-manifest-spec`, `CAP-DLV-workflow-definitions`, `CAP-DOCS-document-model` and the document-memo ADR family.
The AST/node ADRs require shared ASTs to remain unmodified; extraction retains that constraint. The snapshot ADR
requires diff-scoped rule selection; persistence changes neither selection nor global judgment discovery.
The document memo writer policy continues unchanged; Python facts deliberately add their own writer policy.

## Measurement limits

No implemented-facts prototype or complete-process timing was produced during Planning. The source measurements
remain historical evidence, not a validated performance forecast. Development must measure actual richer records,
remaining AST consumers, file hashing, fingerprinting, decoding, judgment and flush costs. The synthetic 95.9 KB
payload excludes much of the required scope/expression representation. If the stated speed target fails, do not
claim this hypothesis proved; revise the design with the evidence.
