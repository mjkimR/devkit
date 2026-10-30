---
id: SPEC-deep-research-bundle
title: Split explicit deep research into an approach-neutral bundle
summary: Move the explicitly invoked research entry and its research roles from the incubation bundle into an approach-neutral deep-research bundle. Results stay under docs/materials/ and proposals or current context reference them by ID, so one investigation can inform several proposals.
status: planned
created: 2026-10-30
related_capabilities:
  - CAP-DLV-idea-incubation
  - CAP-HARN-agent-guidance
related_usecases:
  - UC-research-an-idea-and-shape-a-roadmap
  - UC-incubate-an-idea
  - UC-route-development-intent
workflow: sdd-spec-feature
---

# [SPEC-deep-research-bundle] Split explicit deep research into an approach-neutral bundle

## 1. Problem Statement & Motivation

Handed off from proposal PROP-deep-research-bundle (accepted at historical Git
`f3aeae93339e0a72011811c087bf9c04bc5049fa:docs/proposals/PROP-deep-research-bundle/proposal.md`). The decisions are
`ADR-split-deep-research-bundle` and `ADR-retain-research-as-cited-materials`.

`/incubate-research` runs a bounded research team that compares directions and retains initial documents and a
conditional roadmap (`CAP-DLV-idea-incubation`, `UC-research-an-idea-and-shape-a-roadmap`). It ships in the
`incubation` catalog bundle and stops unless the effective development approach is `incubation`, and it writes
resume facts to `.devkit/incubation.md`, which an SDD repository does not keep. A repository under SDD therefore
cannot run a broad investigation before drafting proposals; switching `[development] approach` for one
investigation is no workaround, because the setting is shared and installed spec extensions refuse new SDD
lifecycle records while it is `incubation` (`CAP-DLV-project-policy`).

Research implements nothing and creates no SDD Unit, so it needs no approach gate. One broad investigation can
inform several proposals, so no single proposal should own its results.

Settled direction (user):

- The entry `/deep-research` runs only on explicit user invocation (`invocation = "user"`). No skill, pointer,
  guide or role suggests it, also on a topic match; the existing suggestion wording is removed.
- `deep-research` is self-contained: it moves `direction-explorer`, `discovery-critic` and `discovery-planner` with
  their IDs and adds its own `research-investigator`. No role is shared and no bundle or package dependency exists
  in either direction.
- Results are retained as one indexed material under `docs/materials/`, cited by `MAT-<slug>`, independent of the
  approach and of any single proposal.
- The entry has no approach gate and never reads or writes `.devkit/incubation.md`.
- The entry never commits; its report directs the commit through the project's Git policy.

## 2. User Stories

- **US-1**: As a developer in an SDD repository, I want to run an explicitly invoked research team without
  switching the shared development approach, so that I can investigate a direction before drafting proposals.
- **US-2**: As a proposal author, I want each investigation retained as one indexed material that I cite by its
  `MAT-<slug>` ID, so that several proposals or an adaptive product use one source without copying it.
- **US-3**: As an incubation consumer, I want the incubation bundle to keep `/incubate` and its three support
  roles, and the guides to tell me how to add the research entry and move my customizations, so that the split
  breaks no existing work silently.

## 3. Non-Goals

1. **Scope Excluded**: no bundle-dependency, shared-role or moved-asset mechanism in devkit-dist; the split uses
   existing sync behavior.
2. **Scope Excluded**: no new document kind, relation field or materials rule; the retention layout stays a
   convention (`ADR-retain-research-as-cited-materials`).
3. **Scope Excluded**: no migration of old `.devkit/transient/incubation-research/` runs or of materials already
   retained by `/incubate-research`.
4. **Scope Excluded**: no rename of the incubation bundle, approach, `/incubate`, `incubation-researcher` or
   `.devkit/incubation.md`; `PROP-rename-incubation-to-adaptive-dev` owns that and depends on this spec.
5. **Scope Excluded**: no handbook edit; the release handbook procedure (`CAP-DLV-release-handbook`) refreshes it at
   release.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The deep-research bundle deploys only on explicit selection

- **Given** devkit-catalog registers the entry point `deep-research = "devkit_catalog.deep_research"` and a project
  selects no catalog bundle
- **When** `devkit sync` runs, and then again after `deep-research:core` is selected
- **Then** the first sync writes no `.devkit/managed/deep-research/`; the bundle declares `default_preset = "core"`
  and no `auto_select`; after selection the managed directory holds exactly `bundle.toml`, the `deep-research`
  skill with `references/orchestration.md`, `references/workspace.md` and `references/synthesis.md`, and the
  subagent contracts `direction-explorer`, `discovery-critic`, `discovery-planner` and `research-investigator`,
  each projected to Codex, Claude Code and Antigravity; no `docs/`, `specs/` or `.devkit/incubation.md` is seeded

### [AC-02] The entry is explicit-only on every host

- **Given** `deep-research:core` is selected for `codex`, `claude-code` and `antigravity`
- **When** sync projects the skill
- **Then** the Codex `agents/openai.yaml` sets `policy.allow_implicit_invocation: false`, the Claude Code frontmatter
  sets `disable-model-invocation: true`, the skill body's first line after the H1 is "Run only when the user
  explicitly invokes this entry; never suggest or start it otherwise.", and the skill `description` contains none
  of the words `use`, `when`, `suggest` or `trigger`

### [AC-03] Bundle text is approach-neutral and self-contained

- **Given** the files of `devkit_catalog/deep_research/bundle/`
- **When** the integration test reads them
- **Then** no file contains `configuration.development.approach`, `.devkit/incubation.md` or `incubation`; no file
  contains a Living Spec document ID; each is at most 12288 bytes; every reference file is named by the skill on a
  line that says `before` or `when`

### [AC-04] Both catalog bundles select together without conflict

- **Given** both `incubation:core` and `deep-research:core` are selected
- **When** `devkit sync` runs
- **Then** it completes without `BUNDLE_CONFLICT`; `direction-explorer`, `discovery-critic` and `discovery-planner`
  are managed under `.devkit/managed/deep-research/subagents/` and absent from `.devkit/managed/incubation/`; the
  incubation preset holds exactly `incubate`, `incubation-pointer`, `product-clarifier`, `incubation-researcher`,
  `usage-reviewer` and `current-context-template`

### [AC-05] A moved role's policy key follows the bundle

- **Given** both bundles are selected and `.devkit/config.toml` sets `[subagents.roles."incubation:<role>"]` for a
  moved role
- **When** `devkit sync` runs
- **Then** it raises `ConfigError` naming `subagents.roles.incubation:<role>` and leaves the owned files unchanged;
  the same key as `deep-research:<role>` syncs successfully

### [AC-06] Role contracts keep coordinator ownership of the retained material

- **Given** the four deep-research role contracts
- **When** they are read as subagent contracts of bundle `deep-research`
- **Then** each states that only the coordinator writes the retained material, that the index and HEAD stay
  unchanged, and that its return carries `status`, source/artifact identity and failure conditions; Codex is
  `emulated` with `sandbox_mode: workspace-write`; `research-investigator` answers one question per instance and
  writes an experiment only inside its assigned scratch boundary; the orchestration reference names the effective
  contracts under `.devkit/managed/deep-research/subagents/`

### [AC-07] Retention contract: one indexed material cited by ID, never committed by the entry

- **Given** the skill and its `synthesis` and `workspace` references
- **When** the integration test reads them
- **Then** they state: one material per investigation at `docs/materials/<YYYY-MM>/<YYYYMMDD>-<slug>/` with index
  `<YYYYMMDD>-<slug>.md` carrying `id: MAT-<slug>`; a `Status` line of `complete` or `partial`; the collision check
  that `devkit docs resolve MAT-<slug>` finds nothing and the directory is absent; a resumed run named by the user
  updates only a `partial` index; consumers cite the ID in a code span; the run directory under
  `.devkit/transient/deep-research/`; and that the entry never commits, its report telling the user to commit the
  material through the project's Git policy

### [AC-08] The entry runs in an installed SDD consumer without devkit-spec

- **Given** built wheels of devkit-docs, devkit-catalog and their dependencies installed without devkit-spec, in a
  Git consumer with the default approach
- **When** the consumer runs `devkit add deep-research`, the skill's workspace example twice, writes a retained
  material, runs `devkit rules check`, `devkit remove deep-research` and `devkit add deep-research`
- **Then** `devkit config show` reports approach `sdd`; the skill and four roles are projected; each allocation is a
  distinct ignored, untracked directory under `.devkit/transient/deep-research/`; `rules check` exits 0; removal
  deletes the projected skill; the retained material is byte-identical after remove and re-add; `sync --check`
  exits 0

### [AC-09] Nothing suggests the entry

- **Given** the incubation bundle, `guides/` and the catalog README
- **When** the integration tests read them
- **Then** no incubation bundle file contains `incubate-research` or `deep-research`; `/incubate`'s procedure and
  `references/discovery.md` suggest no research entry; every line of `guides/**/*.md` and the catalog README that
  contains `deep-research` contains `devkit add deep-research`, is the bundle table row starting with
  ``| `deep-research` ``, or names a moved-role migration path (`deep-research:<role>` or
  `.devkit/overrides/deep-research/`)

### [AC-10] SDD intake exempts the explicit research entry and the proposal reference cites materials by ID

- **Given** the spec skill and its proposal reference
- **When** an agent reads the intake definition and the `materials/` rule
- **Then** the intake step states that an explicit `/deep-research` invocation is not intake and gets no playbook
  discovery, classification or Unit, and that work the research later informs starts as ordinary intake; the
  proposal reference states that research retained outside the proposal is cited by its `MAT-<slug>` ID in a code
  span and never copied into `materials/`

### [AC-11] Migration guidance names the add command and the three manual steps

- **Given** `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`,
  `guides/install/bundle-recommendations.md` and the catalog README
- **When** an incubation consumer upgrades devkit-catalog
- **Then** they name `uv run devkit add deep-research` for the research entry; `INSTALL_GUIDE`,
  `existing-repository` and the README also name renaming an `incubation:<role>` role-policy key to
  `deep-research:<role>`, moving `.devkit/overrides/incubation/subagents/<role>.md` to
  `.devkit/overrides/deep-research/subagents/`, and moving or deleting an edited projection left with
  `ORPHAN_LEFT` before `devkit add deep-research`; the recommendation row's signal is "the user asks for an explicit
  research entry"

### [AC-12] The consumer smoke test sees the new bundle

- **Given** `just smoke` installs the built wheels into a scratch consumer
- **When** it lists the catalog bundles and runs the default sync
- **Then** the catalog bundle set is exactly `response-style`, `maintenance`, `cli-tool`, `incubation` and
  `deep-research`, and `.devkit/managed/deep-research` does not exist

## 5. Design

The bundle and its assets follow `ADR-split-deep-research-bundle`; the retained material follows
`ADR-retain-research-as-cited-materials`.

- **Bundle**: `devkit_catalog/deep_research/bundle/`, entry point `deep-research`, preset `core` (default), version
  equal to the catalog package. `.devkit/architecture.toml` adds `deep_research` to the catalog `data_roots`. No
  guidance asset and no bundle constitution: the skill is self-contained.
- **Entry**: keeps the coordinator model, bounded assignments, independent alternatives, source provenance,
  optional criticism, initial synthesis, bounded partial results, workspace allocation and selective promotion. It
  drops the approach check, the incubation context read and every `.devkit/incubation.md` read or write. It writes
  only its transient run directory and the retained material and reports their paths; it never implements,
  publishes or commits and creates no Unit, approval or envelope.
- **Roles**: the three moved contracts replace "only the coordinator writes `.devkit/incubation.md`" with "only the
  coordinator writes the retained material"; `research-investigator` is derived from `incubation-researcher` but
  answers one question of a team investigation. User and problem framing stays inline or in a
  `direction-explorer` premise; usage evidence comes from a bounded investigator experiment.
- **Resume**: in-flight state lives in the transient run brief; a retained `partial` index carries open questions
  and the next investigation. An earlier run directory (including an old incubation research run) is read only when
  the user names it as an input source.
- **Remaining incubation bundle**: keeps `/incubate`, its three roles, the pointer and the current-context
  template; drops the research entry, its references and the three moved roles; `delegation.md` drops the
  research-only role line; `current-context.md` links a retained research material by its MAT ID; the pointer and
  `AGENTS.md` drop the research entry; `/incubate` step 3 and `references/discovery.md` step 3 drop the suggestion.
- **Migration**: sync removes unmodified projections of the removed assets, keeps edited ones with `ORPHAN_LEFT`
  and announces the unselected bundle with `BUNDLE_UNSELECTED`; guides name the add command and the three manual
  steps of AC-11.
- **Sequencing**: this split lands before `PROP-rename-incubation-to-adaptive-dev`, so the remaining bundle and
  documents keep their `incubation` names.

## 6. Assumptions

- The installed-consumer test for deep-research is a new module `tests/e2e/bundles/deep_research/` rather than an
  extension of the incubation module: it mirrors bundle ownership and keeps each module self-contained, at the cost
  of one more wheel build in the e2e tier.
- AC-09 admits the moved-role migration paths besides the two contexts the proposal named, because AC-11 requires
  the guides to name `deep-research:<role>` and `.devkit/overrides/deep-research/` and neither suggests the entry.
- `incubation-researcher`'s scratch clause, which named "the research run" of the removed entry, now names a task
  scratch directory the payload assigns; its scope is otherwise unchanged.
- The catalog package version stays `0.1.5`; a release bumps it.
