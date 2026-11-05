---
reconcile_id: REC-cloud-research-handoff
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-deep-research.md
    resolution: modified
  - file: docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md
    resolution: modified
---

# Reconciliation: cloud research handoff

`CAP-DLV-deep-research` rules 32–40 and the cloud interface restate request/disclosure, truthful state,
report association/evidence/authority, durable partial resume and missing-result behavior. The use case folds
those into its investigation steps, branches and scenarios 20–24. Existing invocation, optional roles, source
access, coordinator ownership, immutability and material-preservation contracts remain intact.

`ADR-user-mediated-cloud-research` was promoted in the handoff commit before this worker's base; it needs no
wording change. All its outcome clauses are restated in the capability. No architecture, dependency or UX contract
changes. No requested work was deferred; excluded provider execution creates no follow-up commitment.

The existing skill entry is the doorway for both contracts; the conditional reference is not a separate entry.
Entrypoint derivation retained the already-declared skill entry for both targets; helper references and tests were rejected as doorway candidates. Independent reconciliation compares the implementation,
all six ACs and these two targets; instruction tests and semantic review establish no provider execution or LLM compliance.
