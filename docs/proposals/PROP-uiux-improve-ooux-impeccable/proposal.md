---
id: PROP-uiux-improve-ooux-impeccable
title: OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Rename uiux-improve to app-uiux-improve, ground framing in the consumer's OOUX documents when present, let a user-selected, brief-bounded Impeccable session edit product files under coordinator acceptance and add a human usage guide."
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

A project that uses devkit's document system already keeps an OOUX model in files: object names in
`docs/steering/glossary.md`, object representations and calls to action per role in `docs/steering/ux-objects.md`,
and each screen's content tree, states and interactions in `docs/ux/<area>/UX-<slug>.md` (the `ux-writing`
instruction of the `docs` bundle). The current skill never reads them, so a framing pass restates or contradicts the
object model the project maintains.

### Why this reverses part of `MAT-agent-team-design-pilot`

`MAT-agent-team-design-pilot` borrowed Impeccable's design perspectives as guidance and adopted none of its installer,
detector, hooks, CLI or project-file conventions. That choice kept the first bundle content-only while its value was
unknown and the owner declined a validation program. The borrowed perspectives are a static paraphrase: they do not
run Impeccable's deterministic detector or its maintained command references, and they drift from upstream.

This proposal changes the relationship, not the packaging. devkit still ships and vendors nothing from Impeccable.
When the user has installed Impeccable and selects it for a request, the skill delegates craft work to it and
respects its project-file conventions instead of ignoring them. Installing Impeccable and cleaning up its output are
steps the user can take by hand; the skill only performs them on the user's request, for convenience. The pilot's
other conclusions stand: optional roles, no fixed cast and no comparative experiment as a prerequisite.

### Hypothesis

The skill gives the most leverage as an OOUX-grounded coordinator for software interfaces:

1. **Proportionate OOUX framing**: name the relevant objects, relationships, CTAs and attributes before layout or
   styling when a request changes structure or flow, and skip the framing for a local change.
2. **Documents first when they exist**: take the framing from the project's glossary, object register and UX
   documents when present, pass their paths to Impeccable instead of restating them, and report the UX documents a
   change makes stale instead of editing them. Without those documents, frame in conversation.
3. **Optional Impeccable delegation**: on the user's selection, pass the framing and an explicit file boundary to one
   Impeccable session, then accept, verify and deliver its changes through the consumer workflow.
4. **Consumer-owned project files**: treat Impeccable's `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files as
   project context the consumer keeps or ignores. `PRODUCT.md` can carry a short reference section to the OOUX
   documents, so every Impeccable command reads the same object model.
5. **User-requested conveniences**: install Impeccable, add upstream-recommended ignore entries and remove named
   Impeccable output only when the user asks.
6. **Qualified name**: rename the bundle and skill to `app-uiux-improve`, which adds the software-application
   qualifier. `uiux-improve` is absent from release tag `v0.1.5` and has no other consumer, so the rename is a clean
   break.
7. **A guide the user can reread**: a human-facing usage guide beside the bundle explains setup, the per-task flow
   and what the coordinator does and does not do.

### Scope and non-goals

- In scope:
  - Rename the bundle, skill, entry point, module, data root and test paths to `app-uiux-improve` (module
    `app_uiux_improve`).
  - Restructure `SKILL.md` around framing, inline or delegated execution, and verification.
  - Add proportionate ORCA framing, its conditional document sources and baseline craft checks to
    `references/design-guidance.md`.
  - Add the Impeccable brief, routes, acceptance, the `PRODUCT.md` reference section and user-requested setup and
    cleanup to `references/orchestration.md`.
  - Add the human-facing usage guide `bundle/README.md` (§3.6).
  - Restate the capability, use case, component description, installation guide and catalog README.
  - Update the catalog tests for the new paths, instructions and guide.
- Non-goals:
  - Vendoring or bundling Impeccable source, prompt text, binaries or npm packages.
  - Adding a Node.js or npm dependency to `devkit-catalog` or `devkit-dist`.
  - Installing Impeccable, its hooks or its CLI, or removing or ignoring any file, on the coordinator's own initiative.
  - A dependency on `devkit-docs` or its document conventions: the skill reads those documents only where they exist.
  - Writing or updating the consumer's glossary, object register or UX documents from the skill; it reports them.
  - Copying object, attribute or state content into `PRODUCT.md` or `DESIGN.md`.
  - Shipping the usage guide to consumers or linking it from an agent-read file.
  - Non-software design domains (presentation decks, 3D or game graphics, video pipelines).
  - Aliases or migration bridges for the old `uiux-improve` name.
  - Renaming `CAP-DLV-uiux-improvement` or `UC-improve-an-interface-and-user-flow`.
  - Numeric scorecards, heuristic quotas or comparative experiments.

## 2. Technical Spike Questions and Planning Answers

- **Q1. Qualified name.** The user chose `app-uiux-improve` (worker question `q1`), which keeps the recognizable
  `uiux-improve` stem and adds the software-application qualifier. The bundle, skill, entry-point key, module
  (`app_uiux_improve`), data root and test paths take this one name (§3.1). Zero breakage: release tag `v0.1.5` holds
  no `uiux` path, and every tracked reference is listed in [planning evidence](materials/planning-evidence.md) §2.
- **Q2. OOUX depth and sources.** Framing scales with the request (§3.2). A local change skips it; a change across
  views frames the affected objects, from the project's OOUX documents when present and in conversation otherwise; no
  diagram, notation or full-product object map is required (§3.3).
- **Q3. Delegation brief.** `PADR-impeccable-session-authority` settles the authority model; §3.4 lists the brief.
  File boundaries are an explicit edit list checked after the session against a recorded base; interactive commands
  run in a session the user operates.
- **Q4. Impeccable project files.** They are consumer-owned project context (§3.5). The skill reports what a session
  created or changed and points to upstream's commit-versus-ignore guidance. On the user's request it adds ignore
  entries or removes named runtime and session output; `PRODUCT.md` and `DESIGN.md` change only on the user's
  explicit direction.
- **Q5. Inline fallback.** `references/design-guidance.md` keeps its lenses and adds the baseline craft checks in §3.3,
  written originally.
- **Q6. Tests.** The renamed integration test keeps the 12,288-byte, governance-ID and conditional-reference checks and
  adds `assert_rule` checks for the new instructions and guide checks (§3.7).
- **Q7. Child loading Impeccable.** Claude Code documents that a fresh subagent can discover and invoke project,
  user and plugin skills through the Skill tool; Codex documents skill inheritance for sub-agents but not discovery
  ([planning evidence](materials/planning-evidence.md) §4). Loading is host-dependent, so a child that cannot load
  Impeccable returns a blocker and the command moves to the user's session (§3.4).

## 3. Proposed Design & Impact

### 3.1 Clean-break rename

- `app-uiux-improve` replaces `uiux-improve` in `bundle.toml` (`name`, asset `id`, `source`, preset `core`), the skill
  directory and its `SKILL.md` `name`. The `packages/devkit-catalog/pyproject.toml` entry point becomes
  `app-uiux-improve = "devkit_catalog.app_uiux_improve"`, and the `.devkit/architecture.toml` `data_roots` entry becomes
  `app_uiux_improve`.
- Development moves the module to `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/` (skill at
  `bundle/skills/app-uiux-improve/`, usage guide at `bundle/README.md`), the integration test to
  `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py` and the E2E test directory to
  `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/`. The boundaries name these new paths by their existing
  parents, which are owned only for these moves and the guide.
- `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md` and `ARCH-05-2-components` name the
  new bundle and path.
- No alias, redirect or compatibility entry is kept.
- `CAP-DLV-uiux-improvement` and `UC-improve-an-interface-and-user-flow` keep their IDs, so
  `CAP-DLV-design-exploration`, completed specs and ADR references need no change.

### 3.2 Usage flow

`SKILL.md` keeps recovery, inspection, review-only handling and reporting, and orders the work as below. The
one-time steps are the user's; the coordinator helps only on request.

**One-time per project**

1. Install Impeccable through an upstream route (§3.4 item 2): by the user, or by the coordinator on the user's
   request.
2. Run Impeccable's `init` in a session the user operates; it writes `PRODUCT.md`.
3. Add the OOUX reference section to `PRODUCT.md` (§3.5): in that `init` session, or by the coordinator on the user's
   request.

**Per task**

1. **Start.** The user invokes `/app-uiux-improve <goal>` in the devkit session. The coordinator recovers the goal and
   completes the consumer workflow's steps that precede implementation (branch, worktree, required records).
2. **Frame in proportion to the request** (§3.3), in the devkit session.
   - A local change (one component, one state, copy or spacing) proceeds without an ORCA pass.
   - A change that adds, merges or reorders views or flows first names the affected objects, their relationships,
     the CTAs on each object and the attributes each view shows, with their empty, loading, error and populated
     states. The framing reads the project's OOUX documents when present and falls back to conversation.
   - A review-only request can use the same framing as a lens and ends with findings and no product edits.
   - Framing covers the objects the request touches, never an exhaustive audit of the product.
3. **Choose the track.** Inline is the default: the coordinator implements, optionally with the four local roles,
   which stay available on both tracks. On the user's selection of Impeccable, the coordinator writes the brief
   (§3.4): goal, OOUX document paths or framing, edit list, recorded base, commands and stop condition.
4. **Run the Impeccable session.** The coordinator makes no product edits until it returns.
   - (a) Refinement commands on existing surfaces (`polish`, `audit`, narrow refine commands): the coordinator spawns
     a fresh child that loads Impeccable, reads `PRODUCT.md` and the brief, edits only listed files and returns its
     changes with audit and detector results. The child returns any upstream question as a blocker.
   - (b) Interactive commands (new screens, `shape`, `critique`, `init`): the coordinator hands the brief to the user,
     who runs it in their own Impeccable session and reports back.
   - Where the host cannot give a child Impeccable, refinement also goes to the user's session.
5. **Accept and continue** in the devkit session. The coordinator compares the working directory with the recorded
   base, verifies the accepted changes, reports changes outside the edit list and the UX documents the change made
   stale, and continues the consumer workflow.
6. **Optional cleanup**, on the user's request only (§3.5).

In an SDD consumer, a new screen is drafted as a Screen in Planning (`target-docs.md` or `spec.md`) before code;
Impeccable implements and refines that draft. The skill states this as following the consumer workflow, without
naming SDD records.

### 3.3 Design guidance additions

`references/design-guidance.md` gains, in original wording:

- **ORCA framing**: objects are domain nouns users think in, not widgets ("Invoice", not "Table"); relationships give
  navigation paths; CTAs sit on the object they act on rather than in global menus; attributes separate identifiers
  from metadata. One worked example covers a two-object flow.
- **Framing sources**, read only where the files exist:
  - object names from the project glossary (`docs/steering/glossary.md`, plus a selected namespace glossary);
  - representations and CTAs per role from the object register (`docs/steering/ux-objects.md`, plus a namespace
    register);
  - attributes, states and interactions from the UX documents (`docs/ux/<area>/`) of the affected screens.
  - Without them, the coordinator frames in conversation. A partial set is used as far as it goes.
  - The framing never writes these files; stale documents are reported after the change (§3.4 item 8).
- **Baseline craft checks**: readable contrast for secondary text, a consistent type scale, no decorative gradients
  or nested containers without a purpose, and empty, loading and error states for every changed view.
- The provenance section keeps Impeccable as a reference and states that nothing is copied.

The paths are named as an optional convention, so the bundle still installs and runs without `devkit-docs`
(capability rule 13).

### 3.4 Impeccable delegation in `references/orchestration.md`

1. **Selection.** Without the user's selection, the coordinator neither starts an Impeccable session nor loads or
   invokes Impeccable in its own context; an installed Impeccable permits an offer. Output of a hook the user
   installed counts as consumer check evidence.
2. **Availability.** If Impeccable is absent and the user wants it, the coordinator names the upstream routes:
   `npx impeccable install`, Claude Code `/plugin marketplace add pbakaus/impeccable` followed by installing it from
   `/plugin`, or a manual copy of `skills/impeccable`. On the user's request it runs a route it can run (the `npx`
   installer or the manual copy) under the host's approvals; the user answers the installer's prompts, including its
   hook offer, and runs the `/plugin` route. It never installs on its own initiative. The user can continue inline.
3. **Workflow first.** Complete the consumer workflow's steps that precede implementation (branch, worktree, required
   records) before delegating.
4. **Brief.** Goal; the OOUX document paths as read-only context, or the conversation framing when no document
   exists; absolute working directory; recorded base (HEAD, status and content hashes of the listed files under Git,
   the listed files' hashes otherwise); the product files the session may edit; the files and concerns it leaves
   unchanged (data schema, business logic, dependencies, the OOUX documents, files with uncommitted user edits unless
   the user includes them); whether it may write consumer context files; the commands to run; the stop condition; the
   expected return (changed files, commands run, detector or audit results, session output, degraded coverage,
   blockers including any upstream question).
5. **Command routing.** A fresh child runs only commands that refine existing surfaces without user answers: `polish`,
   `audit` and narrow refinement commands such as `distill`, `typeset` or `layout`. The child loads Impeccable through
   the host's skill mechanism; a child that cannot load it returns that as a blocker, and the coordinator moves the
   command to the user's session. New work, `init`, `shape` and `critique` ask the user questions (and `critique`
   needs two isolated sub-agents), so they run in a session the user operates from the same brief. A child returns
   any upstream question as a blocker and never answers it. No route uses `live`, which runs agents with sandbox and
   approvals off.
6. **`shape` and OOUX.** `shape` is an interactive interview that writes no code. The coordinator's framing covers its
   structural role for a fresh child. In a session the user runs, the user may run `shape` with the brief as its
   starting context; its brief stays in conversation.
7. **Pause.** The coordinator makes no product edits until the session returns.
8. **Acceptance.** Compare the working directory with the recorded base. Take changes to listed product files into
   verification. Report Impeccable session output (critique snapshots, mocks, hook and runtime state under
   `.impeccable/`) as session output, and any other change without reverting or deleting it. Report a moved HEAD, a
   missing base or unobservable ignored paths as unverifiable attribution or limited coverage. Report each OOUX
   document whose states or interactions the accepted change made stale, for the consumer workflow to update (under
   SDD, `spec-sync`). Continue accepted changes through the consumer workflow.

### 3.5 Impeccable project files, the `PRODUCT.md` anchor and user-requested setup

- `PRODUCT.md` (`init`), `DESIGN.md` (`document`) and shared `.impeccable/` files (`config.json`, `design.json`,
  `surfaces/*.md`, critique snapshots) are persistent project context; upstream recommends committing them and
  ignoring runtime output (`config.local.json`, caches, screenshots, `review/`, `questions/`, live session state).
- The consumer owns these files and decides their retention. The brief permits writes to `PRODUCT.md`, `DESIGN.md`,
  `.impeccable/design.json`, `.impeccable/config.json` and `.impeccable/surfaces/` only when it lists them.
- **OOUX anchor.** `PRODUCT.md` can hold a short section that names the project's glossary, object register and UX
  document directory by path and says to read them before structural work. It references the documents and copies
  none of their content, so the anchor cannot drift. The user writes it in the `init` session, or the coordinator
  adds it on the user's request. Every Impeccable command reads `PRODUCT.md`, so every session sees the object model.
- **Reporting.** The coordinator lists the context files a session created or changed and points to upstream's
  "Project files and git" guidance.
- **User-requested conveniences.** On the user's request, and never on its own initiative, the coordinator may:
  - install Impeccable through an upstream route (§3.4 item 2);
  - add upstream's recommended ignore entries to `.gitignore`;
  - remove Impeccable runtime or session output the user names (for example screenshots or `review/`);
  - add the OOUX anchor to `PRODUCT.md`.
- `PRODUCT.md` and `DESIGN.md` are never part of a cleanup unless the user names them, because the anchor and design
  context live there. Any change to them needs the user's explicit direction.
- A user-requested change is the consumer's decision and goes through the consumer workflow and the host's approvals
  like any product change (capability rule 3). Sync's artifact preservation (capability rule 14) is unchanged.
- Upstream's README and `init` reference differ on critique snapshots; the skill points to upstream instead of
  restating either list ([planning evidence](materials/planning-evidence.md) §3).

### 3.6 Human-facing usage guide

`packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md` is a guide for the person using the
bundle, read before or after installing it. It is not an agent asset:

- Sync deploys only the declared skill asset and `bundle.toml`, so the guide stays in the devkit repository and the
  wheel and never reaches a consumer's managed or projected files.
- No agent-read file links it: neither `SKILL.md`, a reference, a role nor `bundle.toml`.
- It sits outside the paths of the agent-asset wording and skill-size rules; it follows the repository's
  `document-writing` baseline in English and names no governance ID, so it reads the same outside this repository.
- `packages/devkit-catalog/README.md` keeps a short section for the bundle that links the guide.

Contents, in this order:

1. What the bundle is for (software interfaces) and what it does not do.
2. One-time setup: selecting the bundle, installing Impeccable (three upstream routes, or the coordinator on
   request), running `init` and adding the OOUX anchor to `PRODUCT.md`.
3. Per-task flow (§3.2) with one example request.
4. The two launch routes: a fresh child for refinement, the user's own session for interactive commands, and what
   the user reports back.
5. What the coordinator does and does not do (selection, pause, acceptance, no commit authority, no installation or
   cleanup without a request).
6. OOUX document linkage: which documents the framing reads, the anchor and the report-only write-back.
7. Opt-in setup and cleanup, with the `PRODUCT.md` and `DESIGN.md` exclusion.
8. Troubleshooting: Impeccable asks a question, the child cannot load Impeccable, a change outside the edit list,
   moved HEAD or unverifiable attribution, Impeccable not installed, a stale UX document.

### 3.7 Expected acceptance scenarios and tests

- **AC-1:** Given a request that adds, merges or reorders views or flows, the agent names the affected objects,
  relationships, CTAs and attributes before layout or styling changes; given a local change, it proceeds without an
  ORCA pass; given a review-only request, it returns findings with no product edits.
- **AC-2:** Given the user selects Impeccable, the agent completes the consumer's pre-implementation workflow steps,
  produces a self-contained brief with the working directory, recorded base, edit list, unchanged concerns,
  context-file permission, routed commands without `live`, stop condition and expected return, and makes no product
  edits until the session returns.
- **AC-3:** Given a fresh child would need new work, `init`, `shape` or `critique`, the agent routes those commands to a
  session the user operates; given a child meets an upstream question or cannot load Impeccable, the child returns it
  as a blocker unanswered and the agent routes the command to the user's session.
- **AC-4:** Given Impeccable is absent or not selected, the agent completes the improvement inline with the framing and
  design guidance without loading Impeccable; when the user wants Impeccable, it names the three upstream install
  routes and installs only on the user's request.
- **AC-5:** Given a session created or changed `PRODUCT.md`, `DESIGN.md` or shared `.impeccable/` context files, the
  agent reports them as consumer-owned with upstream's retention guidance; it installs, adds ignore entries or removes
  named runtime or session output only on the user's request, and changes `PRODUCT.md` or `DESIGN.md` only on the
  user's explicit direction.
- **AC-6:** Given the session changed a file outside its edit list, the agent reports that file and neither reverts nor
  delivers it as accepted work; given HEAD moved or the base is missing, it reports attribution as unverifiable.
- **AC-7:** The bundle, skill, entry point, module, data root, tests, README, installation guide and component
  description use `app-uiux-improve` (module `app_uiux_improve`); no alias or entry point for the old `uiux-improve`
  bundle, skill or `uiux_improve` module remains.
- **AC-8:** Every Markdown file under the skill directory stays within 12,288 bytes, contains no governance IDs and
  passes the catalog integration tests; the installed-consumer test passes as `app-uiux-improve` without devkit-agt,
  devkit-docs or devkit-spec.
- **AC-9:** Selection, invocation and delegation grant no commit, integration or publication authority.
- **AC-10:** Given the project has a glossary, object register or UX documents, the agent frames from them and the brief
  passes their paths read-only instead of restating objects; given they are absent, it frames in conversation; after
  an accepted change, it reports the UX documents that need updating and edits none of them.
- **AC-11:** The usage guide exists at `bundle/README.md` with the contents in §3.6, contains no governance IDs, is
  linked from the catalog README, is linked from no agent-read bundle file and is absent from a synced consumer's
  managed and projected files.

Tests:

- Move and rename the integration and E2E tests; keep every existing assertion with the new paths.
- Add `assert_rule` checks: Impeccable neither loaded nor invoked without selection; workflow steps before delegating;
  brief fields including working directory, base and OOUX document paths; command routing to the user-run session;
  upstream questions and load failures returned as blockers; `live` excluded; no product edits while the session runs;
  outside-list changes reported without revert; unverifiable attribution reported; stale UX documents reported, not
  edited; framing sources conditional with the conversation fallback; context files reported; installation, ignore
  entries and cleanup only on request; `PRODUCT.md` and `DESIGN.md` changed only on explicit direction; local change
  without ORCA pass.
- Guide checks (AC-11): the file exists and names each §3.6 section; no governance ID; the catalog README links it;
  no file under the skill directory or `bundle.toml` names `README.md`; the synced managed set stays `bundle.toml` plus
  the skill files, and no projected skill directory holds `README.md`. The installed-consumer test asserts the same
  absence.
- AC-1 to AC-6, AC-9 and AC-10 are instruction checks: the tests verify stated behavior, not model obedience.

### 3.8 Planning decisions

- Capability and use-case IDs stay; only their text and entrypoints change (§3.1).
- The four local roles stay in both tracks; the delegated session is not a local role.
- Naming stays a Planning decision, not a PADR: it is reversible while the bundle has no consumers. The user chose
  `app-uiux-improve` over `software-ui-improve` and `ooux-ui-improve`.
- Capability rule 14 stays a sync rule. Coordinator reporting of consumer context files becomes new rule 18, and the
  capability's interface section says the coordinator owns synthesis, acceptance and retained output.
- `ADR-uiux-improvement-workflow-boundary` is superseded in part, not wholly (`PADR-impeccable-session-authority`).
  The handoff writes its "Superseded in part by" line, and the Host clarifies that line to name the replaced clause
  before a worker starts (post-handoff link check). Development's only `docs/decisions/` edit is the reference repair
  of the bundle name in that ADR's clause 1, which changes no decision.
- **OOUX document linkage (by: user).** The skill links devkit's own OOUX documents in three ways:
  - A, framing source: framing reads the glossary, object register and UX documents when present and the brief passes
    their paths read-only; without them it frames in conversation. The read is conditional and adds no dependency on
    `devkit-docs` (capability rule 13).
  - B, persistent anchor: `PRODUCT.md` gets a reference section, never a copy, written in the user's `init` session
    or by the coordinator on request.
  - C, report-only write-back: the coordinator reports the UX documents a change made stale; the consumer workflow
    updates them.
  - Rejected: copying objects into `PRODUCT.md` (drifts from the documents); the skill updating UX documents itself
    (crosses the consumer workflow's ownership and needs `devkit-docs` conventions); conversation-only framing
    (ignores the model the project maintains).
  - A stays a Planning decision with capability rule 4. B and C change who may write which file, so they are clauses
    of `PADR-impeccable-session-authority`.
- **Setup and cleanup are user-requested conveniences (by: user).** On the user's request the coordinator may install
  Impeccable through an upstream route, add upstream-recommended ignore entries or remove Impeccable runtime or
  session output the user names; never on its own initiative. This replaces "the coordinator never installs
  Impeccable" and "never deletes, moves or git-ignores". `PRODUCT.md` and `DESIGN.md` stay out of default cleanup
  because the anchor and design context live there, and any change to them needs the user's explicit direction. A
  user-directed action is the consumer's decision under capability rule 3; rule 14 is unaffected.
  `PADR-impeccable-session-authority` carries the change.
- **Usage flow (by: user).** §3.2 states the one-time and per-task flow, the two launch routes and the SDD note that a
  new screen is drafted in Planning before Impeccable implements it.
- **Child loading is host-dependent (Planning).** A child loads Impeccable through the host's skill mechanism. Claude
  Code documents that path; Codex does not document it for sub-agents. A child that cannot load Impeccable returns a
  blocker, and the command moves to the user's session. Rejected: a child reading Impeccable's `SKILL.md` by path,
  because it loses skill-scoped hooks and tool grants and is not an upstream route.
- **Usage guide location (by: user, Planning choice of path).** The user asked for a human-facing guide to reread,
  read before or after installation, that is not an agent asset and is linked from no agent entry point. Chosen:
  `bundle/README.md` beside `bundle.toml`. Sync does not deploy it, the authoring rules do not scan it, and it sits
  where the bundle's source is browsed; the catalog README links it.
  - Rejected: a file in the skill directory (deployed into consumers as agent-read content, subject to the agent-asset
    limits and a second copy of the instructions).
  - Rejected: `guides/` (the repository defines it as agent-facing installation guides).
  - Rejected: a longer catalog README section (the user wants that README to stay a short pointer).
  - Rejected: `docs/` (the Living Spec holds capabilities, use cases, architecture and decisions, not usage guides).
- **Development effort stays `medium`.** The added work is instruction text, one guide and test assertions with the
  same verification as before.

## 4. Lifecycle & Retirement Criteria

On acceptance with `devkit spec proposal accept uiux-improve-ooux-impeccable`, the handoff creates the spec, promotes
`PADR-impeccable-session-authority`, carries `PROP-uiux-improve-ooux-impeccable-target` and moves `materials/` into `docs/materials/`.
Development implements under the boundaries above and reconciles the Living Spec. The proposal bundle is removed by
the handoff.
