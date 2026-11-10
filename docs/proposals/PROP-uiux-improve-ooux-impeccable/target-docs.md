---
id: PROP-uiux-improve-ooux-impeccable-target
title: Target Living Spec for OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Prospective capability, use-case, component and decision updates for the renamed software-interface UI/UX skill, proportionate OOUX framing and bounded Impeccable sessions."
status: draft
proposal: PROP-uiux-improve-ooux-impeccable
created_at: 2026-11-10
targets:
  - file: docs/capabilities/delivery/CAP-DLV-uiux-improvement.md
  - file: docs/usecases/delivery/UC-improve-an-interface-and-user-flow.md
  - file: docs/architecture/ARCH-05-2-components.md
  - file: docs/decisions/2026-11/20261105-uiux-improvement-workflow-boundary.md
---

# [PROP-uiux-improve-ooux-impeccable-target] Target Living Spec for OOUX-framed UI/UX improvement and Impeccable delegation

These are prospective changes after implementation. Existing Living Spec contracts remain in force during Planning.
`<name>` stands for the qualified name the user chooses (recommended: `app-uiux-improve`, module `app_uiux_improve`).

## 1. Capability: CAP-DLV-uiux-improvement

Keep the ID. Retitle to name software interfaces (for example "Software interface UI/UX improvement"). Update the
summary, entrypoint and section 1 to the qualified bundle, OOUX framing and optional Impeccable delegation, and cite
`PADR-impeccable-session-authority` beside `ADR-uiux-improvement-workflow-boundary`.

- **Scope**: In-Scope adds proportionate object framing and user-selected Impeccable delegation. Out-of-Scope adds
  Impeccable's installation, commands, hooks, detector and file conventions (upstream) and non-software design domains.
  Scope Excluded keeps automatic companion skill invocation and adds vendored external prompt text.
- **Rule 1** (Opt-in distribution): `<name>:core`; one skill and four local role files; renamed test path.
- **Rule 3** (Consumer authority): unchanged wording; it also covers changes accepted from a delegated session.
- **Rule 4** (Goal-driven improvement): add the framing clause: WHEN a request adds, merges or reorders views or flows,
  the coordinator SHOULD name the affected objects, relationships, CTAs and attributes before layout or styling; a
  local change proceeds without that pass.
- **Rule 9** (Role authority): unchanged for local roles; state that the delegated session is governed by rules 15–18.
- **Rule 10** (Host limits): add: IF Impeccable is unavailable, THEN the coordinator MUST name the upstream install
  routes, install nothing and continue inline when the user wants.
- **Rule 13** (Independent installation): renamed E2E test path.
- **Rule 14** (Artifact preservation): unchanged sync rule and tests.
- **New rule 15** (User-selected delegation): WHERE the user has not selected the Impeccable track, the coordinator
  MUST NOT start an Impeccable session or load or invoke Impeccable in its own context; an installed Impeccable
  permits an offer, and output of a hook the user installed is consumer check evidence.
- **New rule 16** (Session brief and routing): WHEN delegating to Impeccable, the coordinator MUST complete the
  consumer's pre-implementation workflow steps, pass a self-contained brief (goal, framing, absolute working
  directory, recorded base, edit list, unchanged concerns, context-file permission, routed commands excluding `live`,
  stop condition, expected return) and make no product edits until the session returns. A fresh child MUST run only
  refinement commands that need no user answers and MUST return any upstream question as a blocker; new work,
  `init`, `shape` and `critique` run in a session the user operates. The session leaves index, HEAD and files outside
  its permitted classes unchanged.
- **New rule 17** (Coordinator acceptance): WHEN a session returns, the coordinator MUST compare the working directory
  with the recorded base, take only listed product-file changes into verification, report session output and other
  changes without reverting or deleting them, and report a moved HEAD, missing base or unobservable ignored path as
  unverifiable attribution or limited coverage.
- **New rule 18** (Consumer context files): WHEN a session creates or changes `PRODUCT.md`, `DESIGN.md` or shared
  `.impeccable/` context files, the coordinator MUST report them as consumer-owned with upstream's retention guidance
  and MUST NOT delete, move or git-ignore them without the user's direction.
- **Section 4**: `uv run devkit add <name>`, `/<name> <goal>`, registration `<name> = "devkit_catalog.<module>"`; the
  orchestration reference adds the Impeccable brief; the session return lists changed files, commands run, detector
  or audit results, session output, degraded coverage and blockers. Restate "The coordinator owns synthesis, retained
  output and product changes" as "owns synthesis, acceptance and retained output; product changes follow rules 3,
  16 and 17".

Restate `PADR-impeccable-session-authority` at rules 3, 9, 10, 15, 16, 17 and 18 with the traces its clauses name.

## 2. Use case: UC-improve-an-interface-and-user-flow

Keep the ID and main scenario; update the entrypoint. Add:

- Step 3 wording: the agent frames the affected objects when the request changes structure or flow, then develops
  useful design perspectives.
- **3c.** The user selects Impeccable: the agent completes pre-implementation workflow steps, writes the brief and
  delegates one session (a fresh child for refinement, a session the user operates for interactive commands), pausing
  its own edits; after the return it accepts listed product-file changes and resumes at step 6.
- **3d.** Impeccable is selected but unavailable: the agent names the install routes and installs nothing; the user
  installs it (resume at 3c) or continues inline (resume at step 4).
- **6b.** The session changed a file outside its edit list, wrote session output or created consumer context files, or
  attribution is unverifiable: the agent reports each class, reverts and deletes nothing, and continues with the
  accepted changes.
- Postconditions: consumer-owned files remain in place unless the user directed otherwise.
- Scenarios: one for delegated execution with acceptance (3c, 6b) and one for unavailable Impeccable (3d).

## 3. Architecture: ARCH-05-2-components

Rename the bundle and `devkit_catalog/<module>/bundle/` path in the content-bundle paragraph. The bundle still adds no
runtime dependency or shared orchestration module; Impeccable stays an optional, user-installed external skill.

## 4. Decision: ADR-uiux-improvement-workflow-boundary

`PADR-impeccable-session-authority` promotes with `supersedes: [ADR-uiux-improvement-workflow-boundary]`. The handoff
inserts "Superseded in part by" below the heading; the Host's post-handoff check clarifies it to name the replaced
clause: Decision Outcome clause 2's coordinator-only continuation of requested implementation now admits one
user-selected, brief-bounded Impeccable session. The ADR stays `accepted`; clause 4 stays in force for local roles. Development repairs clause 1's bundle name
to `<name>` without changing the decision.
