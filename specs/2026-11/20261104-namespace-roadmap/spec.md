---
id: SPEC-namespace-roadmap
title: Per-namespace milestones under the namespace docs root
summary: Lets a registered namespace keep its own MS milestones under docs/packages/<name>/roadmap/ with the global lifecycle and selection, so packages on their own cadence stop crowding the global roadmap.
status: planned
created: 2026-11-04
namespace: global
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-namespace-roadmap] Per-namespace milestones under the namespace docs root

## 1. Problem Statement & Motivation

Handed off from proposal PROP-namespace-roadmap on 2026-11-04.
- **Preserved Materials**: `docs/materials/2026-11/20261104-namespace-roadmap`

### 1. Background & Hypothesis

`CAP-DOCS-namespaces` mirrors `docs/` under `docs/packages/<name>/` for capabilities, use cases, UX and architecture
documents, but milestones are global only. `ADR-roadmap-and-milestones-ledger` §4 deferred per-namespace roadmaps
"until a repository needs them", and the code enforces the deferral: `milestone_path_valid` accepts only
`docs/roadmap/(_archive/)?MS-<slug>.md`, and `RULE-id-convention` walks every namespace `roadmap/` directory and
reports each file there as misplaced (`id_convention.py`, the `docs_root == "docs"` condition). The `MILESTONE` kind
row is `FormatScope.GLOBAL`, and the Backlog references state that milestones are global.

A monorepo whose packages are independent products now needs them: g-sandbox (`playground/g-sandbox`) holds four games
sharing one platform, each with its own release cadence and its own background under `docs/packages/<game>/`. Its
milestones would either crowd one global roadmap with unrelated themes or stay outside the document system.

Hypothesis: the namespace layer already supplies what per-namespace milestones need. Membership of a document under
`docs/packages/<name>/` is `<name>` (`CAP-DOCS-namespaces` 3.2), `devkit docs list` already selects namespaces, and
`living_path` already maps `docs/packages/<name>/roadmap/X` to `docs/roadmap/X` for the rules. Allowing the placement
and making the lifecycle checks namespace-aware is therefore a contained change; no new discovery command or ID scheme
is needed. This is the first direct member of `MS-monorepo-namespace-support`.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Per-namespace milestones under the namespace docs root so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which checks and commands hard-code the global roadmap root, and does each need the namespace root or only
  `living_path`?
  - *Finding* (`docs/materials/2026-11/20261104-namespace-roadmap/global-roadmap-root-inventory.md`): four code locations and none needs a new root
    parameter. `milestone_path_valid` stays as it is; its three callers validate the path mapped through
    `living_path(path, namespaces=registered)`: `RULE-id-convention` (which also drops the `docs_root == "docs"`
    condition and names both roots in its remediation), `RULE-spec-format` (whose `docs/roadmap/` prefix test guards the
    milestone status and `created_at` checks) and the proposal `--milestone` validation
    (`devkit_spec.features.proposals.usecases.roadmap.milestone_id`). The fourth is the kind table: the `MILESTONE`
    row's `FormatScope.GLOBAL` becomes `EVERY_ROOT`, so `RULE-spec-format` scans each namespace `roadmap/`. The
    document index already indexes `docs/packages/<name>/roadmap/` (discovery covers all of `docs/`), `historical`,
    the `depends_on` graph of `RULE-document-reference` and the `SPEC_MILESTONE_*_UNSETTLED` hygiene advisories are
    kind- and status-based, and `spec-next` already lists milestones with `--all-namespaces`: none of them changes.
    The local viewer's dashboard and roadmap tab read `docs/roadmap/` without the namespace registry
    (`CAP-VIEW-repository-viewer` 4.1 and §5), so until the viewer learns the namespace roots it not only omits namespace
    milestones: a global milestone whose `depends_on` names a namespace milestone renders as an unknown dependency and
    is never ready, and a proposal whose `milestone` names a namespace milestone appears in no roadmap card
    (challenger-01, finding 1). The viewer stays out of this proposal on the user's decision (answer-01, q1); the three
    effects are recorded as `FB-viewer-namespace-roadmap-roots` for follow-up work.
- **Q2**: Where does a namespace milestone cite its goal? `ADR-roadmap-and-milestones-ledger` keeps goals as prose in
  `ARCH-01-introduction-and-goals` and names "goals per namespace" as its own reopen condition.
  - *Finding*: as a global milestone does, in prose, citing `ARCH-01-introduction-and-goals` or an architecture
    document under its namespace docs root by ID (`CAP-DOCS-namespaces` mirrors `architecture/`, so a package can hold
    its own goals document today). A namespace steering file (`PROP-namespace-steering`) carries no ID, so it can only
    be named by path, once it exists; nothing in this proposal depends on it. The citation stays a recommendation
    (`ARCH-01-introduction-and-goals` "SHOULD cite"), checked in review only, as today, so goals stay prose without IDs and
    ADR-roadmap-in-repository is not reopened. The two proposals therefore need no shared Planning round and no
    `depends_on` edge; `PROP-namespace-steering` Q3 can take this finding as its answer.
- **Q3**: What does a cross-namespace milestone edge mean, and how does `devkit docs list milestone` behave without
  `--namespace` from a package directory?
  - *Finding*: `depends_on: [MS-<other>]` across namespaces resolves because IDs are repository-wide
    (`CAP-DOCS-namespaces` 3.3 rule 5) and the `RULE-document-reference` graph is built over every milestone
    document; the lifecycle rules (activate shows each dependency not done or dropped; close, drop, reopen, merge) need
    no namespace clause. Default selection follows 3.3 rule 3: from a package directory, that package's milestones plus
    the global ones; from the repository root, every namespace; `--namespace` and `--all-namespaces` as for the other
    kinds. Membership of a file under `docs/packages/<name>/roadmap/` is `<name>` by 3.2 rule 1 with no change.

### 3. Proposed Design & Impact

Decision record: `ADR-namespace-milestone-roots` (supersedes `ADR-roadmap-and-milestones-ledger` in part).

- **Placement**: a milestone of a registered namespace lives at `docs/packages/<name>/roadmap/MS-<slug>.md`
  (planned/active) or `docs/packages/<name>/roadmap/_archive/MS-<slug>.md` (done/dropped), the global layout under the
  namespace docs root. `milestone_path_valid` keeps its global regex; `RULE-id-convention`, `RULE-spec-format` and the
  proposal `--milestone` validation pass it the path mapped through `living_path` with the registered namespaces. An
  unregistered `docs/packages/<name>/` stays a plain `docs/` directory: its `roadmap/` files are still reported as
  misplaced, as its other documents are.
- **Format scope**: the `MILESTONE` kind row becomes `FormatScope.EVERY_ROOT`, so `RULE-spec-format` checks a
  namespace milestone's frontmatter (`id`, `title`, `status` in planned/active/done/dropped, `created_at`, English
  `summary`) as it checks a global one. The `PROPOSAL` row stays `GLOBAL`: proposal bundles keep one directory.
- **Identity and membership**: IDs, aliases and the `MS-` prefix stay repository-wide; a namespace milestone is a
  member of its namespace by path (3.2 rule 1), and a direct proposal of any namespace declares membership through
  `milestone` naming a milestone at either root. `devkit spec proposal new --milestone` accepts both; its
  `ARGUMENT_INVALID` message and fix name "a milestone at the global or a namespace roadmap root" and
  `devkit docs list milestone --all-namespaces`. `SPEC_PROPOSAL_MILESTONE_INACTIVE` is unchanged.
- **Selection and edges**: `devkit docs list milestone` and `search` follow `CAP-DOCS-namespaces` 3.3 without a
  milestone clause; milestone `depends_on` resolves across namespaces; the hygiene advisories read every milestone.
- **Guidance**: the roadmap README, `ARCH-01-introduction-and-goals` (Repository roadmap), the `spec` skill
  references (`backlog.md` Milestones, `roadmap-catalog.md`, `milestone-completion.md`), the milestone template and the
  `id_convention` and `spec_format` rule guides replace "milestones are global" and the literal `docs/roadmap/` of
  lifecycle moves with the two roots and "the milestone's roadmap root"; the `_archive/` move stays inside that root.
  The seeded introduction-and-goals architecture document of the `docs` bundle names the namespace root in its roadmap sentence.
- **Decision record**: handoff promotes `ADR-namespace-milestone-roots` to an ADR; Development writes one
  "Superseded in part by" line into `ADR-roadmap-and-milestones-ledger` naming both replaced clauses: "Milestones are
  global; per-namespace roadmaps are deferred until a repository needs them" (ADR-milestone-documents) and "live
  milestones remain at the global roadmap root `docs/roadmap/`" (ADR-archive-terminal-milestones-in-roadmap), as the
  PADR's Decision Outcome lists them (challenger-01, finding 2).
  `.devkit/managed/` copies are regenerated by `devkit generated regen`, never edited.
- **Tests**: `RULE-id-convention` fixtures with a registered namespace milestone at each lifecycle location (planned at
  the root, done in `_archive/`, a done file left at the root reported, a planned file in `_archive/` reported), an
  unregistered `docs/packages/<name>/roadmap/` file still reported, a namespace `_archive/` move; `RULE-spec-format`
  fixtures for a namespace milestone's status and `created_at`; `test_roadmap.py` with `proposal new --milestone`
  naming a namespace milestone from the repository root and from the package directory; a `devkit docs list
  milestone` test from a package directory and with `--all-namespaces`; the guidance test
  (`test_milestone_archive_guidance.py`) updated for the new wording.

Expected affected contracts: `CAP-DOCS-namespaces` (3.4 and the kinds a namespace mirrors), `CAP-GOV-spec-rules`
(`RULE-id-convention`, the `RULE-spec-format` scope list and the Milestone validation contract),
`CAP-DLV-proposal-planning` (`--milestone`), the roadmap section of `ARCH-01-introduction-and-goals`,
`ADR-roadmap-and-milestones-ledger` (superseded in part). `CAP-VIEW-repository-viewer` is unchanged (answer-01, q1).

#### Planning decisions

- Validation reuses `living_path` with the registered namespaces instead of a docs-root parameter on
  `milestone_path_valid`: the mapping exists, keeps unregistered directories misplaced and leaves the global function
  unchanged (Host decision within scope).
- A proposal may name a milestone of another namespace or the global root; no same-namespace constraint is added,
  since identity is repository-wide and a platform proposal may serve a package theme (Host decision within scope).
- The goal citation of a namespace milestone stays a review-only recommendation, as the global one is; no rule is
  added, and `PROP-namespace-steering` is neither a prerequisite nor planned jointly (Host decision within scope; Q2).
- `packages/devkit-viewer/` stays excluded and `CAP-VIEW-repository-viewer` unchanged on the user's decision (answer-01,
  q1): the viewer shows global milestones only and mis-renders cross-root edges until the follow-up
  `FB-viewer-namespace-roadmap-roots` is taken up; it would enumerate `docs/packages/*/roadmap(/_archive)/MS-*.md` by
  path pattern from the Git tree, since it reads no registry.
- Challenger round 1 (historical Git `dbaf8f3812a2a01cb2254ddf8418349aba0517ce:docs/proposals/PROP-namespace-roadmap/envelopes/challenger-01.yaml`): finding 2 (the two-clause supersession pointer) is folded in
  section 3 and closed in `reverify-01`; finding 1 (the viewer exclusion's cost) was the `Decision needed` behind q1,
  decided by the user in `answer-01` and closed in `reverify-02`.
- `boundaries.owns` gains the `docs` bundle (rule guides, tests, template, seed), both test trees and the governance
  and delivery capability directories the inventory names; `size` stays `M` (one spec, one task kind).
- `dev_effort` stays `medium`: two packages and five documents change, every change is covered by rule or command
  tests and nothing is irreversible.

### 4. Lifecycle & Retirement Criteria

Planning settled Q1 to Q3 above; acceptance and handoff create one feature spec. Completion requires the rule and
command tests above, synchronized references and a monorepo fixture in which `devkit rules check` reports no finding
for a namespace milestone at each lifecycle location and `devkit docs list milestone` from the package directory lists
it beside the global milestones.

Non-goals: namespaced IDs or per-package ID spaces; per-namespace goals as ID-bearing documents; a namespace copy of
`_archive/` semantics beyond the path; a rule that checks the goal citation; a namespace directory for proposals;
external tracker synchronization of namespace roadmaps.

