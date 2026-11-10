---
id: PROP-uiux-improve-ooux-impeccable-target
title: Target Living Spec for OOUX-framed UI/UX improvement and Impeccable delegation
summary: "Prospective capability, use-case, component and decision updates for the renamed software-interface UI/UX skill, OOUX framing from consumer documents, bounded Impeccable sessions and user-requested setup."
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
The qualified bundle and skill name is `app-uiux-improve` (module `app_uiux_improve`).

## 1. Capability: CAP-DLV-uiux-improvement

Keep the ID. Retitle to name software interfaces (for example "Software interface UI/UX improvement"). Update the
summary, entrypoint and section 1 to the `app-uiux-improve` bundle, OOUX framing and optional Impeccable delegation,
and cite `PADR-impeccable-session-authority` beside `ADR-uiux-improvement-workflow-boundary`.

- **Scope**: In-Scope adds proportionate object framing (from the consumer's OOUX documents when present),
  user-selected Impeccable delegation and user-requested Impeccable setup and cleanup. Out-of-Scope adds Impeccable's
  installer, commands, hooks, detector and file conventions as upstream contracts and non-software design domains.
  Scope Excluded keeps automatic companion skill invocation and adds vendored external prompt text.
- **Rule 1** (Opt-in distribution): `app-uiux-improve:core`; one skill and four local role files; the bundle's human
  usage guide (`bundle/README.md`) is not deployed; test path
  `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`.
- **Rule 3** (Consumer authority): unchanged wording; it also covers changes accepted from a delegated session.
- **Rule 4** (Goal-driven improvement): add the framing clause: WHEN a request adds, merges or reorders views or
  flows, the coordinator SHOULD name the affected objects, relationships, CTAs and attributes before layout or
  styling; a local change proceeds without that pass. WHERE the consumer keeps a glossary, object register or UX
  documents, the framing SHOULD read them, and otherwise it frames in conversation. The skill names these paths as an
  optional convention and depends on no `devkit-docs` concept (rule 13).
- **Rule 9** (Role authority): unchanged for local roles; state that the delegated session is governed by rules 15–18.
- **Rule 10** (Host limits): add: IF Impeccable is unavailable, THEN the coordinator MUST name the upstream install
  routes and continue inline when the user wants; installation follows rule 19.
- **Rule 13** (Independent installation): E2E test path `packages/devkit-catalog/tests/e2e/bundles/app_uiux_improve/`.
- **Rule 14** (Artifact preservation): unchanged sync rule and tests.
- **New rule 15** (User-selected delegation): WHERE the user has not selected the Impeccable track, the coordinator
  MUST NOT start an Impeccable session or load or invoke Impeccable in its own context; an installed Impeccable
  permits an offer, and output of a hook the user installed is consumer check evidence.
- **New rule 16** (Session brief and routing): WHEN delegating to Impeccable, the coordinator MUST complete the
  consumer's pre-implementation workflow steps, pass a self-contained brief (goal, the framing result citing the OOUX
  documents by path read-only or the conversation framing, consumer drafts or specifications by path read-only,
  absolute working directory, recorded base, edit list, unchanged concerns, context-file permission with `PRODUCT.md`
  or `DESIGN.md` only on the user's explicit direction, routed commands excluding `live`, stop condition, expected
  return) and make no product edits until the session returns. A fresh child MUST run only refinement commands that
  need no user answers, loading Impeccable through the host's skill mechanism, and MUST return any upstream question
  or load failure as a blocker; new work, `init`, `shape`, `critique` and any blocked command run in a session the
  user operates. The session leaves index, HEAD and files outside its permitted classes unchanged.
- **New rule 17** (Coordinator acceptance): WHEN a session returns, the coordinator MUST compare the working directory
  with the recorded base, take only listed product-file changes into verification, report session output and other
  changes without reverting or deleting them on its own initiative, and report a moved HEAD, missing base or
  unobservable ignored path as unverifiable attribution or limited coverage. It MUST report each consumer OOUX
  document (glossary, object register or UX document) the accepted change made stale; the skill run MUST NOT edit
  them, and their update follows the consumer workflow's own step.
- **New rule 18** (Consumer context files): WHEN a session creates or changes `PRODUCT.md`, `DESIGN.md` or shared
  `.impeccable/` context files, the coordinator MUST report them as consumer-owned with upstream's retention guidance.
- **New rule 19** (User-requested setup and cleanup): WHERE the user requests it, the coordinator MAY install
  Impeccable through an upstream route that needs no prompt answers (otherwise it hands the user the exact command),
  add upstream's recommended ignore entries confined to `.impeccable/` paths after showing the exact lines, remove
  Impeccable runtime or session output the user names, or add to `PRODUCT.md` a reference section naming the
  consumer's OOUX documents without copying them; it MUST NOT take any of these actions on its own initiative.
  `PRODUCT.md` and `DESIGN.md` MUST change, by the coordinator or a permitted session, only on the user's explicit
  direction. The action follows rule 3.
- **Section 4**: the bundle's human usage guide is `bundle/README.md`, linked from the catalog README and from no
  agent-read file; `uv run devkit add app-uiux-improve`, `/app-uiux-improve <goal>`, registration `app-uiux-improve =
  "devkit_catalog.app_uiux_improve"`; the orchestration reference adds the Impeccable brief; the session return lists
  changed files, commands run, detector or audit results, session output, degraded coverage and blockers. Restate "The
  coordinator owns synthesis, retained output and product changes" as "owns synthesis, acceptance and retained output;
  product changes follow rules 3, 16, 17 and 19".

Restate `PADR-impeccable-session-authority` at rules 3, 9, 10, 15, 16, 17, 18 and 19 with the traces its clauses
name.

## 2. Use case: UC-improve-an-interface-and-user-flow

Keep the ID and main scenario; update the entrypoint. Add:

- Step 3 wording: the agent frames the affected objects when the request changes structure or flow, from the project's
  OOUX documents when present, then develops useful design perspectives.
- **3c.** The user selects Impeccable: the agent completes pre-implementation workflow steps, writes the brief and
  delegates one session (a fresh child for refinement, a session the user operates for interactive commands or when
  the child cannot load Impeccable), pausing its own edits; after the return it accepts listed product-file changes
  and resumes at step 6.
- **3d.** Impeccable is selected but unavailable: the agent names the install routes; the user installs it, or asks
  the agent to run a route that needs no prompt answers (resume at 3c), or continues inline (resume at step 4).
- **6b.** The session changed a file outside its edit list, wrote session output or created consumer context files, or
  attribution is unverifiable: the agent reports each class, reverts and deletes nothing on its own initiative, and
  continues with the accepted changes.
- **6c.** The accepted change made an OOUX document (glossary, object register or UX document) stale: the agent names
  it, edits none in the skill run, and the consumer workflow's own step updates it.
- **7a.** The user asks for cleanup or ignore entries: the agent removes only the Impeccable output the user names or
  adds upstream's ignore entries confined to `.impeccable/` after showing them, leaves `PRODUCT.md` and `DESIGN.md`
  unless named, and continues the consumer workflow.
- Postconditions: consumer-owned files remain in place unless the user directed otherwise.
- Scenarios: one for delegated execution with acceptance (3c, 6b, 6c), one for unavailable Impeccable (3d) and one for
  user-requested cleanup (7a).

## 3. Architecture: ARCH-05-2-components

Rename the bundle to `app-uiux-improve` and its path to `devkit_catalog/app_uiux_improve/bundle/` in the
content-bundle paragraph. The bundle still adds no
runtime dependency or shared orchestration module; Impeccable stays an optional external skill the user installs or
asks the coordinator to install. The bundle directory also holds a human usage guide that sync does not deploy.

## 4. Decision: ADR-uiux-improvement-workflow-boundary

`PADR-impeccable-session-authority` promotes with `supersedes: [ADR-uiux-improvement-workflow-boundary]`. The handoff
inserts "Superseded in part by" below the heading; the Host's post-handoff check clarifies it to name the replaced
clause: Decision Outcome clause 2's coordinator-only continuation of requested implementation now admits one
user-selected, brief-bounded Impeccable session. The ADR stays `accepted`; clause 4 stays in force for local roles.
Development repairs clause 1's bundle name to `app-uiux-improve` without changing the decision.
