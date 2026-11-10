---
name: app-uiux-improve
description: "Explicitly invoked UI/UX improvement for software interfaces: frame the affected domain objects, improve screens and user flows inline or through a user-selected Impeccable session, and carry requested changes through the existing project workflow and actual verification."
---

# Software interface UI/UX improvement

Run only when the user explicitly invokes this entry.
Improve the software interface and experience serving the supplied user goal: web and desktop applications,
dashboards, admin tools, settings and responsive views. If the request targets slide decks, game loops or media
production, say that this entry does not cover them and stop. Choose flow, interaction and visual work according to
the request. A review-only request ends with findings and no product edits.

## Boundaries

- Follow the consumer's existing development workflow for implementation, records, checks and approvals.
- Keep the current development approach and authority; this skill, its local roles and a delegated Impeccable
  session grant no commit, integration or publication permission.
- Preserve supplied product and design-system constraints unless the user authorizes changing them.
- Use available tools and follow their access restrictions; a denied operation stops without another access route.
- Keep roles optional and local; load only selected role bodies for concrete assignments.
- Treat role instructions as behavioral guidance, not native permission or filesystem isolation.
- Load or invoke Impeccable only after the user selects it for this request; without that selection, work inline.
  An installed Impeccable permits an offer.
- Read the project's OOUX documents (glossary, object register, UX documents) only where they exist, and edit none
  of them in this run; report the ones a change makes stale.
- Install Impeccable, add ignore entries, remove Impeccable output or change `PRODUCT.md` or `DESIGN.md` only on the
  user's request, not on your own initiative.
- Do not require a fixed cast, alternative count, numeric score, exhaustive audit or comparative-effectiveness experiment.

## Procedure

1. Recover the target, intended user outcome, relevant artifacts and hard constraints from available context.
   Ask only for missing information that changes the work. For a broad request, choose a bounded initial focus
   and explain how it serves the goal.
2. Inspect the current interface and representative task path. Use the running UI when available; identify
   screenshot-, code- or text-only coverage when actual interaction cannot be checked.
3. Frame in proportion to the request. Read `references/design-guidance.md` when framing or choosing the design
   direction.
   - If the request is a local change (one component, one state, copy or spacing), proceed without an ORCA pass.
   - If the request adds, merges or reorders views or flows, first name the affected objects, their relationships,
     the CTAs on each object and the attributes each view shows, with empty, loading, error and populated states.
   - If the request is review-only, use the framing as a lens and return findings with no product edits.
   - Frame the objects the request touches, not the whole product.
4. Choose the track. Inline is the default: you implement, optionally with local roles. The Impeccable track runs
   after the user selects it. Read `references/orchestration.md` before delegating to a local role or to Impeccable.
   Assign useful designer, unconventional-designer, reference-researcher or critic work on either track; preserve
   independent first passes until their returns arrive.
5. Synthesize a coherent direction from the inspected artifacts and actual returns. Produce alternatives when the
   choice matters. Preserve a useful unusual mechanism and its tradeoff instead of averaging every suggestion into a
   feature list. Resolve routine design choices within scope; raise product or scope choices that require the user.
6. Before product edits or delegation, complete the consumer workflow's steps that precede implementation (for
   example a branch, worktree or required record). If the consumer workflow drafts new screens before code, draft
   the screen there first; implementation then follows that draft.
7. Apply requested changes through the existing project workflow once its requirements permit implementation.
   - Inline: implement the changes yourself.
   - Impeccable: write the brief, route the command and make no product edits until the session returns; then accept
     its changes against the recorded base as `references/orchestration.md` directs.
   - Continue the workflow through the implementation, required checks and delivery approvals. When an approval or
     tool is missing, preserve useful work and name that concrete blocker.
8. Inspect the changed interface and representative interactions with the available tools. Check relevant
   layout states, feedback and recovery, keyboard/focus behavior and responsive behavior according to the change.
   Apply the baseline craft checks in `references/design-guidance.md`. Run the project's applicable checks. Fix
   defects exposed by these checks and recheck the changed behavior. If critique can improve the result, use one
   bounded critique/refinement pass; stop without a score or consensus quota.
9. Report the applied improvement, why it serves the user goal, what was actually checked and material limits.
   On the Impeccable track, also report changes outside the edit list, session output, consumer context files the
   session created or changed, unverifiable attribution and each OOUX document the change made stale.
   Honor a requested output destination; otherwise report in conversation. Product artifacts follow project ownership.
10. If the user asks you to install Impeccable, add ignore entries, remove Impeccable output or add the `PRODUCT.md`
    reference section, read `references/orchestration.md` before acting and follow its project-file rules; carry the
    change through the consumer workflow like any product change.

## Completion

- A normal improvement request finishes with the changed interface or flow and its verification status.
- A narrower request finishes with its requested findings or design artifact.
- A blocked request names the unresolved choice, artifact, workflow requirement or tool and retains useful partial work.
- A delegated request finishes after you accepted or reported every change the session made.
- Separate observed behavior, design inference and unavailable coverage; do not claim measured UX quality or team superiority.
