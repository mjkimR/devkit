---
id: SPEC-uiux-improve-ooux-impeccable
title: OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Rename uiux-improve to app-uiux-improve, ground framing in the consumer's OOUX documents when present, let a user-selected, brief-bounded Impeccable session edit product files under coordinator acceptance and add a human usage guide."
status: planned
created: 2026-11-10
related_capabilities: [CAP-DLV-uiux-improvement]
related_usecases: [UC-improve-an-interface-and-user-flow]
workflow: sdd-spec-feature
---

# [SPEC-uiux-improve-ooux-impeccable] OOUX-framed UI/UX improvement and Impeccable delegation

## 1. Problem Statement & Motivation

Handed off from proposal PROP-uiux-improve-ooux-impeccable on 2026-11-10.

- **Preserved Materials**: [planning evidence](../../../docs/materials/2026-11/20261110-uiux-improve-ooux-impeccable/planning-evidence.md)
  (rename references, upstream Impeccable facts, host facts on child skill loading).
- **Target Docs Blueprint**: `PROP-uiux-improve-ooux-impeccable-target` (Living Spec targets for this plan and
  `reconcile.md`).
- **Decision**: `ADR-impeccable-session-authority` (supersedes `ADR-uiux-improvement-workflow-boundary` in part).

### 1.1 Background

The `uiux-improve` catalog bundle (`CAP-DLV-uiux-improvement`) is an explicitly invoked coordinator with four
optional local roles (`designer`, `unconventional-designer`, `reference-researcher`, `critic`). The coordinator alone
changes product files, and the roles return suggestions only (`ADR-uiux-improvement-workflow-boundary`).

The repository owner reports three recurring problems from using it with coding agents. They are observations, not
measured results:

1. **Unqualified scope.** The name suggests any design work, while the skill targets software interfaces: web and
   desktop applications, dashboards, admin tools, settings and responsive views. It does not cover slide decks, game
   loops or media production.
2. **Structure skipped.** Agents move to styling or code before modeling the domain objects, their relationships and
   the actions on them, which produces fragmented screens and disjointed flows. Object-Oriented UX (OOUX) and its ORCA
   steps (Objects, Relationships, CTAs, Attributes) anchor an interface in those domain objects first.
3. **Generic craft.** Default output repeats generic patterns: nested cards, unmotivated gradients, one overused
   typeface, low-contrast secondary text and missing empty, loading and error states.

A project that uses devkit's document system already keeps an OOUX model in files: object names in
`docs/steering/glossary.md`, object representations and calls to action per role in `docs/steering/ux-objects.md`,
and each screen's content tree, states and interactions in `docs/ux/<area>/UX-<slug>.md`. The current skill never
reads them, so a framing pass restates or contradicts the object model the project maintains.

### 1.2 Why this reverses part of `MAT-agent-team-design-pilot`

`MAT-agent-team-design-pilot` borrowed Impeccable's design perspectives as guidance and adopted none of its
installer, detector, hooks, CLI or project-file conventions. That kept the first bundle content-only while its value
was unknown. The borrowed perspectives are a static paraphrase: they do not run Impeccable's deterministic detector
or its maintained command references, and they drift from upstream.

This change alters the relationship, not the packaging. devkit still ships and vendors nothing from Impeccable. When
the user has installed Impeccable and selects it for a request, the skill delegates craft work to it and respects its
project-file conventions. Installing Impeccable and cleaning up its output are steps the user can take by hand; the
skill performs them only on the user's request. The pilot's other conclusions stand: optional roles, no fixed cast
and no comparative experiment as a prerequisite.

### 1.3 Hypothesis

The skill gives the most leverage as an OOUX-grounded coordinator for software interfaces:

1. **Proportionate OOUX framing**: name the relevant objects, relationships, CTAs and attributes before layout or
   styling when a request changes structure or flow; skip the framing for a local change.
2. **Documents first when they exist**: take the framing from the project's glossary, object register and UX
   documents when present, cite their paths to Impeccable instead of restating them, and report the documents a
   change makes stale instead of editing them in the skill run. Without those documents, frame in conversation.
3. **Optional Impeccable delegation**: on the user's selection, pass the framing and an explicit file boundary to one
   Impeccable session, then accept, verify and deliver its changes through the consumer workflow.
4. **Consumer-owned project files**: treat Impeccable's `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files as
   project context the consumer keeps or ignores; `PRODUCT.md` can carry a short reference section to the OOUX
   documents.
5. **User-requested conveniences**: install Impeccable, add upstream-recommended ignore entries and remove named
   Impeccable output only when the user asks.
6. **Qualified name**: rename the bundle and skill to `app-uiux-improve`. `uiux-improve` is absent from release tag
   `v0.1.5` and has no other consumer, so the rename is a clean break.
7. **A guide the user can reread**: a human-facing usage guide beside the bundle explains setup, the per-task flow and
   what the coordinator does and does not do.

## 2. User Stories

- **US-1**: As a product owner, I want the UI/UX skill's name and text to say it targets software interfaces, so that
  I invoke it for the right work.
- **US-2**: As a product owner, I want an agent to frame the affected domain objects from my project's OOUX documents
  before it restructures views or flows, so that screens follow the object model the project maintains.
- **US-3**: As a product owner with Impeccable installed, I want to select Impeccable for craft work and have the
  coordinator brief, bound, accept and verify its session, so that I can use its maintained commands without giving
  up my workflow's authority.
- **US-4**: As a product owner, I want Impeccable's project files, setup and cleanup to stay my decision, so that
  nothing is installed, ignored or removed without my request.
- **US-5**: As a product owner, I want a usage guide I can reread before or after installing the bundle, so that I
  know the setup, the per-task flow and what the coordinator will not do.

## 3. Non-Goals

1. **Scope Excluded**: vendoring or bundling Impeccable source, prompt text, binaries or npm packages; adding a
   Node.js or npm dependency to `devkit-catalog` or `devkit-dist`.
2. **Scope Excluded**: installing Impeccable, its hooks or its CLI, or removing or ignoring any file, on the
   coordinator's own initiative.
3. **Scope Excluded**: a dependency on `devkit-docs` or its document conventions; the skill reads the OOUX documents
   only where they exist and names no namespace-selection concept.
4. **Scope Excluded**: writing or updating the consumer's glossary, object register or UX documents within the skill
   run; copying object, attribute or state content into `PRODUCT.md` or `DESIGN.md`.
5. **Scope Excluded**: shipping the usage guide to consumers or linking it from an agent-read file.
6. **Scope Excluded**: non-software design domains (presentation decks, 3D or game graphics, video pipelines).
7. **Scope Excluded**: aliases or migration bridges for the old `uiux-improve` name; renaming
   `CAP-DLV-uiux-improvement` or `UC-improve-an-interface-and-user-flow`.
8. **Scope Excluded**: numeric scorecards, heuristic quotas or comparative experiments.
9. **Scope Excluded**: changes to the `design-explore` bundle, `CAP-DLV-design-exploration`, `devkit-dist` or the
   completed `SPEC-ux-design-exploration`.

## 4. Acceptance Criteria & Behavioral Contracts

AC-01 to AC-06, AC-09 and AC-10 are instruction contracts: their tests assert the stated instruction in the bundled
text (`assert_rule` over the named file), not model obedience.

### [AC-01] Proportionate ORCA framing

- **Given** the installed `SKILL.md` and `references/design-guidance.md`
- **When** a request adds, merges or reorders views or flows, is a local change, or is review-only
- **Then** the text directs naming the affected objects, relationships, CTAs and attributes (with empty, loading,
  error and populated states) before layout or styling for the first; proceeding without an ORCA pass for a local
  change; and findings with no product edits for review-only, and the guidance holds one worked two-object example and
  the baseline craft checks

### [AC-02] Selected delegation with a complete brief and a pause

- **Given** the installed `references/orchestration.md`
- **When** the user selects Impeccable
- **Then** the text directs completing the consumer workflow's pre-implementation steps first, then a brief naming:
  goal, framing result citing OOUX documents by path read-only, consumer drafts by path read-only, absolute working
  directory, recorded base, edit list, unchanged concerns, context-file permission (`PRODUCT.md` or `DESIGN.md` only on
  the user's explicit direction), routed commands without `live`, stop condition and expected return; and no product
  edits by the coordinator until the session returns

### [AC-03] Command routing and blockers

- **Given** the installed `references/orchestration.md`
- **When** a command is new work, `init`, `shape` or `critique`, or a child meets an upstream question or cannot load
  Impeccable
- **Then** the text routes the command to a session the user operates, and the child returns the question or load
  failure as a blocker without answering it; only refinement commands (`polish`, `audit`, narrow refinement commands)
  run in a fresh child

### [AC-04] Inline track and installation routes

- **Given** the installed `SKILL.md` and `references/orchestration.md`
- **When** Impeccable is absent or not selected
- **Then** the text directs completing the improvement inline without loading or invoking Impeccable; when the user
  wants Impeccable it names the three upstream install routes (`npx impeccable install`, the Claude Code `/plugin`
  marketplace route, a manual copy of `skills/impeccable`), installs only on the user's request through a route that
  needs no prompt answers, and otherwise hands the user the exact command

### [AC-05] Consumer context files and user-requested setup and cleanup

- **Given** the installed `references/orchestration.md`
- **When** a session created or changed `PRODUCT.md`, `DESIGN.md` or shared `.impeccable/` context files, or the user
  asks for installation, ignore entries, cleanup or the `PRODUCT.md` anchor
- **Then** the text reports the files as consumer-owned with upstream's retention guidance; adds ignore entries
  confined to `.impeccable/` paths only after showing the exact lines; removes only runtime or session output the user
  names; takes none of these actions on its own initiative; and changes `PRODUCT.md` or `DESIGN.md`, or permits a
  session to, only on the user's explicit direction

### [AC-06] Acceptance against the recorded base

- **Given** the installed `references/orchestration.md`
- **When** the session returns having changed a file outside its edit list, or HEAD moved or the base is missing
- **Then** the text reports the outside file without reverting it or delivering it as accepted work, and reports
  attribution as unverifiable or coverage as limited

### [AC-07] Clean-break rename

- **Given** the repository after the change
- **When** `rg -n '(^|[^-_a-z])uiux[-_]improve\b' --hidden -g '!.git' -g '!specs/' -g '!docs/materials/'` runs
  (the bare old name, not `app-uiux-improve`, `app_uiux_improve` or the kept `uiux-improvement` IDs)
- **Then** it reports no match (exit 1), `pyproject.toml` declares
  `app-uiux-improve = "devkit_catalog.app_uiux_improve"`, the `.devkit/architecture.toml` data root is
  `app_uiux_improve`, and no `uiux-improve` entry point, bundle, skill or `uiux_improve` module remains

### [AC-08] Size, self-containment and independent installation

- **Given** the renamed bundle
- **When** the catalog integration tests and the installed-consumer E2E test run
- **Then** every Markdown file under the skill directory is at most 12,288 bytes and contains no governance ID, both
  tests pass (exit 0), and the built-wheel consumer selects `app-uiux-improve` without `devkit-agt`, `devkit-docs` or
  `devkit-spec` installed

### [AC-09] No delivery authority

- **Given** the installed `SKILL.md` and `references/orchestration.md`
- **When** the bundle is selected, invoked or delegates to Impeccable
- **Then** the text grants no commit, integration or publication permission

### [AC-10] OOUX documents as conditional, read-only sources

- **Given** the installed `references/design-guidance.md` and `references/orchestration.md`
- **When** the project has a glossary, object register or UX documents, or has none
- **Then** the text frames from the present files and cites their paths read-only in the brief, frames in conversation
  without them, reports after an accepted change each OOUX document the change made stale, edits none of them in the
  skill run, and names no SDD stage or namespace-selection concept

### [AC-11] Human usage guide outside the agent assets

- **Given** `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/README.md`
- **When** the catalog integration tests and the installed-consumer E2E test run
- **Then** the guide exists with the eight sections of the plan's guide contents, contains no governance ID, is linked
  from `packages/devkit-catalog/README.md`, is linked or named by no file under the skill directory nor `bundle.toml`
  (a pointer to Impeccable's own README stays allowed), the synced managed set is `bundle.toml` plus the skill files,
  and no projected skill directory or managed directory holds `README.md`

## 5. Assumptions

- The proposal's premises hold on the Development base 83b7c0a8: `git ls-tree -r --name-only v0.1.5` lists no `uiux`
  path, `main` has not moved past the handoff, and the tracked references match planning evidence §2.
- Upstream Impeccable facts come from planning evidence §3 at upstream commit a49e3e9b. The file that upstream's
  unprefixed ignore block targets and the installer's non-interactive options stay unverified; the instructions are
  safe either way because the coordinator shows ignore lines first and hands interactive installers to the user.
- Child loading of Impeccable is host-dependent and unverified on every host (planning evidence §4); the instructions
  route a failed load to the user's session.
- The renamed entry point needs no `uv.lock` change, because the lockfile records no entry points; Development checks
  this after `uv sync`.
- Naming stays a Planning decision: the user chose `app-uiux-improve` over `software-ui-improve` and
  `ooux-ui-improve`.
- The "Superseded in part by" pointer in `ADR-uiux-improvement-workflow-boundary` is the Host's post-handoff
  responsibility; Development's only edit to that ADR is the clause 1 bundle-name repair.
