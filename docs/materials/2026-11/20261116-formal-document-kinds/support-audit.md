# Formal document-kind support audit

## Inspection boundary

This audit records source inspection on main commit 534ad541e9d1e87beffa6bbc4f1afa95c71f6106 for the corrected
Backlog direction. It is not implementation verification. No passing runtime/test claim follows from a generic
code path. Planning must turn these findings into a complete per-kind support and verification matrix.

Paths below are workspace-relative; line numbers identify the inspected source. Existing ID-bearing contracts
are cited by full ID. Proposed prefixes DESIGN, DOMAIN and OPS remain spelling decisions for Planning; formal
prefix identity itself is required.

## Model, governance and published interfaces

| Source location | Inspected behavior | Required Planning treatment |
| --- | --- | --- |
| packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py:25,64,303 | Kind enum and explicit KindDefinition rows; enum-order/unique-prefix/relation-field coverage validation | Add all three kinds and complete per-kind facts; verify coverage |
| packages/devkit-docs/src/devkit_docs/features/documents/models/ids.py:30 | Prefix regex derives from definitions | Exercise new prefixes and invalid controls; generic code may suffice |
| packages/devkit-docs/src/devkit_docs/features/documents/models/parse.py:47,61 | Unknown prefix cannot become a document node | Verify formal node parsing and metadata errors for each kind |
| packages/devkit-docs/src/devkit_docs/features/documents/models/model.py:12 | Hardcoded list/scalar/provenance fields; Document serialization uses kind strings | Define relation applicability, distinguish aliases/current/provenance, preserve Python/JSON contracts |
| packages/devkit-docs/src/devkit_docs/features/documents/repositories/index.py:68 | Generic indexed documents/aliases and reference machinery | Verify all three nodes, aliases and incoming/outgoing references |
| packages/devkit-docs/src/devkit_docs/features/governance/usecases/id_convention.py:301 | Living Spec grammars explicitly enumerate capability/usecase/UX/architecture | Register exact path/H1/stem grammar for each formal role and namespace |
| packages/devkit-docs/src/devkit_docs/features/governance/usecases/spec_format.py:78,106,189 | Required id/title/status, path-derived ID and table-driven format scope | Define appropriate metadata/status and verify positive/negative scope/fixes |
| packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_summary.py | Summary coverage derives from kind definitions | Verify all formal documents require the selected summary contract |
| packages/devkit-docs/src/devkit_docs/features/governance/services/entrypoint_paths.py:31 | Entrypoint directories derive from row.entrypoints | Define role-specific applicability; update misleading CAP/UC-only descriptions where needed |
| packages/devkit-docs/src/devkit_docs/features/documents/repositories/config.py:72 | Namespace config validates name/path, with no kind allowlist | Verify global, selected package and all-namespace behavior rather than inventing a config schema |
| packages/devkit-docs/src/devkit_docs/features/documents/cli/commands.py:192,241 | Kind choices dynamic, help enumerates kinds manually | Keep help, choice handling, list/filter and machine output consistent |
| packages/devkit-docs/src/devkit_docs/features/documents/cli/search.py:41 | Search kind choices derive from Kind | Verify supported search modes, exact-ID pinning and filters with new nodes |
| packages/devkit-docs/src/devkit_docs/features/documents/usecases/browse.py | List/order/resolve/refs use generic model paths | Verify each existing supported operation and negative result, not just index loading |
| packages/devkit-docs/pyproject.toml:17-34 | Published bundles, commands, config-template and context-document entrypoints; no docs MCP service | Verify parity of these surfaces; do not invent a new document MCP server |

Core ownership is `packages/devkit-docs` and the existing current owner documents. Planning may authorize required
runtime/CLI boundary integration with a declared cross-package owner and feature dependency. Existing contract
outputs follow `ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol` and `CAP-CLI-agent-cli-toolkit`.

## Authoring and consumer distribution

| Source location | Inspected behavior | Required Planning treatment |
| --- | --- | --- |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md | Explicitly requires ID-free designs/domain and denies domain index standing | Replace those clauses with formal kind authoring and reference contracts |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/architecture-writing.md | Architecture scope and adjacent responsibilities | Keep structure/constraint ownership distinct from mechanisms/domain/operations |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/design-template.md | Optional ID-free template | Formal design template plus formal domain/operations templates and per-kind writing instructions |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml:8-53,124-155 | Instructions are registered separately; templates ship as one directory asset; core selection explicit | Register/select all writing instructions and verify shipped templates |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/AGENTS.md:12 | Template pointer omits design/domain/operations | Update source pointers consistently with installed guidance |
| packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/README.md; docs/README.md | Seed and current hierarchy maps | Explain formal homes and routing without assigning SDD lifecycle to neutral docs assets |
| packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py:47,49,83 | Exact instruction/template inventories and ID-free template assertion | Update meaningful inventories/assertions for formal contracts |
| packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py:32,43,67 | Built-wheel docs-only consumer excludes spec distribution, expects eight instructions and adaptive-dev neutrality | Verify complete changed inventory, sync/get-context and package independence |

## Required lifecycle and viewer owners

These are mandatory milestone phases; they are not optional gap-only follow-ups.

| Owner and source location | Inspected integration point | Required evidence |
| --- | --- | --- |
| Lifecycle: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/{spec-plan,spec-sync,spec-entrypoints}/ | Planning, reconciliation and entrypoint guidance | All three kinds as affected formal impact targets, appropriate entrypoint policy |
| Lifecycle: packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py:391-418 | Target-docs scaffold has capability/usecase/architecture/governance sections | Formal role and migration planning sections with scaffold tests |
| Lifecycle: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja:22,72; brownfield-adoption and sdd-baseline playbooks | Lifecycle pointers and baseline/adoption coverage | Complete SDD integration and source/distribution regression |
| Lifecycle: packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle/skills/adaptive-dev/references/documents.md and roles/documenter.md | Adaptive document routing and maintenance | Formal roles without forced SDD Units/records/gates, integration tests |
| Viewer: packages/devkit-viewer/frontend/src/lib/api/documents.ts:240,276-297 | Prose ID prefix regex and book group whitelist are explicit | All three kinds in reference links, groups/order and namespace navigation |
| Viewer: packages/devkit-viewer/frontend/src/lib/features/document/supersession.ts:27 | Statement ID regex explicit | Formal prefixes recognized in applicable supersession statements |
| Viewer: packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte:290 | Related-document fields limited to related_capabilities/usecases | Display core-supported per-kind relations and applicable metadata/reference graph |
| Viewer backend and frontend public/static output | Generic backend loading is not complete frontend proof | Rendering/deep links/artifact/empty/missing states plus library/static/package tests |
| Viewer-owned scripts/handbook.py:48,56,220 | Kind and ID maps recognize limited prefixes; lookup skips unknown kinds | Recognize formal source IDs; document deliberate inclusion policy; focused script regression |
| tools/devkit-dev/tests/integration/test_handbook_script.py | Existing handbook script tests | Extend existing tier under viewer proposal rather than inventing another tier |

The milestone/proposal/feedback dashboard is purpose-specific; it is not evidence of universal kind navigation.
Viewer completion requires frontend lint/check/test/pack/build and generated-asset checks plus public package proof.
Draft/review screens before implementing changed interactions. Shared existing rendering is valid with complete
new-kind verification; a separate custom editor per kind is not required.

## Migration and decision ledger

- Current main canonical design: `docs/designs/distribution-transactions.md` and its
  `distribution-transactions/file-directory-replacement.md` detail. Current main canonical domain:
  `docs/domain/delivery-relationships.md` and `docs/domain/bundle-selection-and-installation.md`.
  All are ID-free. Inventory full global/namespace role directories before handoff and migrate every canonical
  current role document, with a coherent independent-detail versus supporting-artifact identity policy.
- Ingress includes `CAP-DIST-sync-and-transactions` lines 114/370, `CAP-DLV-proposal-lifecycle` line 43 and
  `docs/steering/glossary.md` lines 16/48. Repair ID ingress and relative support links with migration.
- `ADR-documentation-ownership-and-linked-design-entries` §4 and `ADR-linked-domain-relationship-views` §4
  select ID-free standing and deny new identity/runtime support. A new ADR must supersede these clauses and
  current contract restatements. Retain unique owners, clear architecture boundaries and existing guarantees.
- Operations source exists only in halted worktree commit 55bc46fb5ce350e0a84666d6df338f8947e54e1b.
  [Archive provenance](README.md) identifies exact originals and old-direction verification limits. The operations
  composition can seed a formal current document; its negative index tests cannot prove corrected support.
- Archived pilot evidence remains historical. Do not mass-convert historical materials or completed records into
  current formal role documents, and do not treat preservation as retaining an ID-free canonical alternative.

## Planning verification deliverable

Create a three-kind-by-surface matrix with applicability, implementation owner, changed/reused mechanism and
verification result. Include valid/invalid metadata/path/prefix/H1/alias/reference controls; list/filter/search,
exact-ID pinning/resolve/incoming/outgoing refs; global and registered namespace selection; templates/instructions,
source delivery and docs-only wheel; all migrations and maintenance; lifecycle and viewer owner evidence;
existing-kind and public compatibility regressions. No cell is satisfied solely by an existing owner link or an
untested generic implementation. Complete support is the acceptance criterion; code size is not.
