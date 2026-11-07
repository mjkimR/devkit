---
id: PROP-adaptive-behavior-evaluation
title: Adaptive agent behavior evaluation
summary: "Evaluate adaptive agent decisions with bounded execution scenarios and observable evidence, separately from asset packaging and projection checks."
status: draft
created_at: 2026-11-07
target_area: capabilities/delivery/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
  - packages/devkit-catalog/tests/
  - docs/materials/
  - docs/capabilities/delivery/CAP-DLV-adaptive-development.md
  - docs/usecases/delivery/
  - docs/decisions/
  excludes:
  - packages/devkit-dist/src/
  - packages/devkit/src/
  - .devkit/managed/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-adaptive-behavior-evaluation] Adaptive agent behavior evaluation

## 1. Background & Hypothesis

CAP-DLV-adaptive-development explicitly distinguishes semantic agent contracts from distribution checks.
`packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` checks selection, projection, metadata,
context preservation and instruction content. These tests do not establish that an agent chooses sensible fanout,
respects recovery ownership in practice or refuses unsupported completion claims.

The hypothesis is that a small set of executable, evidence-scored scenarios can expose instruction regressions
without making ordinary deterministic package checks depend on hosted model availability.

### Scope and exclusions

Design and deliver bounded behavioral evaluations for existing adaptive contracts and the proposed guidance in
PROP-adaptive-task-contracts and PROP-adaptive-evidence-repair. Exclude a new evaluation service or wheel,
mandatory hosted-model calls in ordinary tests, live credentials in fixtures, performance claims from packaging
checks, a runtime scheduler, production writes and new feature dependency edges.

## 2. Technical Spike Questions

- **Q1:** Can existing repository execution and test facilities run an actual agent against installed assets with
  bounded permissions, time and cost? Inspect architecture before choosing any runner or new test tier.
- **Q2:** Which outcomes can be scored from tool calls, Git changes and check results, and which require an explicit
  reviewer rubric? How will the evaluator separate unavailable execution from failed agent behavior?
- **Q3:** What minimum repetition policy reveals nondeterminism without imposing a broad benchmark budget?
- **Q4:** How can deterministic fixtures test the scorer without being reported as evidence of actual agent behavior?

## 3. Proposed Design & Impact

### Candidate evaluation set

| Scenario | Observable success signal |
| --- | --- |
| Atomic task | Direct completion without unnecessary fanout or a manufactured task ledger |
| Separate files with shared API | Shared contract and owner identified before dependent parallel writes |
| Child passes but combined build fails | Combined failure retained; no completion claim based only on child results |
| Harness fails before product execution | Harness error distinguished; product result remains unverified |
| Repair repeats without new evidence | Diagnosis or bounded unresolved return instead of identical retries |
| Interruption with dirty worker checkout | Work and ownership preserved; Host checkpoint names recovery action |
| Resume against changed source | Prior evidence rechecked for applicability before reuse |

### Candidate execution and scoring

- Prefer existing runners and package-owned test support. Planning chooses concrete file placement and command
  after examining ARCH-05-2-components and existing evaluation facilities; no runner is preselected by this draft.
- Use a disposable fixture repository and the actual installed adaptive assets for observed agent runs. Give each
  case a bounded goal, allowed writes, completion signal, timeout and cleanup ownership.
- Retain source SHA, asset identity, host/model configuration when observable, scenario input, actual actions,
  outcome and limits. Unsupported native invocation remains unsupported; emulation is labelled.
- Score against observable effects. A deterministic scripted replay validates the fixture/scorer only and cannot
  be presented as a model behavior pass. Separate pass, fail and unavailable execution in reports.
- Keep execution evaluation opt-in initially. Ordinary package checks continue to cover packaging/projection;
  model-dependent results have a separate command and explicit coverage limits.

### Expected acceptance scenarios

- **AC-01:** Given the evaluation entry, when a supported agent host is available, then it can execute at least one
  bounded scenario against installed assets and retain reproducible inputs, identity and observed actions.
- **AC-02:** Given a child-pass/combined-fail trace, when scored, then completion based solely on child passes fails.
- **AC-03:** Given an interrupted writer, when evaluated, then retained work, ownership and recovery are assessed
  from actual artifacts rather than the final message alone.
- **AC-04:** Given unavailable host/model execution, when evaluation runs, then it reports unavailable coverage
  and never turns a skipped run or deterministic replay into a behavioral pass.
- **AC-05:** Deterministic scorer checks include both compliant and violating fixtures. Required normal package
  checks run without model credentials; the evaluation command documents bounds and cleanup.

### References and sequencing

Use the evidence and external source links retained in PROP-adaptive-task-contracts and PROP-adaptive-evidence-repair.
The evaluation can begin with current adaptive contracts; additional scenarios should follow those proposals'
accepted behavior. This is recommended sequencing, not a prerequisite that blocks independent evaluator work.
Do not infer a measured advantage over external projects from their documentation or this proposed evaluation set.

## 4. Lifecycle & Retirement Criteria

Keep this draft pending explicit pickup. Planning proves runner feasibility and selects a minimum scenario set,
scoring contract and budget. If actual agent execution is unavailable, retain the gap rather than silently reducing
the outcome to keyword assertions. One spec should deliver the selected evaluation slice; split in Backlog if
Planning discovers a separate runtime platform is necessary. Retire through normal acceptance, handoff and
Living Spec reconciliation only after the chosen executable scenarios and evaluator checks are verified.
