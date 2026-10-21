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
milestones and --history to include done/dropped records. Existing transition authority is unchanged.

Close planned/active milestones through Backlog: review sufficient decomposition, settled direct proposal work
and the exit condition together. The user's two confirmations record Decomposition: confirmed and Direct proposal
work: confirmed under Completion review with status done in one commit. Missing assertions are unconfirmed;
proposal absence or handoff alone proves no delivery. Scope/membership changes reset both to pending; unchanged
approval survives interruption after rechecking facts. Existing done records remain unchanged; extending done scope
requires a user-owned reopen to active or another milestone. Repeated close of unchanged done writes nothing.
