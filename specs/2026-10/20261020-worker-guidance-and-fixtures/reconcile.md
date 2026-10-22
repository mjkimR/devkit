---
reconcile_id: REC-worker-guidance-and-fixtures
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md
    resolution: modified
---

# Reconciliation

Agent guidance reflects explicit official-document read authority, Host-owned sync, and exact link-repair boundaries.
Envelope guidance describes unsolicited decisions while preserving pending-question answers and recorded-assumption
settlements. Git isolation changes test fixtures only; the production scope registry contract is unchanged.
No architecture, new runtime schema, policy override or additional capability is introduced.

## Direct source resolutions

- `FB-planning-direction-change-without-question`: clarified worker-records section 2, including the existing
  settles-only exception found by independent review and corrected in reverify.
- `FB-planning-platform-facts-unverifiable-offline`: payload read authority and Host evidence fallback, reviewed as AC-02.
- `FB-worker-bundle-edit-leaves-receipt-stale`: Host synchronization order in spec-integrate, reviewed as AC-03;
  actual integration sync remains the Host's subsequent step, not a worker completion claim.
- `FB-worker-fixtures-inherit-git-context`: three reported failures reproduced, then scope103 passed with
  in-worktree basetemp. Full selector fallback and static checks passed.
- `FB-worker-scope-misses-link-repairs`: payload preflight and exact repairs, reviewed as AC-05.

All five sources were open and explicitly authorized direct fixes; their resolutions do not claim integration.
No deferred requirement remains. Host must sync changed bundle assets during integration preparation.

## Entrypoint review

Derived candidates were reviewed: harness guidance already declares its skills directory. The scope-test directory
is not a production entrypoint for either target. The envelope target only clarifies its guidance; the unchanged
runtime entrypoints remain correct. No new pair was applied.
