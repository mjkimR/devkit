---
id: UC-improve-an-interface-and-user-flow
title: Improve an interface and user flow
summary: "An AI coding agent uses an explicitly invoked UI/UX skill to improve a software interface task, framing affected objects, optionally delegating to a user-selected Impeccable session, and implements through a task-approved route with actual verification and limits."
area: delivery
primary_actor: AI coding agent
supporting_actors: [Product owner, Optional design and research subagents, Optional Impeccable session]
status: active
capabilities:
  - CAP-DLV-uiux-improvement
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/bundle/skills/app-uiux-improve/SKILL.md
---

# [UC-improve-an-interface-and-user-flow] Improve an interface and user flow

## 1. Goal

- **Goal**: improve the supplied interface or flow so that it serves the intended user task more clearly and usefully.
- **Scope**: one bounded UI/UX improvement request for a software interface.
- **Trigger**: the product owner explicitly invokes the improvement entry.
- **Preconditions**: the selected bundle and ordinary project environment are available.

## 2. Main Success Scenario

1. The agent recovers the target, intended outcome, relevant artifacts, constraints and the user's task route choice (`CAP-DLV-uiux-improvement`).
2. The agent inspects the representative task path and affected interface states (`CAP-DLV-uiux-improvement`).
3. The agent frames the affected objects when the request changes structure or flow, from the project's OOUX
   documents when present, then develops useful design perspectives for the requested improvement
   (`CAP-DLV-uiux-improvement`).
4. The agent synthesizes a coherent direction and its relevant tradeoffs (`CAP-DLV-uiux-improvement`).
5. The agent applies requested changes through the route the user authorized for the task (`CAP-DLV-uiux-improvement`).
6. The agent checks the changed interface and representative interactions (`CAP-DLV-uiux-improvement`).
7. The agent reports the actual improvement, selected route, verification, documentation follow-up and remaining authority (`CAP-DLV-uiux-improvement`).

## 3. Extensions

- **1a.** A decision-changing artifact or constraint is missing: the agent reuses known context and asks only for
  that missing input; dependent work waits and resumes at step 1.
- **1b.** No exact prior route approval or answer channel exists: read-only inspection is retained and dependent
  product edits and write-capable delegation wait; resumes at step 1 when the user chooses a route.
- **1c.** The user chooses the consumer workflow: the agent follows its pre-implementation, required review and
  delivery steps; resumes at step 2. An exact prior route instruction is reused without another identical prompt.
- **2a.** The running interface cannot be inspected: the agent uses available screenshot, code or text evidence and
  names its coverage; continues at step 3 without claiming actual interaction verification.
- **3a.** A small request needs no team or research: the agent works inline; resumes at step 4.
- **3b.** Fresh children are unavailable: the agent uses useful inline passes and discloses their shared context;
  resumes at step 4 without fabricated role findings.
- **3c.** The user selects Impeccable for craft work: the agent keeps its framing and local perspectives and resumes at
  step 4; implementation follows 5c.
- **3d.** Impeccable is selected but unavailable: the agent names the upstream install routes; the user installs it,
  or asks the agent to run a route that needs no prompt answers (resumes at 3c), or continues inline (resumes at
  step 4 without 5c).
- **4a.** A product or scope decision exceeds existing authority: the agent presents the concrete choice and preserves
  independent useful work; dependent work waits and resumes at step 4 after the user's decision.
- **5a.** Review-only request: the agent returns findings without product edits; the use case ends with the requested review.
- **5b.** A workflow approval or tool is missing: the agent preserves useful partial work and names the blocker;
  the use case ends pending that requirement.
- **5c.** Impeccable is selected: the agent completes pre-implementation steps required by the selected route,
  writes the brief and delegates one session before or after its inline changes. Answer-free refinement uses a
  fresh child; interactive commands use confirmed question relay when the actual host/project capabilities support
  it, or the user's session otherwise. The agent pauses its own product edits, then accepts listed changes and
  resumes at step 6.
- **5d.** A question, pre-fill or affected answer lacks confirmation, another question appears, or relevant source
  facts change: dependent writes wait while the agent presents the complete packet or refreshes affected answers;
  resumes at 5c only after the user confirms. One explicit confirmation can cover the whole visible packet.
- **5e.** Native loading, same-child continuation or required nested roles are unavailable or unverified, or
  continuation state is lost: the agent reports observed availability/current-project enablement and hands the
  brief to the user's session. It loads no plugin-cache files, changes no enablement without a setup request and
  reconstructs no writing child; resumes at 5c after the user's report.
- **6a.** A check exposes a defect: the agent fixes it within scope and repeats the affected check; resumes at step 6.
- **6b.** The session changed a file outside its edit list, wrote session output or created or changed consumer
  context files, or attribution is unverifiable: the agent reports each class, reverts and deletes nothing on its own
  initiative, and continues with the accepted changes; resumes at step 6.
- **6c.** The accepted change made an OOUX document (glossary, object register or UX document) stale: the agent names
  it, its affected statement and the concrete follow-up through the documentation process where present or a
  separate documentation task otherwise. The run edits none and creates no follow-up record without a separate
  request; resumes at step 7.
- **7a.** The user asks for cleanup or ignore entries: the agent removes only the Impeccable output the user names or
  adds upstream's ignore entries confined to `.impeccable/` after showing them, leaves `PRODUCT.md` and `DESIGN.md`
  unless named, and continues through the selected route and host approvals; the use case ends with the requested
  change reported.

- **7b.** Git effects lack current task authority: the agent presents the verified result and asks once for the
  named remaining effects before acting; existing exact authority is reused and route choice grants none. The use
  case remains pending those effects.

## 4. Postconditions

- **Success guarantee**: requested changes and actual verification are reported; narrower review requests return
  findings with no product edits, and the result respects the requested destination and project ownership.
  The chosen workflow retains its required steps and reviews; the outside route retains checks without creating
  workflow-specific records. Consumer-owned files, including Impeccable's project files and the OOUX documents, remain in place unless the user
  directed otherwise.
- **Minimal guarantee**: unavailable work and checks remain explicit; no native isolation, workflow approval,
  publication or real-user quality result is invented, and no change outside a session's edit list is delivered as
  accepted work.

## 5. Acceptance Criteria

Rules: explicit invocation, consumer authority, goal-driven improvement, narrower request, optional perspectives,
role packet, independent context, host limits, verification, qualified completion, user-selected delegation, session
brief and routing, coordinator acceptance, consumer context files and user-requested setup and cleanup, task route choice, scope growth and Git effects.

### Scenario 1: Carry a flow and visual improvement through delivery

- **Covers**: main success scenario, 6a
- **Given**: a supplied interface, user goal and authorized improvement scope.
- **When**: the agent applies the selected direction through the selected route.
- **Then**: the changed interface and representative task checks are reported, with relevant defects fixed and rechecked.

### Scenario 2: Ask only for a consequential missing input

- **Covers**: 1a, 4a
- **Given**: known facts and one missing input or product choice that changes the authorized work.
- **When**: the agent reaches that choice.
- **Then**: it presents the concrete gap, preserves independent useful work and waits only on dependent actions.

### Scenario 3: Qualify screenshot-only coverage

- **Covers**: 2a
- **Given**: screenshots or code but no running UI tools.
- **When**: the agent assesses or changes the interface.
- **Then**: the result names the evidence and unverified interaction coverage without claiming actual usage checks.

### Scenario 4: Keep optional perspectives proportionate

- **Covers**: 3a, 3b
- **Given**: a narrow request or unavailable fresh children.
- **When**: the agent chooses useful design passes.
- **Then**: it can finish inline, describes shared-context limits and imposes no fixed cast, score or comparison program.

### Scenario 5: Honor a review-only request

- **Covers**: 5a
- **Given**: an explicit request for findings only.
- **When**: the agent reviews the supplied interface.
- **Then**: it returns supported findings, possibly zero, with no product source edits.

### Scenario 6: Preserve blocked improvement work

- **Covers**: 5b
- **Given**: a concrete missing approval, artifact or tool prevents completion.
- **When**: the agent reaches the dependent action.
- **Then**: it retains useful partial work and names that blocker without treating requested implementation as complete.

### Scenario 7: Accept a delegated Impeccable session

- **Covers**: 3c, 5c, 6b, 6c
- **Given**: the user selected Impeccable, the project keeps a glossary and UX documents, and the session also changed
  one file outside its edit list.
- **When**: the session returns and the agent compares the working directory with the recorded base.
- **Then**: the listed product-file changes are verified and continued through the selected route; the outside file is
  reported, neither reverted nor delivered; each stale OOUX document is named and left unedited.

### Scenario 8: Offer installation when Impeccable is unavailable

- **Covers**: 3d
- **Given**: the user selected Impeccable and it is not installed.
- **When**: the agent checks availability.
- **Then**: it names the upstream install routes, installs only on the user's request through a route that needs no
  prompt answers or hands the user the exact command, and continues inline if the user prefers.

### Scenario 9: Clean up only what the user names

- **Covers**: 7a
- **Given**: a session left screenshots and a `review/` directory under `.impeccable/`.
- **When**: the user asks to remove the screenshots.
- **Then**: the agent removes only the screenshots, leaves `review/`, `PRODUCT.md` and `DESIGN.md` in place and
  reports the change through the selected route.

### Scenario 10: Approve the outside-workflow route

- **Covers**: main success scenario, 1c
- **Given**: a bounded implementation goal.
- **When**: the agent announces the outside-workflow procedure and the user explicitly approves it for this task.
- **Then**: the improvement loop, applicable project checks and before/after verification proceed without workflow
  records, while product constraints, host permissions and separate Git authority remain effective.

### Scenario 11: Wait for route choice and reuse exact approval

- **Covers**: 1b, 1c
- **Given**: no route approval and no answer or approval channel.
- **When**: product edits would begin.
- **Then**: dependent writes wait while useful inspection is preserved; an exact instruction already selecting a
  route instead avoids another identical prompt.

### Scenario 12: Preserve the selected workflow's reviews

- **Covers**: 1c
- **Given**: the user selects a workflow that requires independent review.
- **When**: implementation is checked.
- **Then**: that review stays required; optional bundle reviews waive no selected-workflow requirement.

### Scenario 13: Bound scope growth and Git authority

- **Covers**: 4a, 7b
- **Given**: an approved goal with no remaining Git-effects authority.
- **When**: proposed work exceeds the goal or changes a user constraint, or delivery needs a commit or integration.
- **Then**: dependent scope changes wait for a decision and named Git effects wait for their own authority;
  an in-goal file addition alone does not trigger scope approval and current exact authority is reused.

### Scenario 14: Report stale documents without an existing process

- **Covers**: 6c
- **Given**: a change makes a consumer UX statement stale and no documentation process exists.
- **When**: the coordinator reports the result.
- **Then**: it names the document, affected statement and separate documentation task, edits none and creates no
  follow-up record without a separate request.

### Scenario 15: Relay a complete confirmed question packet

- **Covers**: 5c, 5d
- **Given**: native skill loading and same-child continuation are observed and the packet includes source-cited pre-fills.
- **When**: the user confirms the complete visible packet.
- **Then**: the read-only question phase becomes the same child's brief-bounded writing phase without the coordinator changing answers.

### Scenario 16: Wait for omitted answers and refreshed source facts

- **Covers**: 5d
- **Given**: only question gaps were answered, another question appeared or relevant brief facts changed.
- **When**: the child would write.
- **Then**: dependent writes wait for every missing or affected answer to be confirmed; source-cited suggestions never answer for the user.

### Scenario 17: Fall back on missing native capabilities

- **Covers**: 5e
- **Given**: native loading or same-child continuation is unavailable, continuation state is lost, or shape/critique lacks required nested roles.
- **When**: the agent routes the command.
- **Then**: it reports observed capabilities and enablement, hands the brief to the user's session, and claims no cache-load or inline-role substitute.

### Scenario 18: Preserve context permission and partial-write attribution

- **Covers**: 5c, 6b
- **Given**: a confirmed answer would change PRODUCT.md or DESIGN.md without explicit file/action permission, or a relay partially executed.
- **When**: the coordinator continues or accepts the result.
- **Then**: missing file authority still stops that write; partial output is compared to the recorded base and reported without blind replay, unsolicited reversion or deletion.
