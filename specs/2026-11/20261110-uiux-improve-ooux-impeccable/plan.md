---
id: PLAN-uiux-improve-ooux-impeccable
spec: SPEC-uiux-improve-ooux-impeccable
---

# Technical Plan: `SPEC-uiux-improve-ooux-impeccable` OOUX-framed UI/UX improvement and Impeccable delegation

## 1. Constitution & Invariant Review

- `ADR-impeccable-session-authority` (accepted, promoted at handoff) carries the only authority change: one
  user-selected, brief-bounded Impeccable session may edit listed product files under coordinator acceptance, and the
  coordinator takes setup and cleanup steps only on the user's request. It supersedes Decision Outcome clause 2 of
  `ADR-uiux-improvement-workflow-boundary` in part; no further ADR is needed.
- `CAP-DLV-uiux-improvement` rules 3 and 9 keep their wording; rules 15 to 19 are added at reconcile
  (`PROP-uiux-improve-ooux-impeccable-target` §1). Rule 13 (independent installation) constrains the OOUX reading: the
  skill names the document paths as an optional convention and depends on no `devkit-docs` concept.
- `ARCH-05-2-components` permits content-only catalog modules with empty initializers under
  `devkit_catalog/<module>/bundle/`. The rename keeps that layout; no runtime dependency, feature edge or
  architecture declaration changes beyond the renamed `data_roots` entry.
- Bundle self-containment (agent-asset writing): no governance ID in bundled skill Markdown, which stays at most
  12,288 bytes per file.

## 2. Architecture Overview & Impact

- **Rename (AC-07)**: `git mv` the module `devkit_catalog/uiux_improve/` to `devkit_catalog/app_uiux_improve/` and
  the skill directory to `bundle/skills/app-uiux-improve/`. `bundle.toml` takes `name`, asset `id`, `source` and preset
  `core` entries `app-uiux-improve`; `SKILL.md` frontmatter `name` matches. `pyproject.toml` declares
  `app-uiux-improve = "devkit_catalog.app_uiux_improve"`; `.devkit/architecture.toml` `data_roots` replaces
  `uiux_improve` with `app_uiux_improve`. The integration test moves to `test_app_uiux_improve.py` and the E2E
  directory to `tests/e2e/bundles/app_uiux_improve/`. No alias or compatibility entry is kept. `uv sync` refreshes the
  editable install's entry points; `uv.lock` stays unchanged.
- **Instructions (AC-01 to AC-06, AC-09, AC-10)**: `SKILL.md` keeps recovery, inspection, review-only handling and
  reporting, and orders the work as framing, track choice (inline default or selected Impeccable), execution and
  verification. `references/design-guidance.md` adds ORCA framing with conditional sources and baseline craft checks.
  `references/orchestration.md` adds the Impeccable section: selection, availability, workflow first, brief, command
  routing, `shape`, pause, acceptance, project files and user-requested conveniences. The four local roles stay
  unchanged on both tracks.
- **Usage guide (AC-11)**: new `bundle/README.md` beside `bundle.toml`. Sync deploys only `bundle.toml` and declared
  assets (the distribution inventory copies `bundle.toml` and each asset source), so the guide stays in the source tree
  and the wheel. No agent-read file links it; `packages/devkit-catalog/README.md` links it.
- **Quick references**: `packages/devkit-catalog/README.md` (table row and section), `guides/install/bundle-recommendations.md`
  (row) and `ARCH-05-2-components` (content-bundle paragraph) name the new bundle and path.
- **Living Spec (reconcile)**: `CAP-DLV-uiux-improvement`, `UC-improve-an-interface-and-user-flow`,
  `ARCH-05-2-components` and the clause 1 bundle-name repair in `ADR-uiux-improvement-workflow-boundary`, per
  `PROP-uiux-improve-ooux-impeccable-target`.

## 3. Component & Interface Design

```text
app-uiux-improve/SKILL.md            (entry: boundaries, procedure, completion)
  -> references/design-guidance.md   when framing or choosing the design direction
  -> references/orchestration.md     before delegating to a local role or to Impeccable
       -> roles/{designer,unconventional-designer,reference-researcher,critic}.md
bundle/README.md                     (human guide; linked only from the catalog README)
```

### 3.1 Per-task flow in `SKILL.md`

1. Recover the goal and complete the consumer workflow's pre-implementation steps (branch, worktree, required
   records) before product edits or delegation.
2. Frame in proportion: a local change (one component, one state, copy or spacing) proceeds without an ORCA pass; a
   change that adds, merges or reorders views or flows names the affected objects, relationships, CTAs and attributes
   with their states first; a review-only request may use the framing as a lens and ends with findings and no product
   edits. Framing covers the objects the request touches, never an exhaustive audit.
3. Choose the track: inline by default (local roles optional on both tracks); Impeccable only on the user's selection.
4. Delegated track: write the brief, route the command, pause product edits until the session returns.
5. Accept and continue: compare with the recorded base, verify accepted changes, report outside-list changes, session
   output, context files and stale OOUX documents, then continue the consumer workflow.
6. Optional setup and cleanup only on the user's request.

A new screen in a consumer whose workflow drafts screens before code is drafted there first; the skill states this as
following the consumer workflow without naming its records or stages.

### 3.2 `references/design-guidance.md` additions

- ORCA framing: objects are domain nouns users think in ("Invoice", not "Table"); relationships give navigation
  paths; CTAs sit on the object they act on; attributes separate identifiers from metadata. One worked two-object
  example.
- Framing sources, read only where present: glossary (`docs/steering/glossary.md`, or a package-level glossary beside
  the affected code), object register (`docs/steering/ux-objects.md`, or a package-level register), UX documents of
  the affected screens (`docs/ux/<area>/`). A partial set is used as far as it goes; without them, frame in
  conversation. Framing never writes them.
- Baseline craft checks: readable contrast for secondary text, a consistent type scale, no decorative gradients or
  nested containers without a purpose, empty/loading/error states for every changed view.
- Provenance keeps Impeccable as a reference and states that nothing is copied.

### 3.3 `references/orchestration.md` Impeccable section

1. Selection: without the user's selection, no session and no loading or invoking Impeccable in the coordinator's
   context; an installed Impeccable permits an offer; user-installed hook output is consumer check evidence.
2. Availability: name `npx impeccable install`, `/plugin marketplace add pbakaus/impeccable` then install from
   `/plugin`, or a manual copy of `skills/impeccable`. On request, run only a route that needs no prompt answers (the
   manual copy, or the installer with non-interactive options whose values the user stated, where upstream documents
   them); otherwise hand the user the exact command. Never install on own initiative; the user can continue inline.
3. Workflow first: pre-implementation steps before delegating.
4. Brief fields: goal; framing result citing OOUX documents by path read-only (or the conversation framing); consumer
   drafts or specifications by path read-only; absolute working directory; recorded base (HEAD, status and content
   hashes of listed files under Git, the listed files' hashes otherwise); edit list; unchanged files and concerns (data
   schema, business logic, dependencies, OOUX documents, files with uncommitted user edits unless included);
   context-file permission (`PRODUCT.md`/`DESIGN.md` only on explicit direction; `.impeccable/design.json`,
   `.impeccable/config.json`, `.impeccable/surfaces/` only when listed); commands; stop condition; expected return
   (changed files, commands run, detector or audit results, session output, degraded coverage, blockers).
5. Routing: a fresh child runs only refinement commands that need no answers (`polish`, `audit`, narrow refinement
   such as `distill`, `typeset`, `layout`), loading Impeccable through the host's skill mechanism; a load failure or
   upstream question returns as a blocker, never answered; new work, `init`, `shape`, `critique` and blocked commands
   run in a session the user operates from the same brief. No route uses `live`.
6. `shape`: the coordinator's framing takes its structural role for a child; the user may run `shape` with the brief.
7. Pause: no product edits until the session returns.
8. Acceptance: compare with the base; listed product-file changes go to verification; session output under
   `.impeccable/` and any other change are reported without reverting or deleting; moved HEAD, missing base or
   unobservable ignored paths are unverifiable attribution or limited coverage; stale OOUX documents are reported and
   not edited in the skill run.
9. Project files: `PRODUCT.md`, `DESIGN.md` and shared `.impeccable/` files are consumer-owned; report created or
   changed ones and point to upstream's "Project files and git" guidance. `PRODUCT.md` anchor: a short reference
   section naming the OOUX documents by path, copying none of their content.
10. User-requested conveniences: install (item 2); ignore entries confined to `.impeccable/` shown first; remove
    named runtime or session output; add the anchor. `PRODUCT.md` and `DESIGN.md` are never part of cleanup unless
    named. Each goes through the consumer workflow and host approvals.

### 3.4 Usage guide contents (`bundle/README.md`)

English, no governance ID, outside the agent-asset rules, in this order:

1. What the bundle is for (software interfaces) and what it does not do.
2. One-time setup: selecting the bundle, installing Impeccable (three upstream routes, or the coordinator on
   request), running `init` and adding the OOUX anchor to `PRODUCT.md`.
3. Per-task flow with one example request.
4. The two launch routes and what the user reports back.
5. What the coordinator does and does not do.
6. OOUX document linkage.
7. Opt-in setup and cleanup, with the `PRODUCT.md` and `DESIGN.md` exclusion.
8. Troubleshooting.

## 5. Error Handling & Edge Cases

- Size budget: `SKILL.md` and `orchestration.md` grow; each file must stay at most 12,288 bytes. If
  `orchestration.md` would exceed it, move the Impeccable section into a third conditional reference
  (`references/impeccable.md`) linked from `SKILL.md` with its read condition.
- A guide link check must not reject a pointer to Impeccable's own README; it rejects only `../README.md`,
  `bundle/README.md` and similar paths to the bundle's guide.

## 6. Verification & Test Plan

- AC-07: `rg` command in AC-07; `test_app_uiux_improve.py` paths and managed/projected names; entry-point load through
  sync in the integration test.
- AC-01 to AC-06, AC-09, AC-10: `assert_rule` checks in
  `test_entry_preserves_improvement_scope_and_consumer_authority` and a new delegation test over `SKILL.md`,
  `references/design-guidance.md` and `references/orchestration.md`.
- AC-08: existing size and governance-ID scan over the skill directory; installed-consumer E2E under
  `tests/e2e/bundles/app_uiux_improve/`.
- AC-11: guide test (sections, no governance ID, catalog README link, no link from skill files or `bundle.toml`,
  managed set and projected directories hold no `README.md`); the E2E asserts the same absence.
- Commands: `just lint devkit-catalog`, `just check devkit-catalog`, `just test devkit-catalog integration`,
  `just test-affected` (unit-integration), `just test-affected --tier e2e`, `just rules-check`,
  `uv run devkit rules check --phase hygiene` on the skill directory and the agent-asset ID scan. `just test-dist`
  only if dist-facing paths change (none planned). `devkit generated check` if a generated artifact is affected.
