# Repository roadmap

Milestones are global documents `MS-<slug>.md` with a word-led slug (for example `MS-release-1-0`), created from the
deployed milestone template. Planned/active files live at `docs/roadmap/`, done/dropped files at
`docs/roadmap/_archive/`. Keep IDs, aliases and filenames unchanged. Use `devkit docs list milestone` to discover
current milestones and `--history` to include done/dropped records. Existing transition authority is unchanged.

## Goal and membership

- Cite the goal in `ARCH-01-introduction-and-goals`. Milestones are loosely managed themes: User and agent jointly
  review a multi-unit phase, release or architectural theme and decompose it into direct PROP members. A theme may
  initially have one proposal while broader scope is not authored; prefer a broader theme over a milestone that only
  sequences one proposal.
- Only direct PROP anchors declare membership, through `milestone`; milestone bodies do not list work. Use unit
  `depends_on` for PROP/SPEC prerequisites; milestone `depends_on` remains MS-only.
- Handoff does not carry milestone metadata to SPEC, and historical SPEC metadata is ignored. Inspect downstream
  code/Git on demand; no delivery lineage is stored.
- A milestone, in any status, frames direction and binds nothing: proposal Planning concretizes and settles scope and
  requirements. Never treat its goal, exit condition or non-goals as constraints when judging design options.

## Exit condition

Exit conditions are recommended to state observable phase-level outcomes and capability boundaries. Prefer observable
phase-level outcomes over CLI flags, branch names, file layouts and scenario tests, which belong in proposals/specs.

## Completion review

- Close planned/active milestones through Backlog, reviewing sufficient decomposition, settled direct proposal work
  and the exit condition together. After the user's two confirmations, record `Decomposition: confirmed` and
  `Direct proposal work: confirmed` under Completion review with status `done` in one commit.
- Missing assertions are unconfirmed; proposal absence or handoff alone proves no delivery. Actual semantic scope
  changes reset both to pending; normal handoff does not. Unchanged approval survives an interruption after
  rechecking facts.
- Done records stay as written unless merged; extending a done milestone's own scope requires a user-owned reopen to
  active or another milestone. Repeated close of unchanged done writes nothing.
- Close/drop/reopen commit the status, applicable assertions/disposition and file movement together under the existing
  user decision. Drop creates no completion assertion; repeated unchanged archived drop writes nothing. Reopen moves
  to the root, sets active and resets both assertions to pending. Stop on destination collisions; no archive-only
  approval is added to an approved transition.

## Merge

On the user's Backlog decision, small milestones of any status may merge into a broader theme milestone. The theme
lists the merged IDs in `aliases`, the merged files are deleted in the same commit and `devkit rules fix` moves
current references; completed specs and Git keep the delivery record. Remaining scope moves to draft proposals in
the theme, which stays planned or active while scope remains and becomes done only through both confirmations. A
merge is not an in-place extension.
