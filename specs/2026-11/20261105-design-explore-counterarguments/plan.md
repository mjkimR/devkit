---
id: PLAN-design-explore-counterarguments
spec: SPEC-design-explore-counterarguments
---

# Technical Plan: `SPEC-design-explore-counterarguments`

## 1. Constitution & Invariant Review

`ADR-optional-design-critique-response` authorizes this additive refinement; no invariant conflicts.
Keep `CAP-DLV-design-exploration` explicit invocation, skill-local optional roles, independent first-pass payloads,
honest fallback and conversation-first output. No new feature edge, global role, runtime or dependency is needed.

## 2. Architecture Overview & Impact

The design-explore bundle remains one skill, two references and three local roles. The entry routes conditional
critique work to its existing orchestration reference. That reference owns the response packet, validation,
coordinator disposition and stop rule. The explorer gains a conditional response assignment; the critic's existing
single-pass output stays bounded. The package entry point and manifest remain unchanged.

## 3. Component & Interface Design

The optional exchange reuses existing role paths and plain-language returns:

1. Keep independent first-pass payloads free of peer conclusions.
2. Select only supported objections that can alter the actual choice.
3. Supply candidate, objection, support, failure condition, affected choice and preserved constraints to the
   original explorer when available; permit one response per affected candidate.
4. Validate actual accept/revise, rebut or bounded-unknown returns and report one disposition per selected objection.
5. If the author is unavailable, disclose it and label coordinator analysis; invent no reply or agreement.
6. Synthesize after the normal exchange. A further pass first names a decision-changing question and finite bound.

No fixed schema is added. The stale-cache example illustrates a revision with an invalidation mechanism, an
evidence-backed rebuttal and an unresolved support limit. A response does not grant implementation authority.

## 6. Verification & Test Plan

| Criteria | Evidence |
| --- | --- |
| AC-01 | Existing optional/zero-findings tests plus a focused response-contract test and semantic walk of simple/zero-findings outcomes. |
| AC-02 | Focused integration assertions across coordinator/explorer/critic instructions; built-wheel consumer verifies installed response assets; semantic objection/revision/rebuttal examples. |
| AC-03 | Bound/finite-question and no-automatic-reply assertions plus semantic unresolved-disagreement walk. |
| AC-04 | Missing-response/inline-authority assertions and existing independent-context/role-authority tests. |
| AC-05 | Evidence/inference/unknown response assertions and semantic unsupported-rebuttal walk. |

Run focused catalog integration and installed-consumer tests, `just lint-check catalog`, `just check catalog`,
`just test-affected --base 992799b38258dd4e2d504d1142d3a795f4de6573` with its full fallback, and branch rules.
After asset changes run `devkit sync`; normal tracked outputs, if any, are admitted and recorded as sync outputs.
Code review is an independent medium-effort role. Living Spec reflection updates the capability and use case and
gets a separate reconcile verification; checks claim instruction consistency, not model obedience.
