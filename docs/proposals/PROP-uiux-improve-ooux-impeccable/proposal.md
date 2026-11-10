---
id: PROP-uiux-improve-ooux-impeccable
title: OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Rename uiux-improve with a software-interface qualifier, add proportionate OOUX framing and let a user-selected, brief-bounded Impeccable session edit product files under coordinator acceptance, leaving Impeccable's project files to the consumer."
status: reviewing
created_at: 2026-11-06
target_area: capabilities/delivery/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-catalog/src/devkit_catalog/uiux_improve/
    - packages/devkit-catalog/src/devkit_catalog/
    - packages/devkit-catalog/tests/integration/bundles/test_uiux_improve.py
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/tests/e2e/bundles/uiux_improve/
    - packages/devkit-catalog/tests/e2e/bundles/
    - packages/devkit-catalog/pyproject.toml
    - packages/devkit-catalog/README.md
    - .devkit/architecture.toml
    - guides/install/bundle-recommendations.md
    - docs/architecture/ARCH-05-2-components.md
    - docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
    - docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
    - docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
  excludes:
    - packages/devkit-catalog/src/devkit_catalog/design_explore/
    - docs/capabilities/delivery/CAP-DLV-design-exploration.md
    - packages/devkit-dist/
    - specs/2026-11/20261105-ux-design-exploration/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-uiux-improve-ooux-impeccable] OOUX-framed UI/UX improvement and Impeccable delegation

## 1. Background & Hypothesis

The `uiux-improve` catalog bundle (`CAP-DLV-uiux-improvement`) is an explicitly invoked coordinator with four
optional local roles (`designer`, `unconventional-designer`, `reference-researcher`, `critic`). The coordinator alone
changes product files, and the roles return suggestions only (`ADR-uiux-improvement-workflow-boundary`).

The repository owner reports three recurring problems from using it with coding agents. They are observations,
not measured results:

1. **Unqualified scope.** The name suggests any design work, while the skill targets software interfaces: web and
   desktop applications, dashboards, admin tools, settings and responsive views. It does not cover slide decks, game
   loops or media production.
2. **Structure skipped.** Agents move to styling or code before modeling the domain objects, their relationships and
   the actions on them, which produces fragmented screens and disjointed flows. Object-Oriented UX (OOUX) and its
   ORCA steps (Objects, Relationships, CTAs, Attributes) anchor an interface in those domain objects first.
3. **Generic craft.** Default output repeats generic patterns: nested cards, unmotivated gradients, one overused
   typeface, low-contrast secondary text and missing empty, loading and error states.

### Why this reverses part of `MAT-agent-team-design-pilot`

`MAT-agent-team-design-pilot` borrowed Impeccable's design perspectives as guidance and adopted none of its installer,
detector, hooks, CLI or project-file conventions. That choice kept the first bundle content-only while its value was
unknown and the owner declined a validation program. The borrowed perspectives are a static paraphrase: they do not
run Impeccable's deterministic detector or its maintained command references, and they drift from upstream.

This proposal changes the relationship, not the packaging. devkit still ships, installs and vendors nothing from
Impeccable. When the user has installed Impeccable and selects it for a request, the skill delegates craft work to it
and respects its project-file conventions instead of ignoring them. The pilot's other conclusions stand: optional
roles, no fixed cast and no comparative experiment as a prerequisite.

### Hypothesis

The skill gives the most leverage as an OOUX-grounded coordinator for software interfaces:

1. **Proportionate OOUX framing**: name the relevant objects, relationships, CTAs and attributes before layout or
   styling when a request changes structure or flow, and skip the framing for a local change.
2. **Optional Impeccable delegation**: on the user's selection, pass the framing and an explicit file boundary to one
   Impeccable session, then accept, verify and deliver its changes through the consumer workflow.
3. **Consumer-owned project files**: treat Impeccable's `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files as
   project context the consumer keeps or ignores, never as scaffolding the skill deletes.
4. **Qualified name**: rename the bundle and skill with a software-interface qualifier. `uiux-improve` is absent from
   release tag `v0.1.5` and has no other consumer, so the rename is a clean break.

### Scope and non-goals

- In scope:
  - Rename the bundle, skill, entry point, module, data root and test paths to the qualified name.
  - Restructure `SKILL.md` around framing, inline or delegated execution, and verification.
  - Add proportionate ORCA framing and baseline craft checks to `references/design-guidance.md`.
  - Add the Impeccable brief, routes and acceptance steps to `references/orchestration.md`.
  - Restate the capability, use case, component description, installation guide and catalog README.
  - Update the catalog tests for the new paths and instructions.
- Non-goals:
  - Vendoring or bundling Impeccable source, prompt text, binaries or npm packages.
  - Adding a Node.js or npm dependency to `devkit-catalog` or `devkit-dist`.
  - Installing Impeccable, its hooks or its CLI for the user.
  - Deleting, moving or git-ignoring consumer files on the skill's own initiative.
  - Non-software design domains (presentation decks, 3D or game graphics, video pipelines).
  - Aliases or migration bridges for the old `uiux-improve` name.
  - Renaming `CAP-DLV-uiux-improvement` or `UC-improve-an-interface-and-user-flow`.
  - Numeric scorecards, heuristic quotas or comparative experiments.

## 2. Technical Spike Questions and Planning Answers

- **Q1. Qualified name.** Pending the user's choice (worker question `q1`). Recommendation: `app-uiux-improve`, which
  keeps the recognizable `uiux-improve` stem and adds the software-application qualifier. The bundle, skill, entry-point
  key, module (`app_uiux_improve`) and test paths take the one chosen name. Zero breakage: release tag `v0.1.5` holds no
  `uiux` path, and every tracked reference is listed in [planning evidence](materials/planning-evidence.md) §2.
- **Q2. OOUX depth.** Framing scales with the request (§3.2). A local change skips it; a change across views writes a
  short object list in conversation; no diagram, notation or full-product object map is required.
- **Q3. Delegation brief.** `PADR-impeccable-session-authority` settles the authority model; §3.4 lists the brief.
  File boundaries are an explicit edit list checked after the session against a recorded base; interactive commands
  run in a session the user operates.
- **Q4. Impeccable project files.** They are consumer-owned project context (§3.5). The skill reports what a session
  created or changed, points to upstream's commit-versus-ignore guidance and changes nothing without the user's
  direction. Deletion is dropped: it conflicts with capability rules 3 and 14. Impeccable's own session output
  (snapshots, mocks, hook state) is reported separately.
- **Q5. Inline fallback.** `references/design-guidance.md` keeps its lenses and adds the baseline craft checks in §3.3,
  written originally.
- **Q6. Tests.** The renamed integration test keeps the 12,288-byte, governance-ID and conditional-reference checks and
  adds `assert_rule` checks for the new instructions (§3.7).

## 3. Proposed Design & Impact

### 3.1 Clean-break rename

- The chosen name replaces `uiux-improve` in `bundle.toml` (`name`, asset `id`, `source`), the skill directory and its
  `SKILL.md` `name`, the `packages/devkit-catalog/pyproject.toml` entry point, the module directory and the
  `.devkit/architecture.toml` `data_roots` entry.
- With the recommended name, Development creates `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/`,
  `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py` and
  `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/`. Their parents are owned only for these moves.
- `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md` and `ARCH-05-2-components` name the
  new bundle and path.
- No alias, redirect or compatibility entry is kept.
- `CAP-DLV-uiux-improvement` and `UC-improve-an-interface-and-user-flow` keep their IDs, so
  `CAP-DLV-design-exploration`, completed specs and ADR references need no change.

### 3.2 Procedure: frame, execute, verify

`SKILL.md` keeps recovery, inspection, review-only handling and reporting, and orders the improvement as:

1. **Frame in proportion to the request.**
   - A local change (one component, one state, copy or spacing) proceeds inline without an ORCA pass.
   - A change that adds, merges or reorders views or flows first names the affected objects, their relationships,
     the CTAs on each object and the attributes each view shows, with their empty, loading, error and populated states.
   - A review-only request can use the same framing as a lens and ends with findings and no product edits.
   - Framing covers the objects the request touches, never an exhaustive audit of the product.
2. **Execute inline or delegated.**
   - Inline (default): the coordinator implements, optionally with the four local roles, which stay available
     regardless of track. `reference-researcher` is retained.
   - Impeccable (on the user's selection only): the coordinator writes the brief in §3.4 and delegates one session
     under `PADR-impeccable-session-authority`: a fresh child for refinement, a session the user operates for
     interactive commands.
3. **Verify and report.** The coordinator inspects the changed interface and runs the project's applicable checks. On
   the Impeccable track, the session's detector and `audit` results join the evidence. It reports actual checks
   separately from design inference.

### 3.3 Design guidance additions

`references/design-guidance.md` gains, in original wording:

- **ORCA framing**: objects are domain nouns users think in, not widgets ("Invoice", not "Table"); relationships give
  navigation paths; CTAs sit on the object they act on rather than in global menus; attributes separate identifiers
  from metadata. One worked example covers a two-object flow.
- **Baseline craft checks**: readable contrast for secondary text, a consistent type scale, no decorative gradients
  or nested containers without a purpose, and empty, loading and error states for every changed view.
- The provenance section keeps Impeccable as a reference and states that nothing is copied.

### 3.4 Impeccable delegation in `references/orchestration.md`

1. **Selection.** Without the user's selection, the coordinator neither starts an Impeccable session nor loads or
   invokes Impeccable in its own context; an installed Impeccable permits an offer. Output of a hook the user
   installed counts as consumer check evidence.
2. **Availability.** If Impeccable is absent and the user wants it, name the upstream routes and stop that track:
   `npx impeccable install`, Claude Code `/plugin marketplace add pbakaus/impeccable` followed by installing it from
   `/plugin`, or a manual copy of `skills/impeccable`. The coordinator never installs it. The user can continue inline.
3. **Workflow first.** Complete the consumer workflow's steps that precede implementation (branch, worktree, required
   records) before delegating.
4. **Brief.** Goal; framing result; absolute working directory; recorded base (HEAD, status and content hashes of the
   listed files under Git, the listed files' hashes otherwise); the product files the session may edit; the files and
   concerns it leaves unchanged (data schema, business logic, dependencies, files with uncommitted user edits unless
   the user includes them); whether it may write consumer context files; the commands to run; the stop condition; the
   expected return (changed files, commands run, detector or audit results, session output, degraded coverage,
   blockers including any upstream question).
5. **Command routing.** A fresh child runs only commands that refine existing surfaces without user answers: `polish`,
   `audit` and narrow refinement commands such as `distill`, `typeset` or `layout`. New work, `init`, `shape` and
   `critique` ask the user questions (and `critique` needs two isolated sub-agents), so they run in a session the user
   operates from the same brief. A child returns any upstream question as a blocker and never answers it. No route
   uses `live`, which runs agents with sandbox and approvals off.
6. **`shape` and OOUX.** `shape` is an interactive interview that writes no code. The coordinator's framing covers its
   structural role for a fresh child. In a session the user runs, the user may run `shape` with the framing as its
   starting context; its brief stays in conversation.
7. **Pause.** The coordinator makes no product edits until the session returns.
8. **Acceptance.** Compare the working directory with the recorded base. Take changes to listed product files into
   verification. Report Impeccable session output (critique snapshots, mocks, hook and runtime state under
   `.impeccable/`) as session output, and any other change without reverting or deleting it. Report a moved HEAD, a
   missing base or unobservable ignored paths as unverifiable attribution or limited coverage. Continue accepted
   changes through the consumer workflow.

### 3.5 Impeccable project files

- `PRODUCT.md` (`init`), `DESIGN.md` (`document`) and shared `.impeccable/` files (`config.json`, `design.json`,
  `surfaces/*.md`, critique snapshots) are persistent project context; upstream recommends committing them and
  ignoring runtime output (`config.local.json`, caches, screenshots, `review/`, `questions/`, live session state).
- The consumer owns these files and decides their retention. The brief permits writes to `PRODUCT.md`, `DESIGN.md`,
  `.impeccable/design.json`, `.impeccable/config.json` and `.impeccable/surfaces/` only when it lists them.
- The coordinator lists the context files a session created or changed, points to upstream's "Project files and git"
  guidance, and changes neither them nor `.gitignore` without the user's direction.
- Upstream's README and `init` reference differ on critique snapshots; the skill points to upstream instead of
  restating either list ([planning evidence](materials/planning-evidence.md) §3).

### 3.6 Expected acceptance scenarios

- **AC-1:** Given a request that adds, merges or reorders views or flows, the agent names the affected objects,
  relationships, CTAs and attributes before layout or styling changes; given a local change, it proceeds without an
  ORCA pass; given a review-only request, it returns findings with no product edits.
- **AC-2:** Given the user selects Impeccable, the agent completes the consumer's pre-implementation workflow steps,
  produces a self-contained brief with the working directory, recorded base, edit list, unchanged concerns,
  context-file permission, routed commands without `live`, stop condition and expected return, and makes no product
  edits until the session returns.
- **AC-3:** Given a fresh child would need new work, `init`, `shape` or `critique`, the agent routes those commands to a
  session the user operates; given a child meets an upstream question, the child returns it as a blocker unanswered.
- **AC-4:** Given Impeccable is absent or not selected, the agent completes the improvement inline with the framing and
  design guidance without loading Impeccable; when the user wants Impeccable, it names the three upstream install
  routes and installs nothing.
- **AC-5:** Given a session created or changed `PRODUCT.md`, `DESIGN.md` or shared `.impeccable/` context files, the
  agent reports them as consumer-owned with upstream's retention guidance and deletes, moves or git-ignores none of
  them without the user's direction.
- **AC-6:** Given the session changed a file outside its edit list, the agent reports that file and neither reverts nor
  delivers it as accepted work; given HEAD moved or the base is missing, it reports attribution as unverifiable.
- **AC-7:** The bundle, skill, entry point, module, data root, tests, README, installation guide and component
  description use the qualified name; no alias or entry point for the old bundle, skill or module name remains.
- **AC-8:** Every bundled Markdown file stays within 12,288 bytes, contains no governance IDs and passes the catalog
  integration tests; the installed-consumer test passes under the new name without devkit-agt, devkit-docs or
  devkit-spec.
- **AC-9:** Selection, invocation and delegation grant no commit, integration or publication authority.

### 3.7 Tests

- Move and rename the integration and E2E tests; keep every existing assertion with the new paths.
- Add `assert_rule` checks: Impeccable neither loaded nor invoked without selection; workflow steps before delegating;
  brief fields including working directory and base; command routing to the user-run session; upstream questions
  returned unanswered; `live` excluded; no product edits while the session runs; outside-list changes reported without
  revert; unverifiable attribution reported; context files reported, not deleted or ignored; install routes named
  without installing; local change without ORCA pass.
- AC-1 to AC-6 and AC-9 are instruction checks: the tests verify stated behavior, not model obedience.

### 3.8 Planning decisions

- Capability and use-case IDs stay; only their text and entrypoints change (§3.1).
- The four local roles stay in both tracks; the delegated session is not a local role.
- Naming stays a Planning decision, not a PADR: it is reversible while the bundle has no consumers.
- Capability rule 14 stays a sync rule. Coordinator reporting of consumer context files becomes new rule 18, and the
  capability's interface section says the coordinator owns synthesis, acceptance and retained output.
- `ADR-uiux-improvement-workflow-boundary` is superseded in part, not wholly (`PADR-impeccable-session-authority`).
  The handoff writes its "Superseded in part by" line, and the Host clarifies that line to name the replaced clause
  before a worker starts (post-handoff link check). Development's only `docs/decisions/` edit is the reference repair
  of the bundle name in that ADR's clause 1, which changes no decision.

## 4. Lifecycle & Retirement Criteria

On acceptance with `devkit spec proposal accept uiux-improve-ooux-impeccable`, the handoff creates the spec, promotes
`PADR-impeccable-session-authority`, carries `PROP-uiux-improve-ooux-impeccable-target` and moves `materials/` into `docs/materials/`.
Development implements under the boundaries above and reconciles the Living Spec. The proposal bundle is removed by
the handoff.
