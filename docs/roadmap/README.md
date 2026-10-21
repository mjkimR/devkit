# Repository roadmap

Milestones are global documents named MS-<slug>.md, created from the deployed milestone template. User and agent
jointly review each theme and decompose it into direct proposal members. Proposal anchors declare membership;
milestone bodies do not list work. Handoff does not carry milestone metadata into specs, and historical SPEC
metadata is ignored. Inspect code/Git on demand for downstream outcomes; no delivery lineage is stored.

A milestone SHOULD represent a multi-unit phase, release or architectural theme advancing `ARCH-01-introduction-and-goals`. It may begin
with one proposal while additional scope is not authored, but SHOULD NOT exist solely to sequence one proposal.
Use unit depends_on for PROP/SPEC prerequisites. Milestone depends_on remains MS-only.

Exit conditions SHOULD state observable phase-level outcomes and capability boundaries. Keep CLI flags, branch
names, file layouts and scenario tests in proposals/specs. Use devkit spec list milestone to discover current
milestones and --history to include done/dropped records. Close planned/active milestones through Backlog after reviewing decomposition, direct proposal work and the
exit condition. Confirm both Completion review assertions with status done in one commit. Missing assertions
are unconfirmed; disappearance or handoff alone proves no delivery. Scope/membership changes reset both to pending.
Unchanged approval persists across interruption after rechecking facts; changed facts require reconfirmation.
Existing done records remain unchanged; extending their scope needs user-owned reopen to active or another
milestone. Repeated close of unchanged done writes nothing; dropped milestones are not close candidates.
