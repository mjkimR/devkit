---
id: PROP-unit-dependencies-and-milestone-scope
title: Unit-level depends_on and coarse milestone scope
summary: "Allows proposal and spec anchors to declare depends_on prerequisites across units and defines milestone authoring guidance so milestones remain multi-unit themes rather than single-proposal gates."
status: reviewing
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
2. Defining explicit milestone sizing and abstraction rules in the Backlog guidance and milestone template prevents
   single-proposal milestones and keeps detailed CLI/implementation contracts inside proposals and specs.

## 2. Technical Spike Questions

- **Q1 — Prerequisite lifecycle across handoff, decomposition and retirement:** When `PROP-<dependent>` declares
  `depends_on: [PROP-<prerequisite>]` and `PROP-<prerequisite>` is handed off to `SPEC-<prerequisite>`, reference
  rewriting updates the target to `SPEC-<prerequisite>`, which remains unsettled until `SPEC-<prerequisite>` reaches
  `status: completed`. How should `RULE-document-reference`, Backlog procedures and `spec-next` handle a prerequisite
  proposal that is decomposed (`decomposed_from`), superseded (`supersedes`), reclassified to a `session` task, or
  rejected (`status: rejected`)?
- **Q2 — Reference validation and cycle detection:** Should unit `depends_on` allow only unit anchor IDs (`PROP-`
  and `SPEC-`) while milestone `depends_on` keeps allowing only `MS-` IDs? Confirm cycle detection across mixed
  `PROP-`/`SPEC-` edges (including a slug pair during handoff preflight) and whether `devkit spec proposal new` /
  `devkit spec new` should expose a `--depends-on` CLI option or keep it as frontmatter/Backlog authoring.
- **Q3 — Readiness and `spec-next` ordering:** How should `spec-next` evaluate unit-level `depends_on` when
  selecting eligible drafts? Specifically, a prerequisite `PROP-` or an incomplete `SPEC-` (including one active on
  a `plan-` or `dev-` branch) is not yet settled; only a `SPEC-` with `status: completed` on the base satisfies the
  prerequisite without user override. Confirm how blocked drafts are reported alongside unready milestone drafts.
- **Q4 — Interaction with `PROP-deterministic-milestone-completion`:** How does unit-level `depends_on` interact with
  milestone outcome coverage and settlement evaluation so the two proposals remain orthogonal without duplicating
  lineage rules?

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
  completed spec (`SPEC-<slug>` with `status: completed` on the base). A referenced `PROP-<slug>` or an incomplete
  `SPEC-<slug>` means the prerequisite is still unsettled. As with milestone `depends_on`, ordering is a start
  condition enforced at decision/recommendation points rather than a hard refusal if the user explicitly chooses to
  start out of order.
- **`spec-next` selection (`next-work.md`):** An eligible draft must have both a ready milestone (when `milestone` is
  set) and satisfied unit `depends_on` prerequisites. Drafts whose unit `depends_on` includes unsettled work (or
  invalid/rejected/missing targets) are reported separately as blocked or Backlog actions rather than recommended for
  immediate pickup.
- **Backlog lifecycle (`backlog.md`):** When decomposing, superseding, reclassifying to `session`, or rejecting a
  proposal that other units list in `depends_on`, Backlog inspects incoming `depends_on` references (`devkit spec refs
  PROP-<slug> --direction in`) and updates or clears them in the same commit with the user's decision.

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

- Record a PADR updating `ADR-milestone-documents` to allow `depends_on` on unit anchors (`PROP-`/`SPEC-`) alongside
  milestones and to define the coarse-milestone / unit-dependency split.
- Verify with unit tests in `packages/devkit-spec/tests/` covering `parse_document`, `RULE-document-reference`
  (valid `PROP-`/`SPEC-` targets, wrong-kind rejection, handoff rewrite, unit dependency cycles), proposal handoff
  carrying `depends_on`, and bundle contract tests for updated skill/template guidance.
- Run `just lint-check`, `just check`, `just rules-check`, and `just test-affected` before integration.
