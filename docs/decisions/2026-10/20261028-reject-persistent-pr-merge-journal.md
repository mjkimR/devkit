---
id: ADR-reject-persistent-pr-merge-journal
title: Reject persistent PR merge recovery state
summary: "For uncertain PR merge replies, we reject a persistent attempt journal, to keep integration proportionate to demonstrated failures, accepting existing guarded retries and error reporting."
status: accepted
created_at: 2026-10-28
---

# [ADR-reject-persistent-pr-merge-journal] Reject persistent PR merge recovery state

- **Deciders**: user
- **Rejected proposal**: ~~`PROP-pr-merge-recovery`~~, Git `2092282ab6a30059243e26ee4cc148e865e91107`

## 1. Context & Problem Statement

`FB-integration-reissues-merge-after-unknown-outcome` records a fake provider receiving a second merge request.
That observation does not establish duplicate GitHub merge effects. The proposed journal would add persistence,
crash windows and refusal of existing untracked OPEN PRs without demonstrating proportionate benefit.

## 2. Decision Drivers

- Keep recovery cost proportionate to observed failure effects.
- Preserve current identity, source, readiness, authority and error checks.
- Avoid introducing persistent state and new restrictions on existing PRs.

## 3. Considered Options

- Persist an issued marker before merge: preserves a never-resend condition but adds durable state and conservative refusals.
- Retain existing guarded invocations and error reporting: adds no state or runtime change; no universal retry-idempotency guarantee is claimed.

## 4. Decision Outcome

Reject the persistent-journal proposal. The rejection commit `2092282ab6a30059243e26ee4cc148e865e91107` records:

> Repeated merge requests alone do not establish duplicate merge effects. The journal and refusal of untracked existing PRs add unjustified complexity; preserve existing validation, retry and error reporting without new persistent recovery state.

This disposition changes no production code or integration lifecycle contract. It does not authorize unchecked
replays, automatic retry loops, replacement PR creation or cleanup after an unconfirmed merge.

## 5. Consequences

The proposed journal and its capacity, corruption and adoption rules are not implemented. The source feedback
retains its promoted history with this rejection as its final destination. Reconsider recovery changes only when
a concrete harmful failure is reproduced against the actual API semantics.

## 6. Confirmation

Review only: verify the rejection introduces no integration runtime change, preserves the Planning history in Git,
and leaves no live dependency on the removed proposal.
