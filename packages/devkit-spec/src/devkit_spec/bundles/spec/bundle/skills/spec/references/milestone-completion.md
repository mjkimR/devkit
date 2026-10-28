# Milestone completion review

Read this for a requested Backlog close review, or to propose one after the milestone's known work finishes. The shared milestone template is `.devkit/managed/docs/templates/milestone.md`. In SDD, only direct PROP anchors declare milestone membership; handoff does not carry it to SPEC. The milestone frames direction, not binding implementation requirements. Planning settles scope. Semantic scope changes reset both completion assertions to pending; normal handoff does not. Record confirmed assertions and done status together only after user confirmation.

## Prepare one candidate

1. Read the goal, exit condition and non-goals, and judge whether the intended scope is fully decomposed into proposals; empty membership proves nothing.
2. List the direct members: `devkit docs refs MS-<slug> --direction in -n 0` (frontmatter membership, not prose references), with `devkit docs list proposal --history --all-namespaces -n 0` (rejected members included).
3. Inspect the local base and known `plan-`/`dev-` activity without switching another task's checkout, and report the base commit used. Use focused Git inspection for a proposal that left through handoff; persist no descendant graph.
4. Prepare one candidate: each member delivered, explicitly excluded or moved, and the exit condition met for the agreed scope. Update the goal or exit condition when the scope shrank.
   - An unresolved in-scope proposal (draft, reviewing or accepted) or unfinished handed-off work blocks the close.
   - A retained rejected member needs an explicit scope disposition.
   - Handoff, deletion, rejection or reassignment alone proves no delivery.
5. If work is outstanding, the exit condition is unmet or required evidence is missing or inconclusive, keep the milestone open and name the remaining check. Report missing user confirmation separately from evidence gaps.

## Confirm and write

The milestone body holds two assertions under `Completion review`:

```text
Decomposition: pending
Direct proposal work: pending
```

1. Present both assertions with the candidate. Missing or previously confirmed assertions authorize nothing.
2. Immediately before writing, re-read scope and membership and recheck the evidence. If either changed, or the approved candidate cannot be re-established after a pause, present the candidate again; an interruption alone does not invalidate the user's confirmation.
3. On the user's confirmation of both, write `Decomposition: confirmed`, `Direct proposal work: confirmed` and `status: done` in one Backlog commit, from `planned` or `active`.

## Later changes

- Wording or format corrections that keep the meaning do not reset the assertions.
- To extend a `done` milestone, get the user's decision to reopen it to `active` and reset both assertions, or put the new scope in another milestone. Merging it into a broader theme milestone ([Backlog](backlog.md)) is not such an extension: the theme's own assertions decide its close.
- Closing an unchanged `done` milestone writes nothing. A `dropped` milestone is no close candidate, and existing `done` records stay as they are unless merged.
