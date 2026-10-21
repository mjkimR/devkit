---
id: PROP-unit-dependencies-and-milestone-scope
title: Unit-level depends_on and coarse milestone scope
summary: "Allows proposal and spec anchors to declare depends_on prerequisites across units and defines milestone authoring guidance so milestones remain multi-unit themes rather than single-proposal gates."
status: accepted
created_at: 2026-10-21
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/
    - docs/capabilities/delivery/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/harness/
    - docs/decisions/
    - docs/development/reference/
    - docs/roadmap/
  excludes:
    - packages/devkit/
    - packages/devkit-dist/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-unit-dependencies-and-milestone-scope] Unit-level depends_on and coarse milestone scope

## 1. Background & Hypothesis

`ADR-milestone-documents` and `CAP-DOCS-document-model` restrict `depends_on` to milestone documents (`MS-<slug>`)
and validate only `MS-` target prefixes (`RULE-document-reference`). Because proposals and specs have no way to
declare ordering prerequisites against other work units, agents and authors have used milestones as fine-grained
dependency gates—creating 1-proposal milestones (for example splitting individual maintenance playbooks or
narrowing a milestone to a single CLI entrypoint) whenever one unit must wait for earlier units to finish. In
addition, milestone `Exit condition` sections have drifted into feature-level specification checklists rather than
coarse phase or theme outcomes.

The hypothesis is that separating **unit-level prerequisite ordering** from **milestone grouping** restores
milestones to their intended role:

1. Allowing unit anchors (`proposal.md` and `spec.md`) to declare `depends_on` over prerequisite units (`PROP-<slug>`
   or `SPEC-<slug>`) moves sequencing gates down to the work-unit level.
2. Defining explicit milestone sizing and abstraction rules in the Backlog guidance and milestone template discourages
   milestones used solely as single-proposal sequencing gates and keeps detailed CLI/implementation contracts inside proposals and specs.

## 2. Planning Decisions

- **D1 — Typed graphs:** Unit anchors accept only PROP/SPEC anchor IDs, and milestones retain MS-only
  dependencies. The graphs remain separate. Validate list/string shape, exact target identity, ambiguity,
  self-edges and cycles across live unit anchors, including completed target resolution and namespaces; no lineage graph is stored.
- **D2 — Lifecycle:** Handoff carries outgoing dependencies and rewrites incoming references to the resulting
  SPEC. Decomposition and supersession do not imply fulfillment or automatic successor selection. Backlog
  reviews each incoming edge with the user and replaces it with the required child/successor set, or removes it
  only when the prerequisite is explicitly waived. Rejection, deletion and session reclassification likewise
  require a per-dependent disposition in the same authorized change; they never satisfy an edge automatically. Only live incoming direct
  dependencies require repair; retained completed history is not rewritten or continuously maintained. A retained
  rejected PROP remains resolvable but blocked. An unresolved missing target is invalid, never ready.
- **D3 — Recommendation, not delivery certification:** An edge is satisfied only by a uniquely resolved SPEC
  whose anchor is completed in the selected local base snapshot. This is a status-based scheduling signal, not
  verification of tasks, reconciliation, approvals or outcome coverage. PROP references are never satisfied;
  incomplete SPECs are blocked. A missing, ambiguous, malformed or unreadable base result is a Backlog action.
  Read the base rather than the current activity checkout; report the base ref and commit used. Do not fetch
  implicitly or claim remote freshness. Active branches cannot substitute their completion state for the base.
- **D4 — Minimal authoring surface:** Keep dependencies as optional frontmatter, omit the field when empty, and
  document examples in proposal/spec templates and Backlog. Do not add creation CLI flags or a readiness command
  in this change. Existing index, refs and rules supply deterministic structure; spec-next supplies recommendations.
- **D5 — Simple milestone ownership:** A milestone groups direct PROP members only. User and agent jointly
  review the theme and decompose it into proposals. Handoff MUST NOT carry milestone metadata to the SPEC.
  Remove `devkit spec new --milestone` and its direct-spec API parameter in place; direct spec templates
  do not advertise or write milestone membership. Existing SPEC milestone metadata is ignored for membership,
  without a legacy reader or compatibility shim; no bulk historical cleanup is performed.
  On-demand code/Git inspection can answer downstream questions, without a stored MS-to-PROP-to-SPEC lineage.
- **D6 — Orthogonality:** `SPEC-deterministic-milestone-completion` is an independent work unit. This
  proposal assumes none of its schema, completion or lineage design. It adds direct prerequisite edges only,
  no confirmed-coverage evaluator, automatic completion or persistent delivery lineage.

## 3. Proposed Design & Impact

### Document model and `RULE-document-reference`

- Extend `parse_document` (`CAP-DOCS-document-model`) so `depends_on` is valid on both `Kind.MILESTONE` and unit
  anchors (`is_unit_anchor`: `proposal.md` and `spec.md`), remaining invalid on other document kinds.
- Update `RULE-document-reference` (`CAP-GOV-spec-rules`):
  - On a milestone (`MS-`), `depends_on` continues to require `MS-` IDs and checks milestone dependency cycles.
  - On a unit anchor (`PROP-` or `SPEC-`), `depends_on` requires `PROP-` or `SPEC-` IDs (resolving through the
    document index, with `--history` / completed specs resolvable as existing documents) and checks unit dependency
    cycles across `PROP-` and `SPEC-` nodes.
  - Existing handoff reference rewriting (`CAP-DLV-proposal-incubation` §4.7) and `devkit rules fix` (`_handed_off`)
    automatically rewrite `depends_on` entries from `PROP-<slug>` to `SPEC-<slug>` when the prerequisite proposal is
    handed off, and `handoff` carries `depends_on` from `proposal.md` to `spec.md`.

### Readiness and Backlog / `spec-next` procedures

- **Unit readiness:** A unit's `depends_on` prerequisites are satisfied when every referenced ID resolves to a
  completed spec (`SPEC-<slug>` with `status: completed` on the base), evaluated one direct edge at a time;
  do not recursively reopen prerequisites of a completed SPEC. Completed historical SPECs are terminal nodes for scheduling and cycle traversal. A referenced `PROP-<slug>` or an incomplete
  `SPEC-<slug>` means the prerequisite is still unsettled. As with milestone `depends_on`, ordering is a start
  condition enforced at decision/recommendation points rather than a hard refusal if the user explicitly chooses to
  start out of order.
- **`spec-next` selection (`next-work.md`):** Apply the unit dependency filter before existing priority and milestone ordering, including
  critical drafts. Preserve the existing critical-priority milestone exception and all other milestone ranking;
  unit readiness does not change milestone readiness semantics. Drafts whose unit `depends_on` includes unsettled work (or
  invalid/rejected/missing targets) are reported separately as blocked or Backlog actions rather than recommended for
  immediate pickup.
- **Backlog lifecycle (`backlog.md`):** When decomposing, superseding, reclassifying to `session`, or rejecting a
  proposal that other units list in `depends_on`, Backlog inspects incoming `depends_on` references (`devkit spec refs
  PROP-<slug> --direction in`) and updates or clears them in the same commit with the user's decision. Enumerate all
  namespaces for live incoming direct edges. Completed historical anchors remain unchanged. If the required dependent edit is outside
  authorized write scope, stop the lifecycle mutation and ask the Host to coordinate the scope; never silently
  delete the prerequisite or mutate another worker's checkout.

### Coarse milestone scope and authoring guidance

- Update `backlog.md`, `docs/roadmap/README.md` (and seeded `bundle/seed/docs/roadmap/README.md`), and
  `bundle/templates/milestone.md`:
  - **Coarse grouping rule (`SHOULD`):** A milestone represents a multi-unit phase, release or architectural theme
    advancing `ARCH-01-introduction-and-goals`. Authors SHOULD NOT create a milestone for a single proposal or split
    a cohesive theme into separate milestones merely to express ordering between units; use unit `depends_on` for
    unit-to-unit sequencing.
  - **Exit condition abstraction (`SHOULD`):** Milestone `Exit condition` sections state observable phase-level
    outcomes and capability boundaries. Command-line flags, branch names, file layouts and scenario-level test cases
    belong in `proposal.md` and `spec.md`, not in the milestone document.

### Non-Goals

- **Scope Excluded**: Retroactively merging or deleting existing milestones under `docs/roadmap/` as part of this
  mechanism change (existing roadmap cleanup remains a separate user decision in Backlog).
- **Scope Excluded**: Cross-kind `depends_on` edges (such as a milestone depending on a proposal, or a proposal
  depending on a milestone via `depends_on` instead of `milestone`).

## 4. Lifecycle & Retirement Criteria

- Record a PADR superseding `ADR-milestone-documents` while retaining its unaffected decisions to allow `depends_on` on unit anchors (`PROP-`/`SPEC-`) alongside
  milestones and to define the coarse-milestone / unit-dependency split.
- Verify with unit tests in `packages/devkit-spec/tests/` covering `parse_document`, `RULE-document-reference`
  (valid `PROP-`/`SPEC-` targets, wrong-kind rejection, handoff rewrite, unit dependency cycles), proposal handoff
  carrying `depends_on`, and bundle contract tests for updated skill/template guidance.
- Run `just lint-check`, `just check`, `just rules-check`, and `just test-affected` before integration.

### Implementation constraints and acceptance evidence

- Dependency references remain normal indexed relationships. History-hidden completed SPEC targets must resolve;
  list/search presentation filters must not prevent resolving a direct target. Incoming repair covers live
  anchors only; historical references follow the existing historical-document policy.
- Handoff MUST validate the proposed post-handoff unit graph before its first write: replace the source PROP node
  with its SPEC node, carry outgoing edges, and rewrite incoming dependency targets in memory. Exclude the source
  PROP from this projected graph; do not allow an actually pre-existing same-slug SPEC collision. Invalid shape,
  missing/ambiguous/wrong-kind anchors or cycles refuse before mutation using the existing handoff advisory family
  and an actionable directive. Preserve normal rollback and do not redesign generic integration.
- Graph diagnostics retain `RULE-document-reference`; use deterministic traversal and report affected checked
  anchors. A changed anchor that completes a multi-node or mixed PROP/SPEC cycle must be reported even when other
  cycle nodes are outside the changed-path filter. Completed historical SPECs are terminal targets, not traversed for inherited prerequisites or cycles.
  Self-edges and cycles among live unit anchors remain invalid.
- Unit readiness is evaluated for every candidate from one base snapshot. Each blocked draft reports the exact
  prerequisite ID and its reason (unfinished proposal, unfinished spec, rejected proposal, or invalid/unknown
  target). No dependencies means unit-ready. A critical blocked draft stays blocked. Explicit user pickup can
  override order, with the unsatisfied IDs and reason recorded in the ordinary intent decision; it cannot waive
  malformed references or cycle diagnostics. Direct spec intake and explicit proposal pickup inspect the same
  fields; no new gate or hard readiness refusal is introduced.
- Coarse milestone guidance is advisory (`SHOULD`), not a minimum-member-count validator. A newly created theme
  can initially contain one unit when additional scope is not authored yet; it must describe a multi-unit outcome
  and cannot exist solely as a sequencing gate. Existing milestone transitions and readiness stay unchanged.
- Development acceptance scenarios cover omitted/empty/malformed lists, valid mixed targets, auxiliary-document
  targets, cross-kind targets, missing/ambiguous targets, self/two-node/mixed live cycles and terminal historical targets, and namespace-wide
  incoming references. Real isolated Git fixtures cover handoff carry/rewrite, projected-graph refusal without
  writes, same-slug collision, and base-completed versus branch-only-completed prerequisite states.
- Guidance fixtures cover ordinary and critical blocked drafts, existing milestone priority exceptions, explicit
  pickup override, direct spec intake, split/supersede/reject/session dispositions, and the one-initial-member
  theme exception. Lifecycle examples require no automatic lineage guessing or bulk roadmap changes.
- Development updates the document model, governance rule, proposal incubation, `CAP-DLV-spec-bundles`,
  Backlog/orientation contracts,
  the superseding ADR and the source bundle guidance/templates. Milestone membership queries and hygiene ignore SPEC anchors, and handoff omits milestone metadata.
  Tests verify direct PROP membership, absence of carried SPEC milestone, removal of direct-spec CLI/API
  milestone inputs (normal unknown-option rejection for the removed CLI flag), and ignored historical SPEC metadata.
  Existing roadmap edits are limited to README
  guidance; installed projections are regenerated through the repository's ordinary sync process, never edited.
  Development effort remains medium: the change extends existing relations and recommendation procedures without
  introducing an execution gate, branch scanner or completion evaluator.

The explicit product direction is a simple direct relationship model. Do not persist a milestone delivery graph,
expand prerequisites through `decomposed_from`/`supersedes`, continually repair completed history, or infer delivery
from disappearance of a proposal. The existing exact same-slug PROP-to-SPEC rewrite during handoff is retained
only as direct reference relocation for live documents; it does not imply completion. A stale direct reference
that cannot be repaired by this exact existing mapping is surfaced for user-assisted Backlog repair.
