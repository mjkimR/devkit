# PR merge recovery evidence and option comparison

Input snapshot: `ca522c755d4d4c843cfda403467c0f04161cafd6`; Planning base: `6ffb1ea17a1ee861318925ebd585d03777f2c637`.

| Evidence | Consequence |
| --- | --- |
| `packages/devkit/src/devkit_agt/features/integration/usecases/pull_request.py:128-139` selects OPEN then matching MERGED | CLOSED is discarded despite all-state adapter lookup. |
| Same file, lines 345-410, merges a refreshed non-MERGED PR | Fresh OPEN does not show whether a prior merge was sent. |
| `packages/devkit/tests/integration/features/integration/test_pull_request.py:61-66` returns unknown without state change | Fake provider can reproduce the ambiguous OPEN state without external calls. |
| Same file, lines 111-126 and 141-151 | Existing fresh-service helper and pending continuation provide the regression seam. |
| `packages/devkit/src/devkit_agt/features/worktree/repositories/pull_request.py:303-326` | All-state discovery and exact-number view already exist. |
| `packages/devkit/src/devkit_agt/features/worktree/services/merging.py:46-48` | Integration lock is clone-common; journal operations can share its serialization. |
| `CAP-INT-mcp-services`, Partial results and recovery; `ADR-host-cli-lifecycle-authority`, Decision Outcome | A bounded evidence store changes the no-journal clause, without changing conversational authority. |

| Option | Evidence | Cost | Risk | Open question |
| --- | --- | --- | --- | --- |
| Remote observation only | OPEN is ambiguous in fake provider | Small lookup fix for CLOSED | Unknown merge replay remains | Cannot meet both continuation and never-replay. |
| Refuse every existing OPEN | Existing PR is observable | Removes ordinary pending continuation | Repeated manual platform work | Viable if no durability is desired. |
| Bounded local evidence, recommended | Pre-send issued marker survives restart | Atomic local persistence and conservative legacy refusal | Crash before send can strand an unmerged PR | Accept at plan-accept with the stated limitation. |

No probe, live GitHub request or production mutation ran. Evidence is static code review plus the Scout's
repository-only report, not a newly executed reproduction. Development must demonstrate Red/Green with fake providers.
The Scout used the emulated Codex route. Before/after delegation tree snapshots both equal
`d5b2285720221fce210bd3c432f9e62b3f4abdd5`; HEAD was unchanged. It reported no outside-worktree reads.
All authored Planning files stay inside this proposal; sibling writes use individual host approvals.

## Challenger fold and self-verification

Input: `e6bbd46c1fa81495d5e851127e672d6ccf2fce20`. The read-only Challenger left both delegation
snapshots at `d7bc439bde63501cccbcb50a68504615cec4f491`; HEAD was unchanged and it reported no outside reads.

1. Source repair after pending checks: proposal now permits only a never-attempted source-only update,
   under the lock after fresh authority and the existing source/head/readiness/policy checks. Issued records stay refusing.
   AC-R8 requires pending -> target advance -> source repair -> exactly one eventual fake merge.
2. Saturated discovery: 1000 returned candidates cannot establish absence. Proposal requires
   `INTEGRATION_PR_HISTORY_INCOMPLETE` before new publication; AC-R4 adds the omitted-closed-PR fixture.

The Planning worker compared both changes to the existing target-moved remedy and adapter limit.
They are document fixes verified by review, with executable regressions reserved for Development.
No user-dependent question remains; accepting the bounded journal and conservative untracked-OPEN refusal
is the Host's existing plan-accept boundary, not a new business approval requested by this worker.
