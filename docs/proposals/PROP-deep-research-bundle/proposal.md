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
    - .devkit/architecture.toml
    - docs/capabilities/delivery/
    - docs/capabilities/harness/CAP-HARN-agent-guidance.md
    - docs/usecases/delivery/
    - docs/steering/glossary.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/architecture/ARCH-07-deployment.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/
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

Planning answers each question below; the evidence is `envelopes/scout-01.yaml` and `envelopes/challenger-01.yaml`.

- **Q1 Role ownership**: The research orchestration uses six roles: `direction-explorer`, `discovery-critic` and
  `discovery-planner` serve only the research entry; `product-clarifier`, `incubation-researcher` and
  `usage-reviewer` also serve `/incubate`. Bundles declare no dependency, and two selected bundles that ship the
  same skill or subagent ID fail sync with `BUNDLE_CONFLICT` before any write. **Answer (user, q1)**:
  `deep-research` is self-contained and designed without regard to adaptive development. It moves the three
  research-only roles with their IDs and adds its own `research-investigator`; the incubation bundle (`adaptive-dev`
  after `PROP-rename-incubation-to-adaptive-dev`) keeps `product-clarifier`, `incubation-researcher` (renamed
  `product-researcher` there) and `usage-reviewer`. No role is shared, and no bundle or package dependency exists in
  either direction. The research entry covers user and problem framing inline or through a `direction-explorer`
  premise, and usage evidence through a bounded investigator experiment.
  - The two researchers differ in scope: `research-investigator` answers one question of a team investigation; the
    incubation researcher gathers one product decision's evidence or runs one bounded experiment.
  - `/incubate` never invokes or suggests `/deep-research`; it only reads a retained material by its `MAT-<slug>` ID.
  - Deferred: layering through a Python package dependency plus `auto_select` (`CAP-DIST-content-packages`) works
    only across wheels, and both bundles ship in the opt-in `devkit-catalog` wheel (`PADR-split-deep-research-bundle`).
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
  creates a new material that cites it. Before creating a material, the coordinator checks that the MAT ID resolves
  to nothing and the directory is absent.
- **Q5 Workspace**: New runs use `.devkit/transient/deep-research/` with the existing verify-ignored-then-stop check.
  Old `.devkit/transient/incubation-research/` runs are left in place, never moved or deleted; the entry reads one
  only when the user names it as an input source.
- **Q6 Migration**: All catalog bundles share one version. After the upgrade, sync removes the unmodified
  projections of `incubate-research` and the three moved roles (`[CHANGE: remove <path>]`), keeps edited ones with
  `ORPHAN_LEFT`, and announces the unselected `deep-research` once with `BUNDLE_UNSELECTED`. A consumer selecting
  both bundles in one sync gets no conflict: the moved role paths change owner as updates. No distribution change;
  `INSTALL_GUIDE`, `existing-repository`, `bundle-recommendations` and the catalog README tell an incubation
  consumer that the entry now needs `uv run devkit add deep-research`, and name the manual step for each
  customization of a moved role: rename an `incubation:<role>` role-policy key to `deep-research:<role>` (sync fails
  until then), move `.devkit/overrides/incubation/subagents/<role>.md` to `.devkit/overrides/deep-research/subagents/`
  (it silently stops applying until then), and move or delete an edited projection left with `ORPHAN_LEFT` before
  `devkit add deep-research` (the add is refused until then).
- **Q7 Sequencing**: Host decision (q4), stated in §3.6.

## 3. Proposed Design & Impact

### 3.1 The `deep-research` bundle

- New catalog bundle `devkit_catalog/deep_research/bundle/` (entry point `deep-research`), preset `core` (default),
  never `auto_select`. `.devkit/architecture.toml` adds `deep_research` to the `devkit_catalog` package's `data_roots`. Assets: skill `deep-research` (`invocation = "user"`) with `references/orchestration.md`,
  `references/workspace.md` and `references/synthesis.md`; subagents `direction-explorer`, `discovery-critic`,
  `discovery-planner` (moved) and `research-investigator` (new). No guidance asset and no bundle constitution: the
  skill is self-contained (`PADR-split-deep-research-bundle`).
- The entry keeps the coordinator model, bounded assignments, independent alternatives, source provenance,
  optional criticism, initial synthesis, bounded partial results, useful alternatives, workspace allocation and
  selective promotion (`CAP-DLV-idea-incubation` rules 18 to 26).
- The entry drops the approach check, the `get-context incubation` read and every `.devkit/incubation.md` read or
  write. It never implements or publishes and creates no SDD Unit, approval or envelope. It writes only its
  transient run directory and the retained material, and reports their paths.
- The entry never commits (user, q3). Its report tells the user to commit the retained material through the
  project's Git policy, because a proposal's Planning worktree starts from committed history and resolves a
  `MAT-<slug>` citation only once the material is on the base.
- Under SDD, an explicit `/deep-research` invocation is not development intake: the spec entry does not classify it
  into a depth. The spec skill's intake rules, `UC-route-development-intent` (a new extension) and
  `CAP-HARN-agent-guidance`'s approach-aware SDD entry state this exemption; follow-up work the research informs
  starts as ordinary intake.
- The skill body opens with "Run only when the user explicitly invokes this entry; never suggest or start it
  otherwise" (Antigravity has no native explicit-only setting); the description carries no trigger phrasing.
- Role contracts replace "only the coordinator writes `.devkit/incubation.md`" with "only the coordinator writes the
  retained material"; the effective-contract path becomes `.devkit/managed/deep-research/subagents/`.
- Bundle text names no development approach value, so `PROP-rename-incubation-to-adaptive-dev` does not touch it.

### 3.2 Explicit invocation only

- No skill, guidance pointer, guide or role suggests the entry, also on a topic match. Removed: `CAP-DLV-idea-incubation`
  rule 17's suggestion clause and its §4 sentence on `/incubate`; `incubate-research/SKILL.md` lines 8 and 9 (gone
  with the move); `/incubate` procedure step 3's suggestion; `/incubate`'s `references/discovery.md` step 3;
  `UC-incubate-an-idea` extension 4b and its Scenario 8; the incubation pointer's research clause; the "for a broad
  investigation, explicitly select" sentences in `new-repository` and `existing-repository`; the research paragraph
  of the catalog README's incubation section.
- Guides describe `deep-research` only as an installable bundle. Its `bundle-recommendations` row reads "the user
  asks for an explicit research entry"; repository evidence alone never recommends it.

### 3.3 The remaining incubation bundle

- Keeps `/incubate`, `product-clarifier`, `incubation-researcher`, `usage-reviewer`, the pointer and the
  current-context template. `delegation.md` drops the research-only role line; `current-context.md` says to link a
  retained research material by its MAT ID. `AGENTS.md` and the pointer drop `/incubate-research`.

### 3.4 Living Spec

- New CAP-DLV-deep-research (new) holds the research contract: explicit selection, independent installation with or
  without devkit-spec, explicit invocation with no suggestion, no approach gate, the SDD intake exemption, bounded
  evidence (7), truthful verification (9), optional support (12), role boundaries (13), preservation of retained
  materials on sync, removal and re-selection (15), rules 18 to 23, 25 and 26, the retention, collision and
  citation contract, the role table for its four roles and the workspace path.
- `CAP-DLV-idea-incubation` keeps product iteration only: rules 17 to 23, 25 and 26 leave; rule 24 stays, reworded
  to link a research material by its MAT ID; rule 13's role table keeps three roles; §1 and §4 drop the research
  entry; `UC-research-an-idea-and-shape-a-roadmap` leaves its `usecases`.
- `UC-research-an-idea-and-shape-a-roadmap` keeps its ID and links CAP-DLV-deep-research (new): step 2 recovers goals
  without an approach check, extensions 2a and 2b are replaced by "2a SDD project: retained material is cited by a
  later proposal" and "2b adaptive project: current context links the material", and scenario 2 becomes
  "Run under either approach". Its Rules line drops approach inspection and adaptive clarification.
- `UC-route-development-intent` gains the extension for an explicitly invoked approach-neutral research entry.
- `UC-incubate-an-idea` drops extension 4b and Scenario 8. `CAP-HARN-agent-guidance` describes the two bundles
  separately. `ARCH-05-2-components` and `ARCH-07-deployment` name both catalog bundles and the new e2e test. The glossary registers **Deep research** (an explicitly
  invoked, approach-neutral investigation retained as one indexed material).
- On promotion, `PADR-split-deep-research-bundle` supersedes `ADR-extend-incubation-with-optional-discovery-teams`
  and `PADR-retain-research-as-cited-materials` supersedes
  `ADR-keep-discovery-plans-distinct-from-delivery-commitments`; each carries forward the parts it keeps.

### 3.5 Tests and packaging

- `pyproject.toml` gains the `deep-research` entry point; `tests/e2e/smoke.sh` adds it to the exact bundle set;
  the catalog README lists it.
- A new integration test module beside `test_incubation.py` moves `test_research_entry_projects_explicit_invocation_for_each_host`,
  checks the preset, the four roles' projections and coordinator ownership, the skill body guard, selection with
  `incubation:core` without `BUNDLE_CONFLICT`, and an `incubation:<moved-role>` role key failing while
  `deep-research:<role>` passes. Text checks: no incubation bundle file contains `incubate-research` or
  `deep-research`; guides and the catalog README mention `deep-research` only on lines with `devkit add deep-research`
  or the bundle table row; no deep-research bundle file contains `configuration.development.approach`,
  `.devkit/incubation.md` or `incubation`; the 12 KiB and no-document-ID checks stay. `test_incubation.py` drops the
  moved roles and the research skill.
- The installed-consumer e2e test for deep-research (an extension of the existing module, to avoid a second wheel
  build, is Development's choice) runs on docs and catalog without devkit-spec under the default
  `sdd` approach, allocates the workspace example under `.devkit/transient/deep-research/`, and checks that
  remove and re-add preserve a retained material.

### 3.6 Sequencing

Both drafts edit the incubation bundle, `CAP-DLV-idea-incubation`, the two use cases, the guides and the catalog
README. This split lands first (Host, q4): `PROP-rename-incubation-to-adaptive-dev` declares
`depends_on: [PROP-deep-research-bundle]`. This split's Development therefore uses the current `incubation` names for
the remaining bundle and documents. The rename then renames a bundle that no longer contains the research entry and
roles, and `deep-research` text names no approach value, so the rename touches none of it. No same-release
constraint applies, because no consumer uses the incubation bundle yet.

### Non-Goals

- No bundle-dependency, shared-role or moved-asset mechanism in devkit-dist.
- No new document kind, relation field or materials rule.
- No migration of old transient runs or of materials already retained by `/incubate-research`.
- No rename of the incubation bundle, approach, `/incubate` or `.devkit/incubation.md` (`PROP-rename-incubation-to-adaptive-dev`).

### Planning decisions

- User: explicit invocation only, with the suggestion wording removed; results under `docs/materials/`
  independent of approach and proposal; no approach gate and no `.devkit/incubation.md` dependency; the rename is
  a separate proposal.
- User (`envelopes/answer-01.yaml`): q1 a self-contained `deep-research` with no shared role and no dependency in
  either direction; q2 the entry name `/deep-research`; q3 the entry never commits and its report directs the
  commit through the project's Git policy.
- Host (`envelopes/answer-01.yaml`): q4 this split lands first; the rename depends on it.
- Planning: `PADR-split-deep-research-bundle` and `PADR-retain-research-as-cited-materials` record the design and
  supersede the two discovery ADRs; the SDD intake exemption, migration steps, explicit-only body guard, carried
  rules and collision check fold `envelopes/challenger-01.yaml`, and its finding 3 folds q3.
- Planning: `.devkit/architecture.toml` joins the boundaries for the new `deep_research` data root.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-deep-research-bundle`; the proposal is deleted there and its decisions become ADRs.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
