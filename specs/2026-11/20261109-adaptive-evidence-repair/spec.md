---
id: SPEC-adaptive-evidence-repair
title: Adaptive failure verification and bounded repair
summary: Guide risk-based failure verification and evidence-driven repair, retaining only the recovery facts needed to resume adaptive development.
status: planned
created: 2026-11-09
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-adaptive-evidence-repair] Adaptive failure verification and bounded repair

## 1. Problem Statement & Motivation

Handed off from proposal PROP-adaptive-evidence-repair on 2026-11-09.

### 1. Background & Hypothesis

CAP-DLV-adaptive-development requires representative usage, truthful evidence, bounded repair and failure
checkpoints. It does not explain how to select relevant failure paths or distinguish repeated effort from new
information. Current context already retains decisions and reopening conditions; it needs only useful recovery
facts rather than an additional memory subsystem.

The hypothesis is that risk-based failure probes and evidence-based repair decisions reduce false completion and
repeated unsuccessful attempts while preserving lightweight adaptive iteration.

#### Scope and exclusions

Extend verification, repair and current-context guidance as one evidence-to-recovery loop. Exclude a universal
adversarial test matrix, fixed QA pipeline, mandatory screenshots or scores, new state store, transcript retention,
automatic deletion of failed work, runtime retry engine and new feature dependency edges.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Adaptive failure verification and bounded repair so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1:** How should the coordinator select a normal path, a relevant failure path and an integration edge, allowing
  inapplicable cases to be omitted and unavailable checks to remain explicitly unverified?
- **Q2:** What evidence distinguishes a product defect from a test harness or environment failure?
- **Q3:** What default repair bound and no-progress signal prevent loops without stopping useful diagnosis or
  treating elapsed time as permission? Compare an assignment-specific bound with a small fallback bound.
- **Q4:** Which failed attempts still affect the next action and belong in mutable current context?

### 3. Proposed Design & Impact

#### Candidate design

- Select checks from the actual changed behavior and consequence of failure. Consider malformed input, duplicate
  execution, cancellation/resume, stale state and partial failure only when relevant. Keep probes bounded and
  within existing authority; never require production writes to obtain evidence.
- Record expected signal, actual command or interaction, source identity, outcome and limitation. Separate harness
  setup failure, environment unavailability and reproduced product failure before assigning repairs.
- On a failed check, compare symptom, root-cause hypothesis, attempted change and new evidence. Repeating the same
  failure without new evidence triggers diagnosis, a revised split or an explicit unresolved report instead of
  another identical retry. Success still requires the original behavior to pass affected checks.
- Retain caller-supplied repair bounds; Planning chooses a proportionate fallback when none exists. A bound limits
  the repair strategy and never authorizes silently abandoning required outcomes or weakening acceptance criteria.
- Keep checkpoint ownership with the Host. When useful for resume, retain the failed approach and reason, source
  identity, surviving hypothesis, condition for retry and next recovery action in `.devkit/adaptive-dev.md`.
- Preserve active, dirty and unmerged work under existing recovery authority. Clean up only assigned disposable
  probe outputs and processes; no blanket cleanup or separate immutable experiment history.

#### Planning decisions and verification

- Keep an assignment's own bounds when present. Without one, after two consecutive attempts produce the same
  symptom and no materially new diagnostic evidence, change strategy before another equivalent attempt. A new
  observation is material when it changes or tests a causal hypothesis, isolates a dependency, or identifies a
  distinct failure; a repeat of the same output alone is not progress. This is a diagnostic trigger, not a cap on
  authorized work or a completion condition. Continue safe, useful diagnosis; report an unresolved blocker only
  when the next necessary action cannot be performed within authority or available resources.
- When a probe fails before valid product execution, classify a harness or environment cause only on evidence.
  Otherwise retain an unknown cause and leave the product unverified. A harness fix must be followed by a valid
  product probe before claiming the product behavior passed.
- Development reviews the relevant scenario walkthroughs with concrete inputs, expected actions and an evidence
  record covering actual behavior, source identity, observations and limitations. Existing packaging tests establish
  asset/projection properties only. Live agent execution is separate and may be unavailable; report it as unverified
  rather than implying the walkthrough proves model behavior. Do not gate this change on another proposal.
- Example: a test fixture fails to start twice with the same import error. Inspect the fixture environment or import
  path before a third equivalent run; preserve the failed output and leave the product check unverified. A later
  repaired harness must rerun the product flow.

#### Expected acceptance scenarios

- **AC-01:** Given a changed stateful operation, when verifying it, then the coordinator chooses relevant failure
  and integration probes alongside the normal path and records actual source-specific outcomes.
- **AC-02:** Given a broken test harness, when the probe fails, then the result classifies a harness failure only when supported by evidence; an ambiguous cause remains unknown.
  Product behavior stays unverified until a valid probe runs.
- **AC-03:** Given repeated identical failures without new evidence, when the repair bound or no-progress
  condition is met, then the agent changes diagnostic strategy or reports the unresolved defect and next action.
- **AC-04:** Given a useful failed attempt before interruption, when checkpointing, then the Host retains its
  reason and retry condition with source identity and ownership; a resumed agent rechecks applicability.
- **AC-05:** Given a low-impact stateless change, when choosing probes and notes, then the agent omits irrelevant
  adversarial scenarios and unnecessary history. Existing context and unmerged work remain preserved.

#### Evidence and references

These inspected guides motivate candidate behavior; their numeric retry limits are not adopted by this draft:
- [OMX UltraQA](https://github.com/Yeachan-Heo/oh-my-codex/blob/HEAD/skills/ultraqa/SKILL.md): dynamic failure scenarios,
  harness classification and bounded cycling.
- [Agency orchestrator](https://github.com/msitarzewski/agency-agents/blob/HEAD/specialized/agents-orchestrator.md):
  specific QA feedback and retry bounds; exclude its fixed role sequence.
- [Agency reality checker](https://github.com/msitarzewski/agency-agents/blob/HEAD/testing/testing-reality-checker.md):
  compare claimed and observed user journeys; exclude universal screenshots and default failure ratings.
- [OmO memory overview](https://github.com/code-yeongyu/oh-my-openagent/blob/HEAD/README.md): avoid repeating mistakes;
  use existing current context instead of importing the memory runtime.

### 4. Lifecycle & Retirement Criteria

Keep this draft until explicit Planning pickup. Planning recommends the no-progress trigger and evidence distinctions above; acceptance settles the direction. One spec can deliver this guidance and its relevant checks with CAP-DLV-adaptive-development reconciled.
PROP-adaptive-task-contracts can proceed independently; coordinate overlapping orchestration edits if developed
concurrently. PROP-adaptive-behavior-evaluation separately evaluates execution behavior.

