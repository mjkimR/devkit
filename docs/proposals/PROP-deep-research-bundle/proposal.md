---
id: PROP-deep-research-bundle
title: Split explicit deep research into an approach-neutral bundle
summary: "Move the explicitly invoked research entry and its research roles from the incubation bundle into an approach-neutral deep-research bundle. Results stay under docs/materials/ and proposals or current context reference them by ID, so one investigation can inform several proposals."
status: reviewing
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
    - docs/architecture/ARCH-05-2-components.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/proposals-catalog.md
    - tests/e2e/smoke.sh
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

Planning answers each question below; the evidence is `envelopes/scout-01.yaml` and the challenger round.

- **Q1 Role ownership**: The research orchestration uses six roles: `direction-explorer`, `discovery-critic` and
  `discovery-planner` serve only the research entry; `product-clarifier`, `incubation-researcher` and
  `usage-reviewer` also serve `/incubate`. Bundles declare no dependency, and two selected bundles that ship the
  same skill or subagent ID fail sync with `BUNDLE_CONFLICT` before any write. **Answer (recommended, open as q1)**:
  `deep-research` moves the three research-only roles with their IDs and adds its own `research-investigator`;
  the incubation bundle keeps its three shared roles. The research entry covers user and problem framing inline or
  through a `direction-explorer` premise, and usage evidence through a bounded investigator experiment.
- **Q2 Retention contract**: One indexed material per investigation:
  `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/<YYYYMMDD>-<slug>.md` with `id: MAT-<slug>`, linking the run's
  other notes by relative path. Consumers cite the index ID; a note carries its own ID only when cited alone.
  The layout and fields stay a convention: no rule checks materials (`PADR-retain-research-as-cited-materials`).
- **Q3 Consumers**: A proposal, spec or ADR cites the index ID in a code span, which `RULE-document-reference`
  resolves; bare text is no reference edge. Handoff moves only the proposal's own `materials/` and rewrites only IDs
  it wrote, so the citation survives unchanged. No check changes. The spec skill's proposal reference gains one
  line: research retained outside the proposal is cited by its MAT ID, never copied into `materials/`. Adaptive
  current context links the same ID (`/incubate`'s `current-context` reference).
- **Q4 Resume**: No approach-specific file. In-flight state lives in the transient run brief; once a result is
  retained, the index carries `Status: partial`, open questions and the next investigation. A resumed run of the
  same investigation, named by the user, updates that index; a complete material is not rewritten, and later research
  creates a new material that cites it.
- **Q5 Workspace**: New runs use `.devkit/transient/deep-research/` with the existing verify-ignored-then-stop check.
  Old `.devkit/transient/incubation-research/` runs are left in place, never moved or deleted; the entry reads one
  only when the user names it as an input source.
- **Q6 Migration**: All catalog bundles share one version. After the upgrade, sync removes the unmodified
  projections of `incubate-research` and the three moved roles (`[CHANGE: remove <path>]`), keeps edited ones with
  `ORPHAN_LEFT`, and announces the unselected `deep-research` once with `BUNDLE_UNSELECTED`. A consumer selecting
  both bundles in one sync gets no conflict: the moved role paths change owner as updates. No distribution change;
  `INSTALL_GUIDE`, `existing-repository` and `bundle-recommendations` tell an incubation consumer that the entry now
  needs `uv run devkit add deep-research`.
- **Q7 Sequencing**: Host decision, stated in §3.6.

## 3. Proposed Design & Impact

### 3.1 The `deep-research` bundle

- New catalog bundle `devkit_catalog/deep_research/bundle/` (entry point `deep-research`), preset `core` (default),
  never `auto_select`. Assets: skill `deep-research` (`invocation = "user"`) with `references/orchestration.md`,
  `references/workspace.md` and `references/synthesis.md`; subagents `direction-explorer`, `discovery-critic`,
  `discovery-planner` (moved) and `research-investigator` (new). No guidance asset and no bundle constitution: the
  skill is self-contained (`PADR-split-deep-research-bundle`).
- The entry keeps the coordinator model, bounded assignments, independent alternatives, source provenance,
  optional criticism, initial synthesis, bounded partial results, useful alternatives, workspace allocation and
  selective promotion (`CAP-DLV-idea-incubation` rules 18 to 26).
- The entry drops the approach check, the `get-context incubation` read and every `.devkit/incubation.md` read or
  write. It never implements, publishes or commits, and creates no SDD Unit, classification, approval or envelope.
  It writes only its transient run directory and the retained material, and reports their paths.
- Role contracts replace "only the coordinator writes `.devkit/incubation.md`" with "only the coordinator writes the
  retained material"; the effective-contract path becomes `.devkit/managed/deep-research/subagents/`.
- Bundle text names no development approach value, so `PROP-rename-incubation-to-adaptive-dev` does not touch it.

### 3.2 Explicit invocation only

- No skill, guidance pointer, guide or role suggests the entry, also on a topic match. Removed: `CAP-DLV-idea-incubation`
  rule 17's suggestion clause and its §4 sentence on `/incubate`; `incubate-research/SKILL.md` line 9 (gone with the
  move); `/incubate` procedure step 3's suggestion; `UC-incubate-an-idea` extension 4b; the incubation pointer's
  research clause; the "for a broad investigation, explicitly select" sentences in `new-repository` and
  `existing-repository`.
- Guides describe `deep-research` only as an installable bundle. Its `bundle-recommendations` row reads "the user
  asks for an explicit research entry"; repository evidence alone never recommends it.

### 3.3 The remaining incubation bundle

- Keeps `/incubate`, `product-clarifier`, `incubation-researcher`, `usage-reviewer`, the pointer and the
  current-context template. `delegation.md` drops the research-only role line; `current-context.md` says to link a
  retained research material by its MAT ID. `AGENTS.md` and the pointer drop `/incubate-research`.

### 3.4 Living Spec

- New CAP-DLV-deep-research (new) holds the research contract: explicit selection, independent installation with or
  without devkit-spec, explicit invocation with no suggestion, no approach gate, rules 18 to 26, the retention and
  citation contract, the role table for its four roles and the workspace path.
- `CAP-DLV-idea-incubation` keeps product iteration only: rules 17 to 26 leave, rule 13's role table keeps three
  roles, §1 and §4 drop the research entry, and `UC-research-an-idea-and-shape-a-roadmap` leaves its `usecases`.
- `UC-research-an-idea-and-shape-a-roadmap` keeps its ID and links CAP-DLV-deep-research (new): step 2 recovers goals
  without an approach check, extensions 2a and 2b are replaced by "2a SDD project: retained material is cited by a
  later proposal" and "2b adaptive project: current context links the material", and scenario 2 becomes
  "Run under either approach".
- `UC-incubate-an-idea` drops extension 4b. `CAP-HARN-agent-guidance` describes the two bundles separately.
  `ARCH-05-2-components` names both catalog bundles. The glossary registers **Deep research** (an explicitly
  invoked, approach-neutral investigation retained as one indexed material).
- `ADR-extend-incubation-with-optional-discovery-teams` is superseded on promotion by
  `PADR-split-deep-research-bundle`; `ADR-keep-discovery-plans-distinct-from-delivery-commitments` stays.

### 3.5 Tests and packaging

- `pyproject.toml` gains the `deep-research` entry point; `tests/e2e/smoke.sh` adds it to the exact bundle set;
  the catalog README lists it.
- A new integration test module beside `test_incubation.py` moves `test_research_entry_projects_explicit_invocation_for_each_host`,
  checks the preset, the four roles' projections and coordinator ownership, selection with `incubation:core`
  without `BUNDLE_CONFLICT`, and that no incubation asset and no guide names `/deep-research` except as a bundle to
  select. `test_incubation.py` drops the moved roles and the research skill.
- The installed-consumer e2e test for deep-research runs on docs and catalog without devkit-spec under the default
  `sdd` approach, allocates the workspace example under `.devkit/transient/deep-research/`, and checks that
  remove and re-add preserve a retained material.

### 3.6 Sequencing (open for the Host)

Both drafts edit the incubation bundle, `CAP-DLV-idea-incubation`, the two use cases, the guides and the catalog
README. Recommended: land this split first. The rename then renames a bundle that no longer contains the research
entry and roles, and `deep-research` text names no approach value, so the rename touches none of it. If the rename
lands first, this split's edits to the remaining bundle and documents use the `adaptive-dev` names and its
Development starts from the renamed base; the design is otherwise unchanged.

### Non-Goals

- No bundle-dependency, shared-role or moved-asset mechanism in devkit-dist.
- No new document kind, relation field or materials rule.
- No migration of old transient runs or of materials already retained by `/incubate-research`.
- No rename of the incubation bundle, approach, `/incubate` or `.devkit/incubation.md` (`PROP-rename-incubation-to-adaptive-dev`).

### Planning decisions

- User: explicit invocation only, with the suggestion wording removed; results under `docs/materials/`
  independent of approach and proposal; no approach gate and no `.devkit/incubation.md` dependency; the rename is
  a separate proposal.
- Planning: `PADR-split-deep-research-bundle` and `PADR-retain-research-as-cited-materials` record the design;
  q1 and q2 in the worker envelope confirm the role split and the entry name.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-deep-research-bundle`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
