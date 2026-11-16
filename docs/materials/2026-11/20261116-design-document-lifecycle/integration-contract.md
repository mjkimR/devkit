# Formal document delivery integration contract

## 1. Evidence boundary and option comparison

Source inspection: bde0a923192aaea7f6a467bb6a575db4ca447f9e, then reviewing-only commit
306b30ed6d8aff09c26c3547cfffc62705d3123a. The older core support audit's 534ad541 baseline is historical;
source paths relevant to this phase were re-read at this worktree's HEAD. No implementation tests ran in Planning.

| Viable integration | Benefit | Cost / risk | Choice |
| --- | --- | --- | --- |
| A: existing delivery boundaries consume shared core ownership/Kind policy | One identity/role authority, existing gates and records, generic runtime reuse where proved | Semantic per-change impact and source agreement need explicit reviewer evidence | Selected |
| B: shared delivery-specific role checklist/reference consumed by spec and adaptive | Less repeated procedure text | Cross-package private asset coupling or new shared distribution asset; can make neutral docs own SDD process | Rejected; consumers reference neutral core contracts and keep approach-specific procedure locally |
| C: add runtime formal-impact manifest/checker and mandatory whole-kind coverage | Deterministic presence reporting | New parsed schema/registry and false whole-layer work; cannot prove semantic agreement | Rejected; existing targets plus bounded body evidence cover this requirement |

Formal kinds are mandatory in every option. ID-free ownership and optional gap-only integration are not options.

## 2. Core interface consumed

The Host's selected future core interface is pinned and hash-verified in
[core consumption record](core-interface-pin.md), source 504e2e12006ab3e2aad2b8ce470607646ad4c4ac. Core remains the
single schema/ownership authority; the consumption record names exact applicable integration values and tests.
Development handoff requires its delivered implementation revision and prerequisite evidence, not this design pin.

`entrypoint_bearing(path)` in
`packages/devkit-docs/src/devkit_docs/features/governance/services/entrypoint_paths.py:26-34` already derives from
Kind definitions and namespace mapping. `devkit_spec.features.entrypoints.services.derive` calls it for each
non-waived reconciliation target. Lifecycle tests prove each newly eligible kind, and assert
`not-entrypoint-bearing` for each ineligible kind. DESIGN source anchors are reviewed for the mechanism subject. DOMAIN and OPS use body source/action-owner
links and explicitly skip derive/apply; their entrypoints field is rejected by core schema. CAP/UC doorway heuristics and reciprocity do not become universal rules.
No new CLI selector, output schema, error code, approval or workflow stage is planned.

## 3. Change-specific impact and maintenance

The existing proposal/plan body records a compact assessment of design, domain and operations: affected ID(s) or
prospective destination, changed statement/responsibility, source identity and owner, create/update/split/rename/
retire action, source/detail/artifact evidence and verification. An unaffected role gets a bounded reason tied to
the change. This is body guidance, not a parsed mandatory registry or a new record type. Impact assessment is
refreshed against actual implementation diff during review and reconcile. Required affected docs are reconciled;
unaffected documents are left alone. Source changes after a comparison invalidate the affected evidence.

Apply the following operations separately to each of the three kinds in global and registered package roots:

| Operation | Required handling and comparison |
| --- | --- |
| Read | Search/list/resolve full canonical IDs and aliases, incoming/outgoing refs and needed core writing instruction; traverse only useful owner/detail links |
| Create | Use core template/grammar, unique primary owner, actual implemented subject and source identity; add warranted typed relations and incoming routes |
| Update | Compare changed statements with the retained source; update applicable summary/relations/source anchors and regenerate only artifacts whose actual source changed |
| Split | Allocate each transferred statement one resulting owner; give independent formal detail its own ID. Assign every retained support artifact exactly one resulting canonical parent, move its subtree/path and repair links; leave no stale duplicate or unowned subtree. Replace old normative duplicate with orientation link |
| Rename / root move | Move canonical path/H1/ID and ID-owned artifact subtree together; preserve same-kind old-ID aliases on rename. An unchanged-ID root move needs no alias. Repair current prose/structured references, all ordinary artifact links and relative source links in moved docs/artifacts; reject orphan old-parent folders even when an alias resolves; check collisions and namespace destinations |
| Reclassify | Retire the old same-kind identity, create the receiving kind's canonical node, transfer sole statement ownership and assign each retained artifact exactly one receiving canonical parent under its role directory; move support and repair current refs/ordinary links without stale duplicates; cross-prefix aliases remain invalid |
| Retire | Set retired, retain resolve/refs identity and applicable replacement links, remove/replace obsolete DESIGN entrypoints in the same change as source deletion, retain still-live useful anchors and keep removed coordinates only as explicitly historical prose plus commit; retained retired nodes remain rule-checked; preserve required provenance; repair incoming current refs and owner/detail/artifact links; do not borrow ADR supersession fields |

Do not alias one old ID to multiple split destinations. Retain the original active ID only if it still owns a
maintained subject; otherwise retire it and name useful successors through core relations/prose. Repair current
references to their actual receiving owner. Retiring an entry does not imply deleting shared
support files or historical materials. For a support file, inspect its other owners before moving/removing it;
verify retained destinations and non-Markdown links separately because formal refs alone cannot prove them.

SDD uses existing `target-docs.md`, `plan.md`, review and `reconcile.md`. Every modified or deleted formal document/support file is a
`modified` target; retired retained documents use core terminal status. Removed paths additionally have an explicit
retirement comparison in the body and replacement targets where present. Existing RULE-reconcile-contract
implementation (features/governance/usecases/reconcile_contract.py:12–16,109–116) accepts changed or deleted paths
as evidence, so no new resolution enum is needed. No mismatch required by scope is waived.

Adaptive uses existing assignment source identity, governing IDs, documenter return and mutable current-context
map. Formal standing changes neither approach nor authority. The documenter writes only after described source
integration, except an explicitly agreed future shared interface; it reports missing required source evidence as a
conflict/unverified result. It creates no implicit Unit, envelope, gate, retrospective ADR or per-change record.

## 4. Required end-to-end scenarios

- SDD multi-role: a state-lifecycle/diagnostic change affects capability plus DOMAIN meaning, DESIGN mechanism and
  OPS symptom/evidence routing. Generate target-docs, plan the exact IDs, implement selected source change, review
  semantic agreement and reconcile all changed owners plus independent detail/support artifacts. Existing action
  executor authority is unchanged; no duplicated recovery procedure.
- SDD single-role: a mechanism refactor changes DESIGN while domain meaning, externally visible behavior and OPS
  routing remain stable. Plan/review evidence explains the unaffected responsibilities. Only warranted DESIGN and
  supporting artifacts change; no empty CAP/UC/domain/operations document is required.
- Adaptive: retained implementation changes each warranted role; documenter receives exact source identity and
  governing IDs, uses formal templates, compares source, updates context map and runs project/document checks.
  Exercise create/update/split/rename/root-move/reclassify/retire for each kind in global and package roots. Assert no implicit specs/, workflow/envelope/gate files
  or approach change; preserve explicitly pre-existing SDD history if fixture includes it.
- Adoption: brownfield canonical ID-free input migrates once through core formal policy; legacy history remains
  historical. Baseline includes all warranted retained formal docs and missing-source/required-doc gaps; no gap
  qualifies as readiness, no experiment history is reconstructed.
- Maintenance: per kind, rename and retire a document referenced by prose and relation fields, aliases, independent
  detail and ordinary support links. Repair references/relative paths and retain shared support; verify resolve,
  incoming/outgoing refs, actual file destinations and source agreement after every operation.
- Composed rename/root-move plus artifacts: for each of DESIGN/DOMAIN/OPS under both SDD and adaptive, in global
  and registered package roots, start with a canonical parent, one ID-free Markdown support artifact, non-Markdown
  support, independent formal detail and ordinary incoming/source links. Rename the parent and move its subtree;
  then move it between global/package roots in both directions, preserving the ID for the root move. Resolve the
  old same-kind alias to the renamed parent, prove old parent folders absent, and check links from outside and
  inside the moved subtree. Run core path/identity/reference checks, including a deliberately orphaned old-ID
  subtree control which must remain invalid despite the alias. Derive/apply DESIGN anchors via the core API;
  DOMAIN/OPS remain ineligible. The independent detail retains its own identity.
- Composed retire plus source deletion: for each kind × approach × root, remove the supported source/subject and
  retire the retained canonical document in the same change. For DESIGN remove/replace dead entrypoints while
  retaining useful live anchors; retain removed source coordinates only in historical prose with commit. For
  DOMAIN/OPS repair body source/action-owner links without adding entrypoints. Repair incoming current routes and
  ordinary support links, assign retained support one live or retired canonical parent or explicitly historical
  materials with provenance, and leave no stale duplicate/unowned subtree. Assert default browse omission,
  history/resolve/refs access and full core rule validity of the retired node. A retired DESIGN with a deleted
  live entrypoint must fail liveness checking; retirement cannot waive the check.
- Composed split/cross-kind transfer plus artifacts: each kind × approach × root allocates statements, independent
  detail and every retained artifact to one canonical owner, repairs ingress and relative links and verifies no
  stale duplicate. Cross-kind transfer retains the retired old identity and replacement reference, rejects
  cross-prefix aliases and validates applicable entrypoints for the receiving kind using core policy.
- Controls: metadata-only document target yields no selected source anchor; core-ineligible kind yields no pair;
  unregistered/unsupported input follows existing contract; unrelated formal role remains byte-identical. CAP/UC
  derivation/reciprocity, registered namespace selection, malformed metadata and alias collisions retain behavior.

## 5. Verification matrix

The L1 operation matrix is DESIGN/DOMAIN/OPS × read/create/update/split/rename/root-move/reclassify/retire ×
SDD/adaptive × global/registered-package roots. The composed scenarios above are required in addition to
standalone operators; split and transfer include one-parent artifact allocation. All other applicable rows
are exercised separately for design, domain and operations, with explicit ineligible controls. Execution reports name actual core kind/ID/path,
source revision, owner, command and observed outcome per row; an unexecuted or generic-only assertion is a gap.
Tests implement scripted procedures, not proof an autonomous agent made semantic judgments.

| Requirement / surface | Runtime or source owner | Exact verification owner / command |
| --- | --- | --- |
| L1 full kind × operation × approach × root matrix above, including composed artifact moves and source-deletion retirement; source and detail/artifact agreement | Core schemas reused; spec/adaptive procedures changed | New files packages/devkit-spec/tests/e2e/bundles/spec/test_formal_document_lifecycle_scenarios.py and packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_formal_document_lifecycle_scenarios.py; run `uv run pytest packages/devkit-spec/tests/e2e/bundles/spec/test_formal_document_lifecycle_scenarios.py packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/test_formal_document_lifecycle_scenarios.py`. Script actual docs commands/reference fixes and assert final file content/links/source hashes; label semantic review evidence separately |
| L2 generated formal impact/migration/applicability sections | proposals/usecases/scaffold.py | packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py; `uv run pytest packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py` |
| L2 core eligibility and per-kind source anchors; alias/namespace/apply idempotence/skip controls | Existing entrypoints derive/apply/CLI feature | packages/devkit-spec/tests/integration/features/entrypoints/{test_derive,test_apply,test_cli}.py; `uv run pytest packages/devkit-spec/tests/integration/features/entrypoints` |
| L2 multi-role and single-role through plan/review/reconcile; no unrelated edits | spec-plan/review/sync/planning/completion assets | Existing packages/devkit-spec/tests/integration/bundles/spec/ with focused test_formal_document_lifecycle_guidance.py; scripted E2E file above generates blueprint and exercises target handling with core kinds |
| L3 brownfield routes and baseline retained coverage/gaps/source invalidation | brownfield-adoption and sdd-baseline source assets | packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py and test_writing_guidance.py; packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py; `uv run pytest packages/devkit-spec/tests/integration/bundles/spec/test_sdd_baseline_guidance.py packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py` |
| L3 adaptive no implicit SDD records, retained map, source-bound documenter return | adaptive documents/documenter/pointers | packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev_documents.py; new E2E scenario above; `uv run pytest packages/devkit-adaptive/tests/integration/bundles/test_adaptive_dev_documents.py` |
| L4 installed lifecycle source assets and registered pointers agree | spec and adaptive bundles | packages/devkit-spec/tests/integration/bundles/spec/; packages/devkit-adaptive/tests/integration/bundles/; adaptive existing tests/e2e/bundles/adaptive_dev/test_installed_consumer.py. New lifecycle SDD E2E verifies installed spec guidance after sync and get-context, not just raw strings |
| Required core prerequisite evidence, not owned implementation | formal-core docs package | Core handoff supplies three-kind support/migration ledger and packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py plus tests/e2e/bundles/docs/test_installed_consumer.py outcomes; lifecycle reruns impacted prerequisite checks when delivered source changes |
| Required viewer milestone evidence, separate owner | viewer package | `PROP-design-document-viewer` V1–V4; lifecycle cannot claim milestone complete without it |
| Existing contracts/public output/regression | affected spec/adaptive source and tests | `just lint-check spec`, `just check spec`, `just lint-check adaptive`, `just check adaptive`; `just test-affected --base <development-base>` keeping `mode=full` fallback; explicit relevant E2E above; `uv run devkit rules check --ci --base <development-base>` |

No production code or tests are changed in this Planning turn. New test filenames are prospective under named
existing parents, not assertions that files already exist. Core schema/identity/reference tests remain core-owned;
lifecycle scenarios reuse them with new-kind evidence across actual downstream integration.

## 6. Scoped support and provenance

Scout ran in the assigned worktree at frozen HEAD 306b30ed6d8aff09c26c3547cfffc62705d3123a. Before/after status was
clean with identical HEAD, so the complete nonignored tree equals that HEAD tree. The post-return file-content/mode
SHA256 inventory was e4c9bcf2e44360e9dda986ddcda2bce1c1fd5fa66e97d6711a83f05bae4e2ad9. No outside-tree read or write was
reported by Scout. The later Host-admitted immutable core artifact is the sole extra read scope, recorded in
core-interface-pin.md. This is emulated scope verification, not native confinement.

Incoming-reference queries started at each touched capability and ADR. Scout inspected all 7 incoming nodes for
`CAP-DOCS-documentation-ownership`; first pages only for `CAP-DOCS-document-model` (49 total),
`CAP-DOCS-document-lookup` (28), `CAP-DOCS-document-search` (35), `CAP-DOCS-namespaces` (23),
`CAP-TRACE-code-entrypoints` (41) and `CAP-DLV-proposal-planning` (155). Unread pages are not behavior evidence.
Visible incoming contracts include `CAP-GOV-spec-rules`, `CAP-HARN-agent-guidance`, `CAP-COLL-work-scope-registry`,
`CAP-DLV-spec-bundles`, `CAP-DLV-delivery-workflows` and `CAP-DLV-proposal-lifecycle`.

The worker re-ran full incoming queries for `CAP-DLV-sdd-baseline-adoption` (13 nodes),
`ADR-documentation-ownership-and-linked-design-entries` (7), and `ADR-linked-domain-relationship-views` (6).
The Scout's final baseline list was a misattributed query and is not relied on. Verified baseline incoming owners
include `ADR-adaptive-development-and-research`, `ADR-post-merge-verification`, `CAP-DLV-adaptive-development`,
`CAP-HARN-agent-guidance`, `UC-adopt-in-an-existing-repository` and `UC-adopt-sdd-from-adaptive-development`; the rest
are historical MAT/PLAN/REC/SPEC records. The two ADR incoming sets include their current ownership capability,
core proposal and historical foundation/domain records. No historical content is silently migrated.

Bounded body evidence, distinct from node counts:

- `CAP-DOCS-documentation-ownership` §3.1–3.2 assigns unique authority, role separation, ARCH boundaries and existing
  operational action owners. Its §3.3–3.4 ID-free standing is current behavior explicitly replaced by core.
- `ADR-documentation-ownership-and-linked-design-entries` §4 (lines 38–53) and
  `ADR-linked-domain-relationship-views` §4 (lines 42–54) hold the ID-free decisions; core owns their supersession.
- `CAP-TRACE-code-entrypoints` lines 21–26 and 63–65 restrict current CAP/UC applicability. Lifecycle changes §§3.4–3.7 and applicable
  consumer/interface descriptions; core owns §§3.1–3.3 and the applicable-kind authority.
- `CAP-DLV-proposal-planning` lines 39–48 separates command/gate/question/scaffold/governance owners. This phase
  changes impact/scaffold guidance, not acceptance authority.
- `CAP-DLV-sdd-baseline-adoption` §3 rules 3–5 maps retained items to implementation/docs/evidence and disallows
  required gaps in readiness; new formal-role coverage extends that existing boundary.
- Adaptive documents.md steps 6–13 and documenter steps 2–6 require source identity, integrated source, current-state
  documents and no per-change SDD record. Their concrete role routing currently omits formal roles.
- spec entrypoints/services/derive.py target selection already queries docs `entrypoint_bearing`; spec-entrypoints
  skill review/apply and command descriptions still explicitly say CAP/UC. Reuse needs three-kind proof.


Additional scoped Scout pass confirmed `CAP-DLV-delivery-workflows` incoming refs: 204 total, first 20 inspected,
184 unread. Visible owners include `ADR-delivery-approval-and-lifecycle-authority`, `ADR-review-loop`,
`ADR-post-merge-verification`, `CAP-DLV-delivery-roles` and `CAP-DLV-adaptive-development`. Its rule 9 lines 110–118
owns reflection/reconcile before integration; rule 15 lines 145–153 owns affected-contract/diff comparison.
The structural `UC-keep-the-living-spec-consistent` is not a semantic drift/reconciliation engine. This proposal
restates formal impact at those existing delivery rules and only adds structural scenarios to that use case.
No outside-tree reads/writes reported; before/after content+mode inventory matched
9b28830282a954a95c22edcea325a2684f48aa810f55c6ba83b5847dfc810a1b at unchanged HEAD306b30e.

## 7. Updated-input consumer consistency

Continuation base is aa8413847220cc9dc6528a267505954c727837f8; source inventories and both Scout records
remain valid for unchanged sources. The only new source input is the immutable core contract at
504e2e12006ab3e2aad2b8ce470607646ad4c4ac, verified as 22110 bytes with SHA256
1d724834426991e04904fd9f1677f60235de49764d9a1863ad9c8d112c55f413. Adapter/namespace/source metadata
match the Host payload. Its new composed invariants affect spec-plan/planning/scaffold impact selection,
spec-review/completion comparison, spec-sync maintenance and adaptive documents/documenter returns. These already
own the same responsibilities in target-docs; their planned acceptance now explicitly includes the composed
scenarios in section 4 and matrix in section 5. Entrypoint derive/apply continues to call the core API; no duplicated
applicability table, new feature edge or neutral-docs lifecycle obligation is introduced. PADR option 1 and L1–L4
are unchanged. This is contract consistency evidence, not delivered runtime or semantic execution proof.
