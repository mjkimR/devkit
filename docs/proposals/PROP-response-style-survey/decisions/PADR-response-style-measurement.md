---
id: PADR-response-style-measurement
title: Evaluate reply style with paired loss-sensitive fixtures
summary: "Defines a bounded paired pilot with semantic preservation, isolated host conditions and separate deployment coverage."
proposal: PROP-response-style-survey
status: draft
created_at: 2026-10-20
---

# [PADR-response-style-measurement] Evaluate reply style with paired loss-sensitive fixtures

## 1. Context & Problem Statement

Source popularity does not establish that a rule improves devkit replies. Current repository instructions would
contaminate a native child-agent baseline; prompt-length reductions can conceal missing facts and report fields.

## 2. Decision Drivers

Preserve decision-relevant content, compare reproducible conditions, include Korean and explicit depth requests,
keep collection bounded, and distinguish measured quality from rendered host support.

## 3. Considered Options

| Option | Benefit | Limitation |
| --- | --- | --- |
| Author taste or stars only | No model cost | Cannot measure reply behavior. |
| Native child agents in the current checkout | Convenient | Inherited style invalidates the no-style arm. |
| Fresh isolated host sessions with imported results | Small controlled comparison; no launcher framework | Requires a selected host, verified instruction isolation and an explicit collection budget. |
| Multi-host large repeated evaluation | Broader coverage | Larger cost and configuration surface than this pilot needs. |

## 4. Decision Outcome

Use twelve English/Korean fixtures, three style arms and two fresh repetitions, at most 72 generation attempts
per selected host. `MAT-response-style-measurement-design` defines isolation, exact obligations, calibration and
held-out groups, blind semantic checks, promotion thresholds, error preservation and cost records. Select the
host and execution budget with the user before live collection. Freeze observable binary primary anchors; sum
the two passes per fixture, treat equal sums as ties, and require improvements in two intent categories including
one held-out fixture with no held-out regression. Until then host coverage is an open Planning
question, not a claim of portability. Only synthetic inputs and owned style text are submitted.

Keep fixture/result/scorer materials inside the Development spec Unit. The scorer is standard-library and
imports generation results; it neither launches models nor defines a new distributed evaluation tool. Current
style is retained when the candidate fails the frozen acceptance criteria.

## 5. Consequences

Small-pilot results support only the tested cohort. Deterministic checks catch missing cells and malformed
artifacts; semantic preservation needs independent judgment. No per-rule or cross-host effect is inferred from
aggregate gains, and no unmeasured host is silently considered validated.
