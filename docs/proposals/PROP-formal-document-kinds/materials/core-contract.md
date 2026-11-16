# Formal role document implementation contract

This is the selected core contract for PROP-formal-document-kinds. It is a future implementation contract, not
current runtime evidence. It supersedes the earlier ID-free direction. Implementation size is not a success
criterion. Lifecycle and viewer consume this contract through their required phases.

## 1. Kind, identity and location

| Public Python member / JSON and CLI value | Prefix | Directory under every docs root | Entrypoints |
| --- | --- | --- | --- |
| `Kind.DESIGN` / `design` | DESIGN | `designs` | Optional, supported |
| `Kind.DOMAIN` / `domain` | DOMAIN | `domain` | Inapplicable, reject the field |
| `Kind.OPERATIONS` / `operations` | OPS | `operations` | Inapplicable, reject the field |

Append the three enum members and definition rows after existing members, preserving existing member values,
relative order and public output keys. Each row has `living_spec=True`, `area_scoped=False`,
`format_scope=FormatScope.EVERY_ROOT`, `heading_token=True`, `summary=Summary.ALWAYS`, `anchor=""`,
`terminal_statuses=frozenset({"retired"})`, `default_status="draft"`. Relation fields are the one corresponding
`related_designs`, `related_domains` or `related_operations` field below. No optional prefix or ID-free canonical
alternative exists.

A docs root is global `docs/` or a registered namespace's `docs/packages/<name>/`. A canonical role document is an
immediate file `<root>/<directory>/<PREFIX>-<slug>.md`. The slug uses lowercase ASCII letters/digits joined by
single `-`; its first segment contains a letter (`is_word_led_slug`). The file stem, frontmatter `id` and first H1
token `# [<ID>] <title>` agree. There is no area directory or `area` field on these kinds. Independent details use
this same flat identity grammar. Additional hierarchy is navigation through IDs, not an inherited identity.

Use a subject-qualified slug when a generic topic would collide or lose its scope across package catalogs
(for example `api-session-state` versus `cli-session-state`). A namespace does not authorize a duplicate ID;
reserve a distinct descriptive ID before authoring and validate repository-wide uniqueness. A package-root move
can retain its ID if the subject is unchanged; a subject rename keeps a same-prefix alias. Flat organization
scales through title/summary/search/kind/namespace filters and optional related_* navigation, rather than a
mandatory single-area assignment. Reconsider area/grouping through an explicit compatibility decision only when
observed catalog navigation needs a durable taxonomy that these mechanisms cannot express.

IDs and aliases are repository-wide, including across namespaces. Namespace selection affects list/search only;
resolve/refs remain repository-wide. Namespace registry schema and document record JSON keys do not change.
Existing ID parser remains permissive as documented; canonical path/slug/H1 validation belongs to governance.
Unknown prefix is unindexed; valid new prefix with an invalid canonical location is indexed but rule-invalid,
as with existing kinds. Directory mismatches and a role ID declared outside its canonical root are reported.

## 2. Metadata, statuses and references

All three require nonempty string `id`, `title`, `status`, and double-quoted English `summary` (one or two sentences,
maximum 300 characters under the default summary rule setting). The first H1 has the ID token and display title.
Canonical role documents reject `area`, because their layout is unscoped. `created_at` remains optional descriptive
metadata under existing generic handling; missing-field fixes may add it under the existing format rule contract.
Custom descriptive metadata remains allowed, but cannot redefine reserved identity, relation or lifecycle fields.

Status is exactly `draft | active | retired` in these kinds. The template and missing-status fixer use `draft`;
retained canonical migrations use `active`. Status validation uses RULE-spec-format and never rewrites an unknown
status. `retired` is terminal for default list/search; `--history` and explicit `--status retired` expose it.
Resolve/refs and alias resolution continue to work for retired documents. Document formats impose no delivery
approval process. Lifecycle owners decide when authored content becomes active or retired.

| Optional field | Shape and target | Meaning |
| --- | --- | --- |
| `aliases` | List of well-formed prior/alternate IDs with the same prefix | Identity of this document, never an edge; own ID/repetition/collision/legacy IDs forbidden |
| `related_designs` | List of exact DESIGN IDs or resolving same-prefix aliases | Relevant implementation explanation or independent detail |
| `related_domains` | List of exact DOMAIN IDs or resolving same-prefix aliases | Relevant concepts, identities, relationships or lifecycle model |
| `related_operations` | List of exact OPS IDs or resolving same-prefix aliases | Relevant evidence classification and action-owner routing |
| `related_capabilities`, `related_usecases` | Existing typed CAP/UC ID lists | Applicable behavioral or actor-goal owners |
| `entrypoints` | DESIGN only: existing workspace-relative path list | Source reading and code-to-document lookup anchor |

The three new relation fields are available on any indexed document, not only the three role kinds. Add their
names to `model.py` LIST_FIELDS and the corresponding target KindDefinition relation_fields. Keep scalar fields
and existing relation semantics unchanged. An omitted or empty list is valid. A scalar/mapping/non-string item,
wrong target prefix, missing/duplicate target or alias collision fails RULE-document-reference. Self-reference is
not a hierarchy or dependency edge; no generic cycle check, all-pairs links or reciprocal links are required.
Current prose and structured relations appear in incoming/outgoing refs and canonical rewrite. Aliases never
become edges or get rewritten; renamed current references use the existing canonical-reference fix.

Existing `spec`/`plan` current-reference fields retain their generic semantics when used. The delivery fields
`proposal`, `decomposed_from`, `depends_on`, `milestone` and ADR replacement fields `supersedes`, `superseded_by`
are inapplicable to role documents and fail their format schema when present. Do not overload these fields for
conceptual domain lifecycle edges. Cite supporting SPEC/MAT/ADR evidence in prose; retain their existing
provenance interpretation on their owning kinds. Role retirement uses `status: retired` and a prose explanation
of the replacement, with the relevant optional `related_*` edge when a successor exists. No successor is required
when a concept/mechanism simply ceases to exist. Same-kind rename preserves the old formal ID as an alias.
Cross-kind reclassification preserves the retired old node and cites the receiving node; cross-prefix aliases
remain invalid. Retired nodes remain subject to governance: terminal browsing status is not a rule exemption.
When retiring DESIGN because source is removed, remove or replace obsolete entrypoints in that same change.
Retain still-live useful anchors. Historical source locations may remain as explicitly historical prose coordinates
with the source commit, never as live entrypoint declarations. Clean stale current references and ordinary links
or identify historical coordinates explicitly; retirement does not authorize unresolved current references. `docs supersession` remains ADR/PADR-specific and returns existing ARGUMENT_INVALID for role IDs.
This is applicable-surface parity, not missing role identity support.

## 3. Content ownership and independent detail

Domain owns concepts, identity, relations and lifecycles as conceptual current knowledge. Design owns cohesive
implementation mechanisms, worked examples and datasheets. Operations owns symptom/evidence classification,
selection of an existing action owner and normal-state observation. All three are equally formal documents,
searchable/resolvable/referenceable directly; formal identity is independent of behavioral authority.

A newly authored conceptual statement can have its primary owner in DOMAIN. A normative behavioral validity,
safety or permission statement remains with its existing capability/action owner unless an explicit transfer
removes the old normative restatement in the same change and identifies the receiving owner. The current migration
transfers no distribution, delivery, transaction, recovery or readiness guarantee. Domain's conceptual authority
and design's implementation explanation are not subordinate document tiers. Architecture retains structure,
interactions, deployment, cross-cutting technical concepts, constraints, quality and risk. The glossary retains
concise term definitions and cites the appropriate conceptual owner.

An independently maintained Markdown explanation with its own question, summary, maintenance seam or direct
reader entry has its own formal ID, including a design detail or datasheet. It lives as a peer canonical file;
optional related_designs connects it to its entry. No manual reciprocal parent registry is introduced.

A parent-owned support artifact has no independent question/maintenance contract and is meaningful only with its
one identified parent. Store it under `<root>/<directory>/<PARENT-ID>/artifacts/<relative-path>` and link it from
that parent's body with an ordinary relative link. CSV, images, diagrams and generated data need no fake IDs.
A Markdown support artifact is allowed only in that artifacts subtree, has no `id` or first-H1 ID token, and names
its parent in its text; it never substitutes for an independently maintained role document. A README is an optional
navigation file, not canonical role content. No empty artifact directory or README is required.

Governance adds a narrowly scoped role-artifact path classification: verify the same-kind canonical parent file
exists in the same root, reject ID-bearing Markdown in the artifact subtree, and exclude valid ID-free artifacts
from canonical format/summary/H1 checks. No blanket exclusion of nested Markdown is permitted: an ID-free nested
independent detail outside artifacts is invalid. Index selection stays generic: ID-free artifacts remain outside
identity; the rules reject an accidentally indexed artifact. Ordinary artifact/source link integrity and semantic
parent ownership are reviewed in F5; they are not claimed as indexed reference edges.

A same-kind rename moves `<OLD-ID>/artifacts/` to `<NEW-ID>/artifacts/` in the same change as its canonical file,
and keeps OLD-ID only as a valid identity alias. A move between docs roots carries the subtree to the new root
(with no alias needed if the ID stays the same). Repair all current ordinary links to moved artifacts, plus
relative source links in the moved document/artifacts. An alias never legalizes an orphan old-ID artifact directory.
A split assigns every retained artifact exactly one resulting canonical parent; move it to that parent's subtree
and repair links instead of creating a reciprocal ownership registry. A cross-kind transfer does the same under
the receiving role directory while retaining the retired old node and its explicit replacement reference. An
artifact no longer maintained as current support may be retained in separately identified historical materials;
record its provenance and repair current ingress. Do not leave an unowned role-artifact subtree. Lifecycle consumes
these composed invariants; viewer follows the resulting canonical parent/artifact destinations.

## 4. Source entrypoints and interface consumers

DESIGN entrypoints are optional because a design explains current implementation and benefits from source reading
and reverse lookup. Use the existing safe workspace-relative path normalization, existence, snapshot deletion,
symlink escape and reverse whole-segment coverage behavior. No field or complete code catalog is required.
DOMAIN/OPS route to concepts or existing action owners, so entrypoints are inapplicable rather than unvalidated.
Their code/artifact/owner links remain useful body links. Reject their entrypoints field via RULE-spec-format;
do not silently claim reverse code lookup. CAP/UC entrypoint and traceability requirements are unchanged.

`entrypoint_bearing(path)` stays the shared public applicability API. It recognizes canonical DESIGN files in global
and package roots and excludes role artifact/README paths; its existing package-root mapping remains configuration
independent. Existing CAP/UC behavior is retained. The lifecycle phase consumes this API for derivation/apply;
core owns declaration/liveness/reverse lookup and CAP-TRACE-code-entrypoints §§1,3.1–3.3 only. Lifecycle owns that
capability's spec derivation/apply sections. Existing architecture edges already permit these consumers.

No new feature edge is required: documents owns model/parser/index/query, governance depends on documents, both
use existing dist/agt boundaries. No docs-to-spec import, new layer, package, test tier or assumed docs MCP service.
Public Python Kind exports, prefix tables, CLI choices/help, JSON strings, reference fields and terminal behavior
are additive contracts; existing kind strings, document/reference JSON keys, notices, result sentinels, errors,
ordering and exit statuses are unchanged. No new command is needed solely to create a role document.

## 5. Authoring and neutral distribution

Under `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`, add templates `design.md`, `domain.md`,
`operations.md` and instructions `design-writing.md`, `domain-writing.md`, `operations-writing.md`. Register each
instruction as its own instruction asset and include it in core. Templates remain in the existing directory asset.
Retain `templates/design-template.md` as a compatibility pointer to `design.md`, remove ID-free prompts, and test
the pointer destination. There are eleven core writing instructions and nine template files including this pointer
(the current six templates plus three formal ones); the pointer is not a fourth formal template.

Each template supplies the exact required metadata, H1 and optional relation placeholders, using example IDs only.
Design prompts: reader question, mechanism, owner boundary, source/entrypoints, useful details/examples/datasheets,
maintenance/next action. Domain prompts: conceptual question, concepts/identity, relationships/lifecycles,
owner boundaries, examples and maintenance; no mandatory class/schema catalog. Operations prompts: symptom,
discriminating evidence, existing action owner, normal-state observation, limits and maintenance; no duplicated
steps/permissions. Instructions trigger before the respective kind's authoring/editing and specify these schema,
reference, detail and ownership rules without imposing SDD Units, gates, histories or immutable records.

Replace ID-free clauses in living-spec-writing; update architecture-writing's adjacent role boundaries, bundle
AGENTS/constitution template pointers, seed/docs/README hierarchy and repo docs/README. Keep the always-loaded
pointer concise; per-kind instructions own detail. All shipped references are self-contained placeholders or
bundle-local paths, never this repository's CAP/ADR IDs. Source registration, sync/get-context visibility, exact
inventory tests and docs-only installed built-wheel tests are required. Do not edit projected files as source.

## 6. Required dependent interfaces

Lifecycle L1–L4 (PROP-design-document-lifecycle): consume these paths/statuses/schema/entrypoint flags for impact
planning; create/update/split/rename/reclassify/retire; reconcile source-owned instructions and proposal scaffold;
prove SDD and adaptive consumers without implicit SDD obligations in neutral docs.
Viewer V1–V4 (PROP-design-document-viewer): consume `design`, `domain`, `operations`, DESIGN/DOMAIN/OPS prefixes,
related_* fields, retired filtering and globally unique IDs; groups/navigation/deep links/prose refs/metadata/graph;
parent-owned artifacts, namespaces and missing states; public frontend/static/package assets and deliberate
handbook inclusion policy. New kinds are not equivalent to proposal/feedback dashboard rows. No custom editor or
new docs MCP service is implied. These are required milestone phases, not optional core support gaps.

## 7. Migration identities

| Source/input | Exact canonical destination / ID |
| --- | --- |
| docs/designs/distribution-transactions.md | docs/designs/DESIGN-distribution-transactions.md / DESIGN-distribution-transactions |
| docs/designs/distribution-transactions/file-directory-replacement.md | docs/designs/DESIGN-distribution-file-directory-replacement.md / DESIGN-distribution-file-directory-replacement |
| docs/domain/delivery-relationships.md | docs/domain/DOMAIN-delivery-relationships.md / DOMAIN-delivery-relationships |
| docs/domain/bundle-selection-and-installation.md | docs/domain/DOMAIN-bundle-selection-and-installation.md / DOMAIN-bundle-selection-and-installation |
| materials/legacy-operations/docs/operations/distribution-sync.md.txt | docs/operations/OPS-distribution-sync.md / OPS-distribution-sync |

All five targets are active canonical nodes. The two design nodes use optional related_designs as useful; no
reciprocal edge is required. Repair relative source links after flattening the detail and use full IDs between
canonical documents. The four old paths cease to hold canonical content. They did not declare formal IDs, so no
invalid path-shaped aliases are created. Retain no live ID-free duplicate or redirect entry as a second canonical
route. Current ingress moves to full formal IDs. Historical paths resolve through the archived evidence at the
recorded source Git commit, not by pretending aliases can resolve paths.

## 8. Formal alternatives and enforcement allocation

Formal standing is the fixed goal; all options below provide first-class Kind/ID/index standing.

| Choice | Organizational / metadata / scale / cohesion trade-off | Outcome |
| --- | --- | --- |
| Flat role root, full prefixed stem, optional typed relations | Topic slugs and search organize a repository-wide role catalog; namespace partitions package ownership; crosscutting concepts need no invented area. Very large catalogs rely on list/search and related_* navigation rather than folder taxonomies. Independent details stay cohesive through chosen links. | Selected for all three kinds; the current four-role inventory spans distribution and delivery, with no existing role-area taxonomy. |
| Area-scoped formal roots `<kind>/<area>/<PREFIX>-<AREA>-<slug>.md`, required area metadata | Useful when stable exclusive areas organize many role docs; creates a second classification in addition to namespace and requires reassignment/alias policy for concepts spanning areas. Prefix+area is viable and fully formal. | Not selected: current role questions compose several owner areas and are better named by their subject; no observed exclusive role-area ownership warrants imposing area identity. Reconsider through an explicit schema change when actual catalog navigation needs a stable area taxonomy. |
| Grouped formal roots `<kind>/<topic>/<PREFIX>-<slug>.md`, global stem IDs | Physical cohesion of a large mechanism and its details; independent identity preserved. Topic changes need path migration and path-pinning repairs even if IDs stay constant; arbitrary grouping needs a second path grammar. | Not selected: flat IDs plus selected relations already express these four documents' cohesion; future nested canonical groups require explicit grammar compatibility decisions. |
| Source-specific `designs`/`domains`/`operations` relation fields only | Concise names but can read as ownership or mandatory completeness and multiply source-specific applicability rules. | Use target-typed `related_*` fields on any indexed source instead, with no completeness or reciprocity claim. |
| All kinds accept code entrypoints | Uniform field availability; DOMAIN/OPS can be falsely treated as implementation doorways despite their conceptual/action-routing responsibility. | DESIGN accepts optional paths; DOMAIN/OPS use owner/body references. This is semantic applicability, not lesser formal standing. |
| No terminal status versus retired | Both permit mutable current content. No terminal value requires deletion or an ad-hoc filter to keep obsolete explanations out of default discovery. Retired retains identity/history and lets existing terminal selection work. | Use strict draft/active/retired vocabulary on these kinds only; existing kinds retain their status contracts. |

Enforce the exact new-kind required/status/reserved-field schema in `governance/usecases/spec_format.py`, selected
by Kind/path rather than by prose or templates alone. Required string fields reuse RULE-spec-format's existing
find/fix behavior; summary substance/length remains RULE-document-summary. Bad status, inapplicable area/delivery/
replacement/entrypoints fields are non-fixable RULE-spec-format findings with deterministic field-specific
remediation. Valid custom descriptive metadata is retained. Enforce identity/flat path/stem/H1/word-led slug and
artifact-parent/ID exclusions in id_convention.py; keep parse/index permissiveness unchanged. No separate generic
schema framework or new public error code is needed. Missing fields under malformed blocks retain current refusal
behavior. Aliases and new relation shapes/target kinds/resolution use RULE-document-reference. New-kind tests prove
scope and codes for all three rules rather than accepting template-only constraints.

Source entrypoints name files/directories only, as CAP-TRACE-code-entrypoints defines; they do not name Python
symbols as field values. A symbol useful to a reader is linked/described in the design body while its containing
file/directory is the optional entrypoint. These documentation anchors do not designate public adapters or claim
that every symbol implements BaseUseCase. Exposed-operation contracts in ARCH-05-2-components remain unchanged.
