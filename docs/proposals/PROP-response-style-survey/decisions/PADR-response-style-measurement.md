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
keep collection bounded, and distinguish observed rule adherence, subjective reading preferences and rendered
host support. None is a universal answer-quality score.

## 3. Considered Options

| Option | Benefit | Limitation |
| --- | --- | --- |
| Author taste or stars only | No model cost | Cannot measure reply behavior. |
| Native child agents in the current checkout | Convenient | Inherited style invalidates the no-style arm. |
| Fresh isolated host sessions with imported results | Small controlled comparison; no launcher framework | Requires a selected host, verified instruction isolation and an explicit collection budget. |
| Multi-host large repeated evaluation | Broader coverage | Larger cost and configuration surface than this pilot needs. |

## 4. Decision Outcome

The structured comparison option uses twelve English/Korean fixtures, three style arms and two fresh repetitions,
at most 72 generation attempts per selected host. This option has not been selected or authorized; a small set
of paired examples is enough to begin a practical inspection, with collection scope chosen before execution. `MAT-response-style-measurement-design` defines isolation, exact obligations, calibration and
held-out groups, blind semantic checks, promotion thresholds, error preservation and cost records. Select the
host and execution budget with the user before live collection. Freeze observable binary primary anchors; sum
the two passes per fixture, treat equal sums as ties, and label changes by intent category, including held-out cases, without interpreting that compliance count as
overall quality or automatically choosing a style. Until then host coverage is an open Planning
question, not a claim of portability. Only synthetic inputs and owned style text are submitted.

Keep fixture/result/scorer materials inside the Development spec Unit. The scorer is standard-library and
imports generation results; it neither launches models nor defines a new distributed evaluation tool. A candidate that violates factual or required-output obligations is revised or rejected. Style preference is a
separate human judgment using actual examples and stated tradeoffs in the existing final review; no additional
workflow approval gate is created.

## 5. Consequences

Small-pilot observations describe only the tested cohort and cannot establish how much better a reply is.
Readability, useful depth and tone remain partly subjective; a metric is a proxy or contract check, not that judgment. Deterministic checks catch missing cells and malformed
artifacts; semantic preservation needs independent judgment. No per-rule or cross-host effect is inferred from
aggregate gains, and no unmeasured host is silently considered validated.
