---
id: UC-adopt-in-an-existing-repository
title: Adopt Spec-Driven Delivery in an Existing Repository
summary: "A developer installs devkit-spec into a repository that already has code and documentation, gets the spec bundle and the devkit spec commands through devkit sync, and brings the spec rules to a passing baseline without rewriting legacy documents first."
area: harness
primary_actor: Developer maintaining a consumer repository
supporting_actors:
  - AI coding agent running the brownfield-adoption playbook
status: active
created_at: 2026-10-13
capabilities:
  - CAP-HARN-agent-guidance
  - CAP-GOV-spec-rules
  - CAP-HARN-command-mount
  - CAP-DLV-sdd-baseline-adoption
---

# [UC-adopt-in-an-existing-repository] Adopt Spec-Driven Delivery in an Existing Repository

## 1. Goal

- **Goal**: install devkit-spec, have every agent session pick up spec-driven delivery, and get `devkit rules check`
  passing before legacy content is migrated, so that new work follows the Living Spec immediately while legacy
  documents move over through normal work instead of a big-bang rewrite
- **Scope**: the devkit-spec package: its `spec` bundle deployed by `devkit sync`, its `devkit spec` commands mounted
  in devkit's executable, its spec rules and its `brownfield-adoption` playbook
- **Path distinction**: This path contains legacy rule debt and permits gradual migration. An explicit adaptive-dev
  baseline request instead follows `UC-adopt-sdd-from-adaptive-development`, which verifies retained product evidence before
  activating SDD and does not automatically contain or move legacy documents.
- **Trigger**: the developer decides to adopt spec-driven delivery in a repository with existing code, docs and agent
  instructions
- **Preconditions**: the repository is managed with `uv` and devkit; its current state is committed as a rollback
  point

---

## 2. Main Success Scenario

1. The developer adds devkit and devkit-spec to the project's development dependencies; the package registers the
   `spec` bundle and the `devkit spec` command group through entry points (`CAP-HARN-command-mount`).
2. The developer synchronizes the project; the system deploys the `spec` bundle's `core` preset to
   `.devkit/managed/spec/`, projects its skills and role contracts into each agent host and adds the guidance pointer
   line to the root `AGENTS.md` block, writing nothing under `docs/` or `specs/` (`CAP-HARN-agent-guidance`).
3. The developer confirms that the `devkit spec` commands answer through the project's `devkit` executable with the
   installed devkit-spec version (`CAP-HARN-command-mount`).
4. The developer runs the rules; the spec rules check the Markdown already under `docs/` and `specs/` and report
   violations in the legacy files (`CAP-GOV-spec-rules`).
5. The developer asks the agent for the `brownfield-adoption` playbook, or confirms the one-line offer `spec` intake
   makes for a request to adopt devkit here (`CAP-HARN-agent-guidance`).
6. The agent moves the legacy Markdown under `docs/materials/_legacy/`, which the spec rules leave free-form, without
   editing any rule (`CAP-HARN-agent-guidance`, `CAP-GOV-spec-rules`).
7. The agent reruns the rules; the check passes (`CAP-GOV-spec-rules`).
8. Later agent sessions read the constitution through the guidance pointer, route new work through the `spec` skill
   and migrate legacy content as work touches it (`CAP-HARN-agent-guidance`).

---

## 3. Extensions

- **1a.** The developer explicitly requests an adaptive-dev baseline before activation: the agent follows
  `UC-adopt-sdd-from-adaptive-development` (`CAP-DLV-sdd-baseline-adoption`); this legacy-containment use case ends without
  automatic moves or a claim that asset installation establishes baseline readiness.

- **2a.** The project opts out of the bundle in its preset selection: the system deploys none of the `spec` bundle's
  managed files or projections, while the `devkit spec` commands stay mounted through their entry point; the use case
  ends after step 3.
- **2b.** The developer adds the opt-in `docs-skeleton` preset: the system seeds only the skeleton files that do not
  exist yet, and every existing file stays unchanged; resumes at step 3.
- **6a.** A file must stay at its path (a tool reads it there), or the developer chooses to fix a rule's debt in
  place: the agent records the deferral the developer decided as a `.devkit/config.toml` entry with its reason in a
  comment directly above it; resumes at step 7.

---

## 4. Postconditions

- **Success guarantee**: the `spec` bundle and the `devkit spec` commands are installed, the root `AGENTS.md` block
  carries the guidance pointer, `devkit rules check` passes, legacy files sit under `docs/materials/_legacy/`, and
  every added configuration entry carries the decision that justifies it.
- **Minimal guarantee**: `devkit sync` changes no existing file under `docs/` or `specs/`; no rule is edited to make
  the check pass; a deferral exists only where the developer decided it.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Installation exposes the bundle and the commands
- **Covers**: main success scenario (steps 1 to 3)
- **Given**: a repository managed with `uv` and devkit
- **When**: the developer runs `uv add --dev devkit devkit-spec` and `uv run devkit sync`
- **Then**: `.devkit/managed/spec/` holds the `core` preset, the root `AGENTS.md` block gains the `spec-pointer`
  line, and `uv run devkit spec --version` prints `[VERSION: devkit-spec <version>]`

### Scenario 2: Leaves existing docs alone by default
- **Covers**: main success scenario (step 2)
- **Given**: a repository with its own `docs/` tree
- **When**: `devkit sync` deploys the `spec` bundle without the `docs-skeleton` preset
- **Then**: no file under `docs/` is created or changed

### Scenario 3: Seeds only the missing skeleton files
- **Covers**: 2b
- **Given**: a repository with its own `docs/README.md`
- **When**: the developer runs `devkit add docs:docs-skeleton`
- **Then**: the skeleton files that did not exist are written, and `docs/README.md` is unchanged

### Scenario 4: Contains legacy documents without rewriting them
- **Covers**: main success scenario (steps 4 to 7)
- **Given**: the developer asked for the `brownfield-adoption` playbook or confirmed its intake offer, and
  `devkit rules check` reports violations in legacy Markdown under `docs/`
- **When**: the agent follows the playbook
- **Then**: the legacy files move under `docs/materials/_legacy/`, no rule is edited, and `devkit rules check` passes

### Scenario 5: Records a remaining deferral as a decided configuration entry
- **Covers**: 6a
- **Given**: a legacy file that a tool reads at its current path
- **When**: the developer decides to keep it there and the agent contains it
- **Then**: the deferral is a `.devkit/config.toml` entry with a comment stating the developer's reason, no rule is
  edited, and `devkit rules check` passes

### Scenario 6: Opts out of the bundle
- **Covers**: 2a
- **Given**: a project that wants the `devkit spec` commands but not the bundle
- **When**: it sets `[presets] spec = false` in `.devkit/config.toml` and runs `devkit sync`
- **Then**: the `spec` bundle's managed files and projections are not deployed

### Scenario 7: Separates verified adaptive-dev adoption from legacy containment
- **Covers**: 1a
- **Given**: the developer asks to adopt SDD from the retained adaptive-development product
- **When**: the agent selects the adoption path
- **Then**: it uses the explicit baseline procedure, keeps adaptive development during preparation and performs no automatic legacy containment
