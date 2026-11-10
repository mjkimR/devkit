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
- **Rule 9** (Role authority): unchanged for local roles; state that the delegated session is governed by rules 15–17.
- **Rule 10** (Host limits): add: IF Impeccable is unavailable, THEN the coordinator MUST name the upstream install
  routes, install nothing and continue inline when the user wants.
- **Rule 13** (Independent installation): renamed E2E test path.
- **Rule 14** (Artifact preservation): add: WHEN a delegated session creates or changes Impeccable project context
  files, the coordinator MUST report them as consumer-owned with upstream's retention guidance and MUST NOT delete,
  move or git-ignore them without the user's direction.
- **New rule 15** (User-selected delegation): The coordinator MUST start an Impeccable session only when the user
  selects that track; an installed Impeccable permits an offer.
- **New rule 16** (Session brief): WHEN delegating to Impeccable, the coordinator MUST pass a self-contained brief
  (goal, framing, edit list, unchanged concerns, context-file permission, commands excluding `live`, stop condition,
  expected return), MUST record the working-tree state and MUST make no product edits until the session returns;
  the session leaves index, HEAD and files outside the edit list unchanged.
- **New rule 17** (Coordinator acceptance): WHEN a session returns, the coordinator MUST compare the working tree with
  the recorded state, take only in-list changes into verification and report out-of-list changes without reverting
  or deleting them.
- **Section 4**: `uv run devkit add <name>`, `/<name> <goal>`, registration `<name> = "devkit_catalog.<module>"`; the
  orchestration reference adds the Impeccable brief; the session return lists changed files, commands run, detector
  or critique results, degraded coverage and blockers.

Restate `PADR-impeccable-session-authority` at rules 3, 9, 10, 14, 15, 16 and 17 with the traces its clauses name.

## 2. Use case: UC-improve-an-interface-and-user-flow

Keep the ID and main scenario; update the entrypoint. Add:

- Step 3 wording: the agent frames the affected objects when the request changes structure or flow, then develops
  useful design perspectives.
- **3c.** The user selects Impeccable: the agent writes the brief, delegates one session and pauses its own edits;
  after the return it accepts in-list changes and resumes at step 6.
- **3d.** Impeccable is selected but unavailable: the agent names the install routes and installs nothing; the user
  installs it (resume at 3c) or continues inline (resume at step 4).
- **6b.** The session changed a file outside its edit list or created Impeccable project files: the agent reports them
  as consumer-owned and unaccepted where applicable, and continues with the accepted changes.
- Postconditions: consumer-owned files remain in place unless the user directed otherwise.
- Scenarios: one for delegated execution with acceptance (3c, 6b) and one for unavailable Impeccable (3d).

## 3. Architecture: ARCH-05-2-components

Rename the bundle and `devkit_catalog/<module>/bundle/` path in the content-bundle paragraph. The bundle still adds no
runtime dependency or shared orchestration module; Impeccable stays an optional, user-installed external skill.

## 4. Decision: ADR-uiux-improvement-workflow-boundary

`PADR-impeccable-session-authority` promotes with `supersedes: [ADR-uiux-improvement-workflow-boundary]`. The handoff
inserts "Superseded in part by" below the heading; Development replaces its summary text with: Decision Outcome
clause 2's coordinator-only continuation of requested implementation now admits one user-selected, brief-bounded
Impeccable session. The ADR stays `accepted`. Clause 1's bundle name is repaired to `<name>` without changing the
decision.
