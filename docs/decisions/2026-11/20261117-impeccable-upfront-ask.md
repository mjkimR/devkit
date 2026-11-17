---
id: ADR-impeccable-upfront-ask
title: Ask about Impeccable at the start of each improvement request
summary: "For the optional Impeccable track, we ask the user in the first question round whether to use it unless the request already decides, to make the choice visible before design work, accepting one extra question on requests that would have stayed inline."
proposal: SPEC-uiux-impeccable-upfront-ask
supersedes: [ADR-impeccable-session-authority]
status: accepted
created_at: 2026-11-17
---

# [ADR-impeccable-upfront-ask] Ask about Impeccable at the start of each improvement request

## 1. Context & Problem Statement

`ADR-impeccable-session-authority` runs the Impeccable track only after the user selects it and lets an installed
Impeccable permit an offer. An optional offer leaves the timing and the decision to make it with the coordinator: users
who do not know the track exists never select it, and an offer made after framing and design work arrives once the
inline path has already shaped the result. The track must stay optional and user-selected.

## 2. Decision Drivers

- Keep Impeccable optional and its use a user decision.
- Make the choice visible before framing, design work or delegation shape the result.
- Ask once, and not when the user already decided.
- Invoke no external skill the user did not select.

## 3. Considered Options

- Keep the optional offer: no extra question, but the choice stays invisible in most requests.
- Ask in the first question round unless the request already decides (selected): one extra question, combined with
  any route or missing-input question, and asking selects nothing.
- Make Impeccable the default track when installed: no question, but it runs an external skill the user did not
  select and contradicts the selection rule.

## 4. Decision Outcome

Chosen option: ask in the first question round, because it makes the choice visible before design work while keeping
the decision with the user and invoking nothing on its own.

- When a request states neither use nor non-use of Impeccable, the coordinator's first question round asks whether to
  use it for this request, says whether it appears installed and is combined with any route or missing-input
  question. A request or exact prior instruction that decides skips the question. → `CAP-DLV-uiux-improvement` rule 15 (MUST).
- A pending or unanswered question selects nothing: Impeccable stays unloaded and uninvoked, and work that does not
  depend on the answer continues inline. → `CAP-DLV-uiux-improvement` rule 15 (MUST).
- A yes without an installed Impeccable follows the existing unavailable path. → `CAP-DLV-uiux-improvement` rule 10 (MUST).

Supersedes in part `ADR-impeccable-session-authority`: Decision Outcome clause stating that an installed Impeccable permits an offer.

Selection before any Impeccable session, load or invocation, hook-output handling and all other in-force clauses remain.

## 5. Consequences

- Every request that does not decide the track carries one Impeccable question, including small and review-only ones.
- Users learn about the track without reading the bundle guide.
- Installation detection stays best effort; the question states what the coordinator observed.

## 6. Confirmation

- `packages/devkit-catalog/tests/integration/bundles/test_app_uiux_improve.py`: instruction assertions for the
  upfront question, the skip condition and non-selection on silence.
- Review only: whether the question is actually asked first in a live run.
