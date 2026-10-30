---
id: PROP-deep-research-bundle
title: Split explicit deep research into an approach-neutral bundle
summary: "Move the explicitly invoked research entry and its research roles from the incubation bundle into an approach-neutral deep-research bundle. Results stay under docs/materials/ and proposals or current context reference them by ID, so one investigation can inform several proposals."
status: draft
created_at: 2026-10-30
target_area: capabilities/delivery/
priority: high
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/
    - packages/devkit-catalog/tests/
    - packages/devkit-catalog/README.md
    - packages/devkit-catalog/pyproject.toml
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/delivery/
    - docs/steering/glossary.md
    - guides/
  excludes:
    - .devkit/managed/
    - handbook/
    - specs/
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-deep-research-bundle] Split explicit deep research into an approach-neutral bundle

## 1. Background & Hypothesis

`/incubate-research` runs a bounded research team that compares directions and retains initial documents and a
conditional roadmap (`CAP-DLV-idea-incubation`, `UC-research-an-idea-and-shape-a-roadmap`). It ships in the
`incubation` catalog bundle and stops unless the effective development approach is `incubation`:

- `incubate-research/SKILL.md` Constraints and `CAP-DLV-idea-incubation` rule 4 stop product actions under SDD.
- The research entry writes resume facts to `.devkit/incubation.md`, which an SDD repository does not keep.

A repository under SDD therefore cannot run a broad investigation before drafting proposals. Switching
`[development] approach` for the research is not a workaround: the setting is shared, and installed spec
extensions refuse new SDD lifecycle records while it is `incubation` (`CAP-DLV-project-policy`).

Research itself implements nothing and creates no SDD Unit, so it needs no approach gate. One broad
investigation can also inform several proposals, so no single proposal should own its results.

The hypothesis: an approach-neutral `deep-research` bundle with one explicit entry, its research roles and a
retention contract under `docs/materials/` serves SDD and adaptive development alike. Proposals and current
context reference the retained material by ID instead of copying it into a proposal's `materials/`.

### Settled direction

- The entry runs only on explicit user invocation (`invocation = "user"`). No skill, pointer or guidance suggests
  it, including on a topic match. The existing suggestion wording is removed:
  - `CAP-DLV-idea-incubation` rule 17 ("a topic match permits a suggestion") and its §4 sentence on `/incubate`.
  - `incubate-research/SKILL.md` ("suggest this entry and wait for that selection").
  - `/incubate` procedure step 3 and `UC-incubate-an-idea` extension 4b.
- Results are retained under `docs/materials/`, independent of the approach and of any single proposal.
- Research never implements, publishes or creates SDD Units, approvals or envelopes.
- `PROP-rename-incubation-to-adaptive-dev` renames the remaining incubation bundle and approach to `adaptive-dev`.
  This proposal owns the split, not the rename.

## 2. Technical Spike Questions

- **Q1 Role ownership**: `direction-explorer`, `discovery-critic` and `discovery-planner` serve only the research
  entry, while `incubation-researcher` also serves `/incubate` (`incubate/references/delegation.md` §2). Bundles
  declare no dependency on another bundle. Which bundle owns the shared researcher, and how does `/incubate`
  delegate when `deep-research` is not selected: a separate role copy, a conditional delegation, or inline work?
- **Q2 Retention contract**: Which identity does retained research carry (indexed `MAT-<slug>` under
  `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/`), and what does a consumer cite: the run's index document, or
  individual notes?
- **Q3 Consumers**: How does an SDD proposal reference retained research without its handoff moving or rewriting
  it (`devkit spec proposal handoff` moves only the proposal's own `materials/`)? Does any spec skill, rule or
  check need a change, or does the existing ID reference model already cover it?
- **Q4 Resume**: What replaces the `.devkit/incubation.md` write for an interrupted run under SDD: a resume section
  in the retained index document, or the transient run brief only?
- **Q5 Workspace**: Does `.devkit/transient/incubation-research/` move to a neutral path, and how do existing
  scratch runs remain readable?
- **Q6 Migration**: A consumer with `incubation:core` loses `/incubate-research` from that bundle. What does
  `devkit sync` report, and what do the guides tell the consumer to select?
- **Q7 Sequencing**: Both drafts edit the incubation bundle and `CAP-DLV-idea-incubation`. Which lands first in
  Development?

## 3. Proposed Design & Impact

- A new `deep-research` catalog bundle owns the research entry (renamed from `incubate-research`), its
  `orchestration`, `workspace` and `synthesis` references and the research-only roles.
- The entry drops the approach gate and the `.devkit/incubation.md` write. It keeps the coordinator model,
  bounded assignments, source provenance and selective promotion from `CAP-DLV-idea-incubation` rules 18 to 26.
- A new or split capability under `docs/capabilities/delivery/` holds the research contract;
  `CAP-DLV-idea-incubation` keeps product iteration only.
- `UC-research-an-idea-and-shape-a-roadmap` becomes approach-neutral, with extensions for an SDD consumer and an
  adaptive-development consumer.
- Install guides and bundle recommendations list `deep-research` as its own opt-in bundle.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-deep-research-bundle`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
