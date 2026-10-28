---
id: PADR-bounded-pr-merge-recovery-evidence
title: Persist bounded pull request merge recovery evidence
summary: "For uncertain pull request merges across CLI calls, we retain bounded clone-local attempt evidence without approval, to prevent unknown merge replay, accepting refusal when evidence is missing or unresolved."
proposal: PROP-pr-merge-recovery
status: draft
created_at: 2026-10-28
---

# [PADR-bounded-pr-merge-recovery-evidence] Persist bounded pull request merge recovery evidence

- **Status**: Draft
- **Date**: 2026-10-28

---

## 1. Context & Problem Statement

`CAP-INT-mcp-services` prohibits replay of unknown remote writes while retaining no recovery journal.
`ADR-host-cli-lifecycle-authority` relies on remote observation after restart.
An `OPEN` PR does not distinguish a pending, never-attempted merge from an uncertain call.
`FB-integration-reissues-merge-after-unknown-outcome` records both replay and replacement of closed pending PRs.

## 2. Decision Drivers

- Preserve a never-replay refusal across CLI process restarts.
- Continue a devkit-created pending PR whose merge was never attempted.
- Keep Host authority, current source validation and remote evidence independent.
- Bound local state without discarding unresolved attempts.

## 3. Considered Options

| Option | Benefit | Cost or failure |
| --- | --- | --- |
| Keep remote-only observation | No durable state | `OPEN` cannot distinguish prior uncertain merge; replay remains possible. |
| Refuse every existing `OPEN` PR | Prevents replay without a journal | Ordinary pending-check continuation cannot finish through this CLI. |
| Bounded clone-local recovery evidence | Continues tracked pending PRs and refuses uncertain replay | Adds local durability and conservative refusal when history is unavailable. |

## 4. Decision Outcome

Select bounded clone-local recovery evidence, with the identity, limits and transitions in `PROP-pr-merge-recovery`.
Persist an issued marker before merge; unresolved `OPEN` never clears it.
Admit only confirmed newly created PRs as never-attempted; refuse untracked existing `OPEN` PRs.
Remote proof of `MERGED` supports only verified remaining cleanup.
Closed exact-source PRs refuse replacement.

This decision supersedes only the no-recovery-journal clause of `ADR-host-cli-lifecycle-authority`.
Its Host conversational authorization decision remains in force.
Store no approval or reusable request credential.
Every mutation requires current preparation, scope validation and Host authority.
The journal can add a refusal; it cannot authorize an effect.

## 5. Consequences

- Fresh invocations distinguish tracked pending work from possibly sent merges.
- A crash immediately before sending can require manual reconciliation even though no merge occurred.
- Existing external PRs, legacy attempts and a lost/deleted journal cannot be safely auto-adopted.
- Local records do not coordinate another clone or manual platform writes.
- Unresolved entries do not expire; capacity exhaustion refuses until terminal remote evidence permits removal.
- No recovery-daemon, approval store or general retry engine is introduced.

## 6. Confirmation

Development adds fake-provider cases to `packages/devkit/tests/integration/features/integration/test_pull_request.py`
and CLI assertions to `packages/devkit/tests/integration/features/integration/test_cli.py`.
Cases cover fresh-process unknown/open and lost-reply/merged recovery, pending continuation, closed refusal,
identity drift, durability/crash windows, capacity, lock serialization and authority independence.
Review checks that the Living Spec changes only the no-journal contract and preserves the Host authority boundary.
Planning verifies the documented design; no production code or external platform behavior is tested in this turn.
