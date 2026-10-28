# Repository roadmap

Milestones are global documents named MS-<slug>.md, created from the deployed milestone template. User and agent
jointly review each theme and decompose it into direct proposal members. Proposal anchors declare membership;
milestone bodies do not list work. Handoff does not carry milestone metadata into specs, and historical SPEC
metadata is ignored. Inspect code/Git on demand for downstream outcomes; no delivery lineage is stored.

Milestones are loosely managed themes. Prefer a multi-unit phase, release or architectural theme advancing
`ARCH-01-introduction-and-goals` over a milestone that only sequences one proposal; a theme may begin with one proposal
while additional scope is not authored. Use unit depends_on for PROP/SPEC prerequisites. Milestone depends_on remains
MS-only.

Exit conditions are recommended to state observable phase-level outcomes and capability boundaries. Keep CLI flags, branch
names, file layouts and scenario tests in proposals/specs. Use devkit docs list milestone to discover current
milestones and --history to include done/dropped records. Existing transition authority is unchanged.

Close planned/active milestones through Backlog: review sufficient decomposition, settled direct proposal work
and the exit condition together. The user's two confirmations record Decomposition: confirmed and Direct proposal
work: confirmed under Completion review with status done in one commit. Missing assertions are unconfirmed;
proposal absence or handoff alone proves no delivery. Actual semantic scope changes reset both to pending; normal handoff does not; unchanged
approval survives interruption after rechecking facts. Done records stay as written unless merged; extending a done
milestone's own scope requires a user-owned reopen to active or another milestone. Repeated close of unchanged done
writes nothing.

On the user's Backlog decision, small milestones of any status may merge into a broader theme milestone. The theme
lists the merged IDs in aliases, the merged files are deleted in the same commit and devkit rules fix moves current
references; completed specs and Git keep the delivery record. Remaining scope moves to draft proposals in the theme,
which stays planned or active while scope remains and becomes done only through both confirmations. A merge is not an
in-place extension.
