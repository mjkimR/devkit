---
id: ADR-response-style-measurement
title: Review examples and verify the deployed response style
summary: "Uses authored examples for subjective design review and existing bundle checks for implementation, without a required benchmark or an objective quality ranking."
proposal: SPEC-response-style-survey
status: accepted
created_at: 2026-10-20
---

# [ADR-response-style-measurement] Review examples and verify the deployed response style

## 1. Context & Problem Statement

A small numeric score cannot decide how much a reply helps a particular reader. A controlled live comparison
also needs deliberate isolation and a chosen execution budget, neither of which is needed to discuss concrete
proposed wording. Native role inheritance alone cannot provide an unstyled baseline.

## 2. Decision Drivers

Use reviewable examples, preserve factual and output obligations, distinguish illustrations from observations,
and keep verification proportionate to a response-style bundle change.

## 3. Considered Options

| Option | What it establishes | Limitation |
| --- | --- | --- |
| Source survey alone | Published practices | Does not show the proposed text or any local behavior. |
| Authored examples plus normal implementation verification | A concrete design and evidence that its text is deployed correctly | Does not measure reader comprehension or model-wide quality. |
| Repeated live benchmark and scorer | Observations for the selected cohort | More collection/setup cost; proxy scores still do not settle preference. |

## 4. Decision Outcome

Recommend the second option. `MAT-response-style-rewrite-draft` contains the proposed wording and four illustrative
request types; `MAT-response-style-measurement-design` states what review and deployment checks do and do not
prove. Show the examples and rationale for subjective judgment. Apply the normal independent Development review,
Living Spec reflection, relevant tests, lint, types, smoke and rules before completion.

No generation quota, scoring tool or large benchmark is a required phase. The Host withdrew its obsolete cohort
question without selecting a host or recording user approval. A later live comparison needs its own explicit
conditions and execution allowance; it is not a dependency of `plan-accept` for this recommended design.

## 5. Consequences

Report a reviewed rewrite and the checks actually performed, rather than an unverified quality gain. Facts,
required formats and workflow reports cannot be waived by style preference. There is no additional approval
gate, headless-launcher implementation or automatic style-selection rule.
