---
id: PROP-formal-document-kinds-target
title: Formal document kinds target blueprint
summary: "Fixes exact formal role schemas, complete existing-system support, canonical migrations and required lifecycle and viewer interfaces."
status: draft
proposal: SPEC-formal-document-kinds
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
  - file: docs/usecases/documents/UC-find-the-right-documents.md
  - file: docs/usecases/governance/UC-keep-the-living-spec-consistent.md
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/decisions/2026-11/20261116-documentation-ownership-and-linked-design-entries.md
  - file: docs/decisions/2026-11/20261116-linked-domain-relationship-views.md
  - file: docs/designs/DESIGN-distribution-transactions.md
  - file: docs/designs/DESIGN-distribution-file-directory-replacement.md
  - file: docs/domain/DOMAIN-delivery-relationships.md
  - file: docs/domain/DOMAIN-bundle-selection-and-installation.md
  - file: docs/operations/OPS-distribution-sync.md
  - file: docs/steering/glossary.md
  - file: docs/README.md
---

# [PROP-formal-document-kinds-target] Formal role document target blueprint

The [selected contract](../../../docs/materials/2026-11/20261116-formal-document-kinds/core-contract.md) is normative for Development planning of this proposal.
Current source is unchanged. Planned new IDs in this blueprint are plain text until created. All support cells
below require implementation evidence; none claims a current passing implementation or inherits old pilot tests.

## 1. Exact core source scope and architecture

Production scope is `packages/devkit-docs/`, plus the exact Living Spec targets above, deleted/replaced canonical
paths in §3, and the new handoff-promoted ADR-formal-role-document-identities at its generated dated decision path.
No other capability or architecture behavior changes are authorized by the broad nearest-existing-parent `docs/`
boundary; it permits the planned operations directory only. Archived materials and completed records remain intact.

| Existing source boundary | Concrete implementation contract |
| --- | --- |
| features/documents/models/kinds.py | Append DESIGN/domain/operations rows exactly as core-contract §1, complete coverage/unique prefix+field assertions |
| models/ids.py; models/parse.py; models/model.py | Derived prefix parsing/prose scanning; three new LIST_FIELDS and typed relation definitions; same-prefix aliases and serialization unchanged; test memo round-trip/fingerprint impact |
| repositories/index.py, config.py; services/namespaces.py, rewrite.py | Reuse index/alias/memo/global identity/selection/canonical rewriting with new-kind proof; no namespace schema changes |
| usecases/browse.py, search.py; cli/commands.py, cli/search.py | Existing operations/flags/output contracts, additive kind values; update manual help/inventory text; role status filters/history and exact pinning |
| governance/usecases/id_convention.py | Explicit flat role grammars/coverage, canonical path/prefix/H1/stem/slug, outside-root role IDs and narrow artifact-parent/ID exclusions |
| governance/usecases/spec_format.py | Required fields, strict role status vocabulary and reserved/inapplicable fields, new-kind scope and existing safe fixes |
| governance/usecases/document_summary.py, document_reference.py | Required summaries; typed list relations, aliases, current/provenance distinction, ID links/fixes |
| governance/usecases/code_entrypoints.py, services/entrypoint_paths.py | Optional DESIGN paths, liveness, snapshot deleted-path reporting and canonical role-path applicability; DOMAIN/OPS rejection is format schema |
| bundles/docs/bundle/ | Registered three instructions, three formal templates, legacy template pointer; neutral constitutions/AGENTS/seed hierarchy/guides agree |
| tests/unit/features/{documents,governance}/; tests/integration/features/{documents,governance}/ | Extend existing owned tiers and helpers; new formal-kind integration fixture may be test_formal_kinds.py in existing documents tier |
| bundle/rules/{id_convention,spec_format,document_reference,document_summary,code_entrypoints}/ | Corresponding guides, wrapper tests and deterministic codes/actions reflect formal support; no new rule tier |
| tests/integration/bundles/docs/test_distribution.py; tests/e2e/bundles/docs/test_installed_consumer.py | Exact shipped inventory, source-to-consumer selection/sync/get-context and docs-only wheel proof |
| packages/devkit-docs/README.md | Public Kind/Python/JSON/CLI schema/help/path/status/reference/authoring documentation |

Documents owns Kind/model/query; governance uses the declared documents edge. All existing exposed operations
retain BaseUseCase/adapters contracts. No new feature edge, package, layer or test tier is needed. No docs-to-spec
import is permitted. `devkit-docs` has no published docs MCP service; parity covers its real library/CLI/bundle/
context/config extension surfaces. A fabricated server is outside scope. Existing feature edges and package
isolation remain covered by architecture/lint/type and affected tests.

## 2. Living Spec authority and decision reflection

| Exact owner | Planned reflection |
| --- | --- |
| `CAP-DOCS-document-model` | Kind rows and required schema/status/path/H1; typed relations, aliases/current/provenance/supersession distinctions; public strings/JSON and shipped inventory |
| `CAP-DOCS-documentation-ownership` | Equal formal role standing; domain conceptual authority/design mechanism/ops routing; independent detail versus parent-owned artifact policy; remove every current ID-free denial |
| `CAP-DOCS-document-lookup` | Three kinds, filters/order/history, --file DESIGN applicability, resolve/refs; applicable ADR-only supersession refusal and unchanged outputs |
| `CAP-DOCS-document-search` | Every new kind in selection/modes/pinning and namespace/history; existing ranking policy unchanged |
| `CAP-DOCS-namespaces` | Formal role homes and rule applicability in registered roots; global identity unchanged |
| `CAP-GOV-spec-rules` | Catalog/applicability of identity/strict format/status/summary/reference/entrypoint rules and artifact boundary; existing codes/fixes remain authoritative |
| `CAP-TRACE-code-entrypoints` §§1,3.1–3.3 | Neutral DESIGN declarations/liveness/reverse lookup; DOMAIN/OPS non-applicability; no semantic correctness/public adapter claim |
| `UC-find-the-right-documents` | Unknown role question → search/filter → direct ID → needed relation/source/artifact; global/package, retired/missing controls |
| `UC-keep-the-living-spec-consistent` | Author from formal template, validate, rename via alias, source changes and design liveness; lifecycle phase owns its workflow integration clauses |
| `ARCH-05-2-components` | Docs ownership of formal definitions/governance and neutral assets; no dependency-direction change |
| Two earlier ADR files listed in targets | Exact matching partial-supersession pointers from PADR; retain accepted status and retained clauses, no rationale rewrite |
| ADR-formal-role-document-identities (planned) | Handoff promotion of PADR; exact schema/layout/authority/partial supersession decision and restatement traces |
| `CAP-DIST-sync-and-transactions`, `CAP-DLV-proposal-lifecycle`, glossary | Repair existing ingress only; no guarantee or permission transfer |
| docs/README.md and devkit-docs README | Hierarchy, canonical paths, syntax/public values and useful author routing |

Current contract restatements are rewritten together with the implementation and migration. The new decision
supersedes identity/runtime-denial clauses; existing capability validity, distribution transactions, journal
compatibility, recovery permissions and readiness remain authoritative. No historical result is restated as proof
of formal integration. Architecture and behavioral authority are selected by responsibility, not document length.

## 3. Complete canonical migration and ingress ledger

The HEAD-pinned Scout inventory found exactly four current canonical role files, zero current operations files,
no docs/packages directory and no registered namespaces. Development repeats the bounded role-root inventory at
its starting HEAD; any additional canonical role file is included by this same policy, not left ID-free.

| Old canonical/input path | New path and formal ID | Required repair / content invariant |
| --- | --- | --- |
| docs/designs/distribution-transactions.md | docs/designs/DESIGN-distribution-transactions.md; DESIGN-distribution-transactions | Active metadata/H1; full ID link to independent detail; CAP/ARCH authority retained |
| docs/designs/distribution-transactions/file-directory-replacement.md | docs/designs/DESIGN-distribution-file-directory-replacement.md; DESIGN-distribution-file-directory-replacement | Active independent node; source transaction.py relative link changes from ../../../packages to ../../packages; entry relation uses full ID; eligibility/recovery remain CAP-owned |
| docs/domain/delivery-relationships.md | docs/domain/DOMAIN-delivery-relationships.md; DOMAIN-delivery-relationships | Active metadata/H1; conceptual membership/prerequisite/provenance composition; validation/transformation remain existing owners |
| docs/domain/bundle-selection-and-installation.md | docs/domain/DOMAIN-bundle-selection-and-installation.md; DOMAIN-bundle-selection-and-installation | Active metadata/H1; available/selection/asset/projection/receipt distinctions preserved |
| proposal materials/legacy-operations/docs/operations/distribution-sync.md.txt | docs/operations/OPS-distribution-sync.md; OPS-distribution-sync | New active main node copied from archived content input, all relative references checked; four symptom/evidence rows and normal-state route; no duplicated recovery actions |

Current direct ingress to old role paths:

- `CAP-DIST-sync-and-transactions` line 114 → DOMAIN-bundle-selection-and-installation; line 370 → DESIGN-distribution-transactions.
- `CAP-DLV-proposal-lifecycle` line 43 → DOMAIN-delivery-relationships.
- `docs/steering/glossary.md` lines 16/48 → the corresponding DOMAIN IDs.
- The design entry and independent detail → each other's full formal ID where useful, never old relative paths.
- Current source living-spec-writing, ownership capability and design-template → formal paths/IDs or placeholder syntax.
- Distribution inventory test's old template assumption → formal template/pointer contract.

A scoped `rg` over docs, specs and devkit-docs found additional historical old-path mentions in these retained
records: specs/2026-11/20261116-design-document-foundation/{tasks,reconcile}.md;
specs/2026-11/20261116-domain-model-documents/{tasks,target-docs,reconcile}.md;
docs/materials/2026-11/20261116-design-document-foundation/{development-evidence,target-docs}.md;
docs/materials/2026-11/20261116-domain-model-documents/development-evidence.md. The old ADRs' ID-free policies also
remain historical decisions with partial pointers. Preserve historical file bytes and old source-path text;
record their source-history provenance and the old→new mapping in migration evidence. The source commit
bde0a923192aaea7f6a467bb6a575db4ca447f9e preserves all four pre-migration canonical files. The archived operations
source retains its halted commit provenance 55bc46fb5ce350e0a84666d6df338f8947e54e1b and .txt bytes.

No path-shaped aliases are legal. Historical paths in retained records are source-history coordinates, not a
promise of a live filesystem redirect. Development's migration evidence classifies every scoped old-path hit as
repaired current ingress, preserved historical coordinate or intentional legacy-template compatibility pointer;
any unmatched live ingress fails F5. No duplicate ID-free live canonical path is left behind. Do not mass-convert
historical materials or completed spec bodies. No parent artifacts currently need moving; add a parent-owned
artifact fixture to prove this policy, and check all actual ordinary source/artifact links after canonical moves.

## 4. Three-kind complete support matrix (F1–F6)

D = DESIGN/design, M = DOMAIN/domain, O = OPS/operations. Each cell states applicability and the test obligation;
shared owner/mechanism columns apply to every cell. Every listed test is planned, not executed in Planning.
Generic code counts only with all three actual new-kind nodes. Existing owned tiers above supply test locations.

| Surface / criterion | D | M | O | Owner, changed or reused mechanism; exact verification obligation |
| --- | --- | --- | --- | --- |
| Kind/ID/Python/JSON F1,F6 | Supported DESIGN/design | Supported DOMAIN/domain | Supported OPS/operations | docs models, append enum/rows; test definitions order/coverage, exports, prefix/kind_of/parse and unchanged record keys; existing member values/order regression |
| Canonical path/H1/namespace F1,F3 | designs/DESIGN-slug.md | domain/DOMAIN-slug.md | operations/OPS-slug.md | id_convention explicit grammars; per-kind valid global/package; wrong prefix/directory/nesting/case/word-led slug/stem/id/H1/missing token/duplicate ID controls and safe-fix idempotence |
| Required schema/status/summary F1,F3 | Exact common fields/status | Exact common fields/status | Exact common fields/status | spec_format+summary; missing block/field, non-string, malformed YAML, blank/too-long summary, invalid status/reserved area/delivery/replacement fields; missing field fixes only, invalid value no guessed fix; retired history filters; retiring DESIGN with source deletion clears/replaces obsolete entrypoints in the same snapshot and still passes governance while resolve/refs/aliases/history retain the node |
| Aliases/rename F1,F2,F5 | Same DESIGN prefix | Same DOMAIN prefix | Same OPS prefix | parse/index/reference reuse; valid alias resolves/pins, own/repeat/non-list/wrong-prefix/legacy/colliding aliases fail; current rewrite preserves aliases and historical records; composed global→package and package→global parent rename/move carries artifact subtree, verifies single parent and all ordinary links |
| Typed/prose refs F1,F2,F3 | related_designs target | related_domains target | related_operations target | model LIST_FIELDS+definition target map; all three sources and CAP/UC source fixture, list/empty/scalar/mapping/non-string/wrong-prefix/missing/duplicate/alias target, prose masking, incoming/outgoing canonical grouping and rewrite |
| Provenance/ADR supersession F1,F3,F6 | Role reserved fields fail | Role reserved fields fail | Role reserved fields fail | spec_format new-kind schema; existing Unit provenance outside refs preserved; role supersession query returns existing ARGUMENT_INVALID; ADR/PADR supersession tests unchanged |
| List/filter/order/text/JSON F2 | Direct node | Direct node | Direct node | browse/CLI reuse plus help change; each kind choice, combined filters/status/where, pagination/ID ordering/empty/malformed controls; exact public strings/keys and legacy kinds |
| Search/pinning F2 | Direct ranked/pinned | Direct ranked/pinned | Direct ranked/pinned | search reuse; lexical actual fixture, auto selection, dense/hybrid deterministic embedder fixture plus existing missing-extra contract; ID/alias/path/filename pin first once; filters/history/glossary selection |
| Resolve/refs/namespaces F2 | Global+package | Global+package | Global+package | index/config/namespaces reuse; same global/selected/all namespace fixture, cross-package/global resolution/in/out refs, unknown namespace/conflicting selectors, missing/duplicate IDs; current repo absence is not proof |
| Entrypoints F3,F5 | Optional supported paths | Inapplicable; field fails format | Inapplicable; field fails format | governance existing path model; DESIGN missing/empty/valid file/dir, malformed/external/symlink/deleted-snapshot paths, --file exact/ancestor coverage; canonical role-artifact/README excluded; DOMAIN/OPS ordinary links remain valid |
| Detail/artifact F1,F5 | Independent detail ID + support fixture | Same canonical/artifact policy | Same canonical/artifact policy | id grammar/classification, per-kind valid canonical parent+ID-free Markdown/data/image artifact; orphan/mismatched-parent/ID-bearing artifact and un-ID'd independent nested Markdown fail; inspect links and node visibility |
| Templates/instructions F4 | design.md + design-writing | domain.md + domain-writing | operations.md + operations-writing | bundle registration/core and templates directory; fill template into valid node, required fields/H1/relations, meaningful kind prompts, legacy design-template pointer destination |
| Shipped consumer F4,F6 | Formal assets discoverable | Formal assets discoverable | Formal assets discoverable | exact 11 instruction/9 template inventory; source sync/get-context list+read, built-wheel docs-only consumer with spec absent, no SDD gates/records/retention requirements |
| Canonical migration F5 | Two active migrated nodes | Two active migrated nodes | One active archived-input node | whole §3 ledger and source/link audit; current IDs found by CLI, all live ingress repaired, retained old evidence unchanged, migration old-path classification complete |
| Maintenance F5 | create/update/split/rename/retire walkthrough | Same formal lifecycle inputs | Same formal lifecycle inputs | core fixtures prove schema/aliases/terminal/reference behavior plus artifact-owning rename/root move/split/cross-kind transfer and retirement/source-deletion cleanup; lifecycle L1–L4 proves end-to-end SDD+adaptive maintenance, no transfer/duplicate statement owner |
| Existing system regression F6 | Additive supported kind | Additive supported kind | Additive supported kind | same document/governance/bundle suites including CAP/UC reciprocity, UX/ARCH/ADR/Unit behavior, memo/parser round-trip, no docs-to-spec import, no output/error/exit regressions |

Core unit Development runs lint, type checks and `just test-affected` with mode=full fallback; targeted owned
unit/integration/rule/built-wheel E2E tests above remain mandatory even if affected selection omits a consumer.
Use existing deterministic search test providers to avoid network dependence; any real external model download
needs separately authorized environment access, not an assumption in acceptance. No quantitative before/after
performance claim is made, so no borrowed-machine baseline or checkout is required.

## 5. Required phase contract and acceptance evidence

| Owner | Required phase evidence | Core interface consumed |
| --- | --- | --- |
| `PROP-design-document-lifecycle` L1 | Planning, reconciliation and source-impact routing know all three formal roles | Exact homes/IDs/schema; equal formal standing and content authority |
| Lifecycle L2 | Create/update/split/rename/reclassify/retire scenarios in global/package fixtures | Active/retired with continuing governance; same-kind aliases, independent detail IDs; move artifact ownership/links on rename/root move/split/cross-kind transfer; remove obsolete DESIGN entrypoints on retirement/source deletion |
| Lifecycle L3 | SDD skills/scaffold/adoption/baseline use formal targets and DESIGN source anchors | Neutral docs instructions/templates; shared entrypoint_bearing and existing declared feature edge |
| Lifecycle L4 | Adaptive documenter and installed-consumer guidance preserve approach neutrality | Same schema with no implicit SDD records/gates/history |
| `PROP-design-document-viewer` V1 | Groups/order/navigation/prose IDs and deep links | design/domain/operations, DESIGN/DOMAIN/OPS, global IDs and namespace selection |
| Viewer V2 | Metadata/relationships/ref graph and retired/missing states | related_* current edges, aliases identity, provenance/ADR supersession distinct |
| Viewer V3 | Canonical detail and parent-owned artifact rendering, package/deep-link parity | Flat role IDs, explicit artifact parent path and ordinary link contract |
| Viewer V4 | Public library/static/distributed assets and deliberate handbook inclusion tests | Stable core JSON/Kind strings, source identity recognized; no accidental exclusion |

Core acceptance cannot be credited with unrun sibling evidence. Core F1–F6 is a complete one-L integration unit;
these two separately owned mandatory phases complete the milestone. Source overlap for CAP-TRACE and shared use
case clauses is section-scoped and ordered core then lifecycle by Host; no concurrent cross-proposal writes.
Viewer owns its screens/interaction draft/review and frontend verification. Core defines no screens in this turn.

## 6. Planning evidence and limits

[Scout evidence](../../../docs/materials/2026-11/20261116-formal-document-kinds/scout-evidence.md) distinguishes source inspection, incoming-ref counts, body sampling,
read scopes and full snapshot verification. [Support audit](../../../docs/materials/2026-11/20261116-formal-document-kinds/support-audit.md) is the earlier baseline
inspection; it is not formal-kind runtime proof. [Core contract](../../../docs/materials/2026-11/20261116-formal-document-kinds/core-contract.md) §8 compares formal
layout/schema alternatives and assigns deterministic schema enforcement. The PADR records partial supersession.
Development tests, all five migrations and dependent lifecycle/viewer evidence remain unimplemented in Planning.
