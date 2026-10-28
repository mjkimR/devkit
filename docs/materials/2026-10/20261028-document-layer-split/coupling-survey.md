# Document layer and SDD lifecycle coupling survey

A read-only survey of what splitting devkit-spec's document layer from the SDD delivery process would take. A Scout
run and a Host spot check on base `e3e03483` produced it; no test, rule or devkit command was run for it. Locations
name files and symbols; line numbers drift and are left out.

## Summary

The split is feasible but spans several units. The document model is mostly self-contained, and process features
already depend on it one way. The coupling sits in about twenty seams: the shared `[tool.spec]` config reader, the
`DocumentIndex` history rule, the shared `base/errors.py`, `base/units.py` and `base/axes.py` modules, the
entrypoints bridge, a few mixed rules and the spec bundle, which mixes both sides in its `core` preset.

Neither devkit-agt, devkit-dist, devkit-viewer nor tools/devkit-dev imports devkit_spec. The viewer hard-codes
document layout and kind prefixes, so a layout or kind change needs mirroring there, but the split itself does not
touch its imports.

## Couplings from the document side to the lifecycle

All paths are under `packages/devkit-spec/src/devkit_spec/`.

| Location | Coupling | Suggested resolution |
| --- | --- | --- |
| `features/documents/repositories/index.py` (`DocumentIndex` load, `is_historical`) | Files of a `completed` spec bundle and `done`/`dropped` milestones are historical; knows the bundle layout | Lifecycle injects a history predicate |
| `features/documents/usecases/browse.py` | Imports `policy.repositories.branches.planning_branches` (shows a draft as reviewing when `plan-<slug>` exists) and `policy.services.config`; task counts through devkit_agt; proposal and feedback display fields | Lifecycle display-field providers; namespace reader moves to the document side |
| `features/documents/cli/commands.py`, `cli/search.py` | Use private browse helpers for proposal, planning, feedback and status columns; help text names lifecycle statuses | Split list display; the lifecycle CLI adds its columns |
| `features/documents/models/kinds.py` | The `Kind` enum holds PROPOSAL, PROPOSAL_DECISION, SPEC, PLAN, TASKS, RECONCILE and FEEDBACK; terminal statuses and anchor files per kind | Keep the vocabulary in one table (`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`) or move lifecycle kinds out |
| `features/documents/models/model.py`, `models/parse.py` | `is_unit_anchor` hard-codes `spec.md`/`proposal.md`; parse applies unit-only fields (`decomposed_from`, `supersedes`, `depends_on`) | Injected unit-anchor predicate |
| `features/documents/services/dependencies.py` | Hard-codes PROP/SPEC anchors; a completed SPEC is terminal | Keep the structural graph; inject the live predicate |
| `features/documents/services/namespaces.py` | Imports `Namespace` and constants from `policy/services/config.py`; `_bundle_anchor` encodes the `specs/` and `docs/proposals/` layout | Move `Namespace` and its reader; inject the layout resolver |
| `features/policy/services/config.py` | One `[tool.spec]` reader mixes namespaces (document) with worktree, depth, scope and feedback keys, and rejects unknown keys | Decide table ownership |
| `base/errors.py`, `base/units.py`, `base/axes.py` | Document and lifecycle error classes, unit constants (`SKELETON_MARKER`, `is_spec_dir`) and efforts/task kinds share modules | Move each to its owner; keep the documented `SPEC_` codes |
| `features/governance/services/documents.py` | `is_proposal_anchor` encodes the proposal layout and is shared by document and lifecycle rules | Decide placement |
| `features/governance/usecases/document_reference.py` | Handoff semantics: a handed-off PROP reference resolves to its SPEC; PROP/SPEC slug collision | Split the handoff part to the lifecycle |
| `features/governance/usecases/spec_format.py` | Milestone status values, proposal effort hints, namespace on unit anchors | Split the rule |
| `features/governance/usecases/id_convention.py` | SPEC/PLAN/TASKS/REC and feedback path grammars; imports `trailing_comment` from `spec_lifecycle` | Move the lifecycle grammars; move the helper to a neutral module |
| `features/governance/usecases/document_summary.py` | Uses `SKELETON_MARKER` | Neutral constant |
| `features/entrypoints/` | `usecases/derive.py` and `repositories/bundle.py` read spec status, task boundaries and reconcile targets; `services/paths.py` and apply write document frontmatter | derive and bundle to the lifecycle; paths and apply to the document side |

Lifecycle-only rules move as units: `spec_lifecycle`, `spec_progress`, `task_coverage`, `reconcile_contract`,
`proposal_boundaries` and the rejected-proposal hygiene.

## Process-to-document edges (already one-way)

`proposals/services/history.py`, `proposals/services/rewrite.py`, `proposals/usecases/handoff.py`, `scope/services/`
and `worker/usecases/inputs.py` import the document model or entrypoints parsers. `policy/repositories/branches.py`
imports devkit_agt worktree markers and stays on the lifecycle side.

## CLI and entry points

- Document commands: `devkit spec resolve`, `refs`, `list`, `search`. Mixed: `entrypoints` (derive is lifecycle,
  `--apply` writes documents).
- Lifecycle commands: `new`, `proposal ...`, `policy`, `scope`, `worker inspect`.
- `packages/devkit-spec/pyproject.toml` entry points: `devkit.bundles` (split into two bundles or presets),
  `devkit.commands` (the group composes both sides), `devkit.post_finish`, `devkit.integration.readiness`,
  `devkit.attach_check` and `devkit.hygiene` (lifecycle), `devkit.config_template` (split: namespaces versus
  lifecycle keys).

## Proposed boundary

- **Document package**: `features/documents` without the lifecycle fields and history rule, the document rules
  (with the mixed rules split), entrypoints paths and apply, the namespace reader, document error classes, and
  `resolve`/`refs`/`list`/`search`. It depends on devkit-core, devkit-agt (rules, scanner) and devkit-dist (search,
  CLI adapters), and not on policy.
- **Process package** (devkit-spec): proposals, delivery, scope, worker, the lifecycle part of policy, lifecycle
  rules and hygiene, entrypoints derive and bundle, lifecycle units/axes/errors, the CLI composition and the
  lifecycle bundle assets. It depends on the document package.
- Edges to remove: documents to policy (`browse.py`, `namespaces.py`), governance to policy, and `id_convention`
  to `spec_lifecycle`.

## Open decisions

1. A new wheel, or a second regular package in devkit-spec's wheel; the version policy of a new wheel.
2. One `devkit spec` group for both sides or a separate document group.
3. Whether lifecycle kinds stay in the shared kind table.
4. Whether milestones are document or lifecycle vocabulary.
5. The history rule: an injected predicate (no memo impact) or a document-side completed-bundle rule.
6. `[tool.spec]` ownership: split the reader, or a document-owned table (affects `ADR-spec-package-on-devkit`).
7. Two bundles or one bundle with two presets; the `auto_select` default and the owner of `docs-skeleton`.
8. Error code prefixes: keep `SPEC_` or rename.
9. Whether the scanner the document model borrows from devkit-agt moves to devkit-core.

## Affected records

- Capabilities: `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`, `CAP-DOCS-document-search`,
  `CAP-DOCS-namespaces`, `CAP-GOV-spec-rules`, `CAP-TRACE-code-entrypoints`, `CAP-DLV-project-policy`,
  `CAP-DLV-spec-bundles`, `CAP-DLV-delivery-workflows`, `CAP-DLV-proposal-incubation`,
  `CAP-COLL-work-scope-registry`.
- Architecture: `ARCH-05-1-containers`, `ARCH-05-2-components`, `ARCH-04-1-ecosystem-boundaries`,
  `ARCH-04-2-delivery-policy`, `ARCH-05-3-command-plugins`, `ARCH-07-deployment`; `.devkit/architecture.toml`.
- Decisions to amend or check: `ADR-spec-package-on-devkit`, `ADR-package-split-and-namespaces`,
  `ADR-kind-definition-table-keyed-on-the-declared-kind-enum`, `ADR-roadmap-and-milestones`,
  `ADR-single-release-version`.
- Scripts: `scripts/affected_tests.py`, `scripts/_lib.sh`, `scripts/release.sh` gain the new wheel.

## Size

About 7,200 lines move largely as they are (`features/documents` about 4,000; document rules and governance
services about 3,000; entrypoints paths and apply about 240). About 2,000 lines stay with the lifecycle. Tests: 25
test files import document-side modules and 47 import process modules. The survey judges the work at three to four
spec units; that is an estimate, not a measurement.

## Not verified

- No test, architecture rule or devkit command was run.
- Whether `devkit.config_template` lets two packages contribute keys to one `[tool.spec]` table.
- The constitution and most skill and subagent text; bundle assets cite document commands 53 times and lifecycle
  commands 75 times (grep counts).
- Whether `ADR-single-release-version` and `ADR-package-split-and-namespaces` agree on a new wheel's version policy.
