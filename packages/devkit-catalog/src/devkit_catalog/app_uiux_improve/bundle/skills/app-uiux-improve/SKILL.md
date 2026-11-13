---
name: app-uiux-improve
description: "Explicitly invoked UI/UX improvement for software interfaces: frame the affected domain objects, improve screens and user flows inline or through a user-selected Impeccable session, and implement through a task-approved outside-workflow run or the user-selected project workflow with actual verification."
---

# Software interface UI/UX improvement

Run only when the user explicitly invokes this entry.
Improve the software interface and experience serving the supplied user goal: web and desktop applications,
dashboards, admin tools, settings and responsive views. If the request targets slide decks, game loops or media
production, say that this entry does not cover them and stop. Choose flow, interaction and visual work by the
request. A review-only request ends with findings and no product edits.

## Boundaries

- Follow the route the user approved for this task: the outside-workflow procedure or the consumer workflow.
- Keep the configured development approach unchanged; selection or invocation alone changes no workflow policy.
- This skill, its local roles and a delegated Impeccable session grant no commit, integration or publication permission.
- Preserve supplied product and design-system constraints unless the user authorizes changing them.
- Use available tools within their access restrictions; a denied operation stops without another access route.
- Keep roles optional and local; load only selected role bodies for concrete assignments. Role instructions are
  behavioral guidance, not native permission or filesystem isolation.
- Load or invoke Impeccable only after the user selects it for this request; without that selection, work inline.
  An installed Impeccable permits an offer.
- Read the project's OOUX documents (glossary, object register, UX documents) only where they exist, and edit none
  of them in this run; report the ones a change makes stale.
- Install Impeccable, add ignore entries, remove Impeccable output or change `PRODUCT.md` or `DESIGN.md` only on the
  user's request, not on your own initiative.
- Do not require a fixed cast, alternative count, numeric score, exhaustive audit or comparative-effectiveness experiment.

## Procedure

1. Recover the target, intended user outcome, relevant artifacts and hard constraints from context; ask only for
   missing information that changes the work. For a broad request, choose a bounded initial focus and explain how
   it serves the goal. A focus such as color first orders work; only user-stated constraints or explicit deferrals
   become non-goals. For implementation or requested setup/cleanup, announce: this procedure runs outside the
   repository's development workflow and its process guidelines. Obtain explicit approval for this task or follow
   the consumer workflow the user chooses, before product edits or write-capable delegation. Reuse an exact route
   instruction already given; do not ask twice. Without an answer or approval channel, preserve useful read-only
   inspection and wait before dependent edits. Silence selects no route. A review-only request needs no route approval.
2. Inspect the current interface and representative task path in the local branch build when executable; retain
   the baseline task, data and capture method before edits. A deployed environment supplies at most a baseline. If live service use is costly or shared, use a repeatable mocked backend
   against that branch build; name screenshot-, code- or text-only coverage when interaction cannot be checked.
3. Frame in proportion to the request. Read `references/design-guidance.md` when framing or choosing the design
   direction.
   - If the request is a local change (one component, one state, copy or spacing), proceed without an ORCA pass.
   - If the request adds, merges or reorders views or flows, first name the affected objects, their relationships,
     the CTAs on each object and the attributes each view shows, with empty, loading, error and populated states.
   - If the request is review-only, use the framing as a lens and return findings with no product edits.
   - Frame the objects the request touches, not the whole product.
4. Choose the track. Inline is the default: you implement, optionally with local roles; the Impeccable track runs
   after the user selects it. Read `references/orchestration.md` before delegating to a local role or to Impeccable.
   Assign designer, unconventional-designer, reference-researcher or critic work on either track where useful, and
   preserve independent first passes until their returns arrive.
5. Synthesize a coherent direction from the inspected artifacts and actual returns, with alternatives when the
   choice matters. Preserve a useful unusual mechanism and its tradeoff instead of averaging suggestions into a
   feature list. Resolve routine design choices within scope; raise product or scope choices to the user.
6. If the user chose the consumer workflow, complete its steps that precede implementation before product edits
   or delegation (a branch, worktree or required record). If that workflow drafts new screens before code, draft the
   screen there first; implementation follows that draft. On the approved outside-workflow route, use this
   improvement loop without creating workflow-specific records or another delivery procedure.
7. Apply requested changes through the selected route.
   - Inline: implement the changes yourself.
   - Impeccable: write the brief, route the command and make no product edits until the session returns; then accept
     its changes against the recorded base as `references/orchestration.md` directs. For interactive work, relay
     every user-confirmed answer through the same child only after native loading, continuation and required nested
     capabilities are observed; otherwise use the user-operated session.
   - Keep product constraints and host permissions on both routes. If a host denies an operation, stop it without
     another access route. If an approval or tool is missing, preserve useful work and name that blocker.
   - Before a new surface or behavior beyond the approved goal, or a change to a user constraint, obtain a new user
     decision. An in-goal file addition or implementation choice alone is not scope growth; pause only dependent work.
8. Repeat the same representative task and data against the changed local branch build before and after, retaining
   a re-runnable capture method. Label mocked coverage as mocked, not an end-to-end check, and name missing live
   coverage. Inspect representative interactions: relevant layout states, feedback and recovery,
   keyboard/focus and responsive behavior as the change requires. Apply the baseline craft checks in
   `references/design-guidance.md` and run the project's applicable checks; fix exposed defects and recheck. If
   critique can improve the result, use one bounded critique/refinement pass; stop without a score or consensus quota.
   The bundle adds no mandatory independent UX or code review; keep every review required by the selected consumer
   workflow. Otherwise recommend a useful optional check when structure or implementation warrants it and report
   whether it ran.
9. Report the selected route, applied improvement, why it serves the user goal, before/after interface verification,
   applicable project checks, what was actually checked and material limits, including missing or declined optional
   checks. Name each stale consumer OOUX or UX document, its affected statement and a concrete separate follow-up
   through the documentation process where present, or a separate documentation task otherwise; edit none and
   create no follow-up record without a separate request.
   On the Impeccable track, also make the reports that `references/orchestration.md` "Accept the return" and
   "Project files and user requests" require.
   Before Git effects, reuse current authority for the exact task effects. If authority is missing, present the
   verified result and ask once for the named remaining commit, integration or publication effects before acting;
   route approval alone grants none. Honor a requested output destination; otherwise report in conversation.
   Product artifacts follow project ownership.
10. If the user asks you to install Impeccable, add ignore entries, remove Impeccable output or add the `PRODUCT.md`
    reference section, read `references/orchestration.md` before acting and follow its project-file rules; carry the
    change through the selected route and host approvals like any product change.

## Completion

- A normal improvement request finishes with the changed interface or flow and its verification status, selected route,
  stale-document follow-up and any remaining unauthorized Git effects.
- A narrower request finishes with its requested findings or design artifact.
- A blocked request names the unresolved choice, artifact, workflow requirement or tool and keeps useful partial work.
- A delegated request finishes after you accepted or reported every change the session made.
- Separate observed behavior, design inference and unavailable coverage; claim no measured UX quality or team superiority.
