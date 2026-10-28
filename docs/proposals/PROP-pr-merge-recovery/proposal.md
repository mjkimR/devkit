---
id: PROP-pr-merge-recovery
title: Recover uncertain pull request merge outcomes across CLI calls
summary: "Preserve clone-local pull request merge attempt evidence across CLI calls and reconcile it with remote state, so unknown merges are not replayed and closed pending requests are refused. Recovery evidence never grants approval."
status: reviewing
created_at: 2026-10-28
target_area: capabilities/integration/
priority: high
size: M
planning_effort: medium
dev_effort: high
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/integration/
    - packages/devkit/tests/integration/features/integration/
    - docs/capabilities/integration/
    - docs/decisions/
  excludes:
    - packages/devkit-mcp/
task_kind: bugfix
workflow: sdd-proposal
---

# [PROP-pr-merge-recovery] Recover uncertain pull request merge outcomes across CLI calls

## 1. Background & Hypothesis

A fresh CLI invocation repeats a merge whose earlier outcome was unknown while its PR remains `OPEN`.
The lookup also discards a `CLOSED` pending PR and can create another PR.
`CAP-INT-mcp-services` prohibits replay of an unknown remote write, but excludes a persistent recovery journal.
`ADR-host-cli-lifecycle-authority` assigns approval to the Host and relies on observable remote state after restart.
The fake provider demonstrates that `OPEN` alone cannot distinguish an unattempted merge from an uncertain attempt.

`PADR-bounded-pr-merge-recovery-evidence` proposes a limited exception for clone-local recovery evidence.
The CLI still accepts no persisted approval, credential or proof of conversation.
`materials/recovery-analysis.md` records the evidence and alternatives.

## Source feedback

- `FB-integration-reissues-merge-after-unknown-outcome`: own both unknown-merge replay and closed-pending-PR refusal.
  Its promoted disposition remains unchanged.

## 2. Technical Spike Questions

- **Q1 — settled**: Remote `OPEN` is insufficient evidence that a merge was never sent.
  Persist a conservative merge-attempt marker before the call.
- **Q2 — proposed**: Select a bounded clone-local journal over remote-only continuation or refusal of every existing PR.
  The marker controls refusal and observation, never authority.
- **Q3 — settled**: A closed PR matching the repository, base, head branch and source SHA is a conflict.
  A recorded PR number remains binding even when its remote fields change.
- **Q4 — tradeoff for review**: An untracked existing `OPEN` PR cannot be automatically adopted safely.
  Refuse it; the Host inspects it and uses separately authorized platform handling, or a distinct PR after reconciling the old one.
  No journal-reset or force-adopt command is introduced.

## 3. Proposed Design & Impact

### Recovery identity and storage

Keep one versioned JSON journal at `<git-common-dir>/devkit/integration/pr-merge-recovery.json`.
All worktrees of the clone share the existing integration lock.
Production storage belongs to the integration repository layer; do not modify the installation receipt.
Bind each record to resolved GitHub host/repository, fetch/push destinations, PR number, head/base branch,
source SHA, and task kind/id/unit.
Store a checked build target/tree only as diagnostic evidence; it cannot establish a checked landing in another invocation.
Store no request ID, approval decision, approval credential, readiness verdict or reusable prepared digest.

Limit the journal to 1024 records and 1 MiB of serialized bytes.
Exceeding either limit refuses a new record before any merge call.
Remove records only after observing their exact PR as `MERGED` with valid source containment or `CLOSED`.
Unresolved records never expire or get evicted to admit another operation.
No journal deletion or source/task change may make an uncertain same-PR merge eligible again.
A never-attempted record may update only its source SHA after fresh preparation and Host authority.
Keep repository, PR number, head/base branches and task identity fixed.
Under the integration lock, revalidate the recorded state and remote head before atomically updating the source binding.
The usual remote-source ancestry, readiness, policy and digest checks still apply.
An issued or otherwise uncertain record cannot use this update path.

Validate the schema, identity and size under the integration lock.
Persist by atomic replacement, fsync the file and containing directory, then call the merge endpoint.
If durability cannot be established, refuse before merge.
A crash after persistence but before sending is deliberately indistinguishable from an uncertain send.
The next invocation refuses another merge while that PR is `OPEN`.
The journal is local operational evidence under the existing filesystem trust model, not tamper-proof storage.

### Invocation transitions

`prepare` observes and discloses recovery disposition without writing journal state.
`integrate` constructs a fresh request, validates its digest and all existing authority/readiness/cleanup conditions,
then re-reads the journal and exact PR under the integration lock before a merge.
Bind the record identity and recovery disposition into the prepared digest; journal drift makes it stale before effects.
Never let a record restore authority or bypass retained-base `ask`, publication authority or source validation.

| Record and PR observation | Permitted behavior |
| --- | --- |
| No PR and no matching unresolved record | Existing publication route; register the confirmed newly created PR before returning pending or attempting merge. |
| Registered, never attempted; exact PR `OPEN` | Pending checks return without merge; a fresh approved invocation can merge once checks pass. |
| Attempt issued; exact PR `OPEN` | Refuse with `INTEGRATION_MERGE_OUTCOME_UNRESOLVED`; no merge, PR replacement or cleanup. |
| Attempt issued; observation missing, timed out or inconsistent | Preserve record and worktree; refuse with the existing observation/conflict code. |
| Exact PR `MERGED` | Verify merge parent/source containment; prepare only remaining guarded cleanup with fresh authority; never send merge. |
| Recorded PR `CLOSED`, or an untracked exact-source closed candidate | Refuse with `INTEGRATION_PR_CONFLICT`; do not create a replacement PR. |
| Existing `OPEN` PR without a valid record | Refuse with `INTEGRATION_MERGE_HISTORY_UNKNOWN`; do not infer no earlier attempt from an absent journal. |
| Malformed, unsupported or unreadable journal | Refuse with `INTEGRATION_RECOVERY_STATE_INVALID`; preserve files and recovery identities. |

Register a never-attempted record only for a PR confirmed created by this invocation.
A PR discovered after a lost creation reply remains untracked and conservatively refused in a fresh invocation.
An exact, already `MERGED` PR can be recovered without a journal because remote evidence proves merge completion.
An ambiguous candidate set refuses; lookup order must not choose the first matching PR.
A discovery result containing 1000 candidates reaches the existing adapter cap.
Refuse new publication with `INTEGRATION_PR_HISTORY_INCOMPLETE` rather than treating that result as proof of absence.
Use exact-number observation for an already bound record; do not require an unbounded history scan.
Historical closed PRs with another source SHA do not block an unrelated request, unless its recorded PR identity binds it.
An unresolved record for a PR blocks that PR even when the task, source SHA or local branch name changes.
A changed binding is a conflict, except the validated never-attempted source-only update above.

Immediately before merge, change the durable record from never-attempted to issued.
A lost reply, timeout, 5xx, malformed response, or crash leaves it issued.
An explicit platform rejection that the existing adapter classifies as definitely not merged may make it never-attempted
again only after a successful exact-PR `OPEN` observation; a crash before recording that transition stays issued.
Remote `OPEN` alone never clears issued.
A fresh Host decision alone never clears issued.
The existing known-refusal mapping remains unchanged; add no transport retry or in-call merge loop.

Agent output names the bound PR, source and recovery disposition with stable advisory codes and deterministic actions.
For unresolved or untracked `OPEN`, the action is to inspect/reconcile the exact PR outside this automated merge path;
a generic instruction to rerun `integrate` is insufficient.
Under `ask`, missing/stale digest retains the existing interaction guidance and exit semantics.

### Development verification criteria

- **AC-R1**: Given a fake unknown merge response with PR still `OPEN`, when a new service prepares and integrates,
  then total `merge_calls` remains one, no replacement PR is created, and worktree/branch cleanup is not run.
- **AC-R2**: Given a merge that completed but whose reply was lost, when a fresh invocation observes `MERGED`,
  then it validates source containment and performs only freshly approved remaining cleanup with one merge call total.
- **AC-R3**: Given a PR published by devkit whose checks were pending without any merge attempt,
  when a fresh approved invocation sees passing checks, then exactly one merge is allowed.
- **AC-R4**: Given a pending PR closed before the next invocation, when preparation or execution runs,
  then it returns `INTEGRATION_PR_CONFLICT` with no merge or replacement creation.
  Include exact-source closed history, unrelated closed history, ambiguous candidates and changes after preparation.
  Saturated 1000-candidate history refuses new publication even when the relevant closed PR is omitted.
- **AC-R5**: Given an issued record, when source/task/remote binding changes, the record is missing/corrupt,
  or the journal exceeds its limits, then no same-PR merge is sent and recovery identities remain.
  Missing journal plus existing `OPEN` yields `INTEGRATION_MERGE_HISTORY_UNKNOWN`.
- **AC-R6**: Inject failure before persistence, after durability but before send, and after send before response recording.
  Assert no send before durability, no replay after issued, and no eviction of an unresolved record at capacity.
  Cover two services sharing a clone lock, atomic-write failure and a journal change after preparation.
- **AC-R7**: A retained marker never satisfies a missing digest, changed readiness/policy/source or missing Host authority.
  Verify known platform refusal permits a newly prepared retry only after definitive refusal and exact observation.
- **AC-R8**: Given tracked pending checks and a never-attempted record, when the target advances and the Host
  incorporates it into the source, re-verifies and obtains fresh authority, then the source binding updates atomically
  and exactly one eventual merge is allowed. The same change on an issued record refuses without another merge.
- **AC-R9**: Existing merged-cleanup ordering, source preservation, checked/unchecked landing reporting,
  CLI JSON/text output and local-route behavior continue to pass.

Use only fake GitHub providers and local fixture repositories.
Development first adds failing regression cases to the existing integration test tier, then implements the fix.
Run package lint, type checks, relevant integration tests and `just test-affected` before its final report.
Planning makes no performance/count improvement claim beyond these deterministic fake-provider assertions.

### Scope excluded

No real GitHub write, generalized durable workflow service, cross-clone coordination, approval persistence,
new MCP surface, automatic platform retry, journal reset/adoption command, or unrelated cleanup refactor.
Push and PR-create retry semantics remain outside this merge-recovery change; an uncertain creation can cause a safe refusal.
The existing worktree GitHub adapter already exposes all PR states and exact-number observation.
Its production code needs no change for this direction.

## 4. Lifecycle & Retirement Criteria

Planning remains `reviewing` until the Host obtains `plan-accept`; no acceptance or handoff occurs in this turn.
The bounded-journal exception needs the proposed PADR accepted before Development changes the current no-journal contract.
Development updates `CAP-INT-mcp-services`, promotes the PADR and marks only the superseded no-journal clause of
`ADR-host-cli-lifecycle-authority`; Host conversational authority and all unrelated clauses remain effective.
`dev_effort: high` remains appropriate because the changed recovery path governs a remote merge that cannot be undone locally.
Planning effort is medium, with an evidence Scout and one Challenger pass.
The proposal retires through the normal handoff after acceptance; no production implementation is part of Planning.
