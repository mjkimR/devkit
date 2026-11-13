---
id: PROP-linter-change-notices
title: Non-blocking rule notices for changed code
summary: "Introduce a distinct notice severity for change-scoped linter guidance while preserving warning semantics. Define changed-block targeting and read-time context so agents can review relevant considerations without remediation or approval records."
status: reviewing
created_at: 2026-11-11
target_area: governance/
priority: low
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - governance/
  excludes:
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-linter-change-notices] Non-blocking rule notices for changed code

## 1. Background & Hypothesis

Some edits deserve a contextual reminder even when the result is valid. Adding a broad exception handler can
justify checking whether failure becomes indistinguishable from success; changing a public signature can justify
checking callers. Neither trigger alone proves a defect or requires a fix.

Warnings should retain their meaning as suspected problems that warrant review and possible correction.
Reporting these reminders as warnings dilutes that signal. Including them in hygiene creates recurring work for
conditions that only need consideration when they change.

Hypothesis: a distinct linter notice severity, scoped to relevant changed blocks, can supply timely guidance
without creating unresolved violations, approval requests or maintenance obligations. This is a low-priority
backlog improvement; this draft does not start implementation.

Current rule contracts expose `Severity.ERROR`, `Severity.WARNING` and `Severity.INFO`, file targets and Git
snapshot metadata. They do not expose a shared changed-hunk API. The Agent Advisory Protocol already distinguishes
`NOTICE` from `WARNING`; its notice level does not affect exit status, including under `--strict`.
Related contracts: `CAP-GOV-rules-engine`, `CAP-GOV-evaluation-lifecycle`, `CAP-GOV-rule-authoring`,
`CAP-ADV-agent-advisory-protocol` and `CAP-HOST-lifecycle-observation`.

## 2. Technical Spike Questions

- **Q1 — Severity and compatibility:** Should `Severity.INFO` migrate to `notice`, remain as a compatibility alias,
  or retain a distinct purpose? Define the effect on settings, severity overrides, text/JSON output, counts,
  workflow checks and commit gates. Distinguish rule notice severity from the result envelope's `notices` field.
- **Q2 — Change evidence:** How should rules obtain changed blocks for working-tree, staged and CI evaluations?
  Set comparison bases and behavior for untracked files, partial staging, deletions, renames and unavailable Git
  evidence. Keep snapshot evaluation independent of unstaged content.
- **Q3 — Semantic scope:** How should an edit select the enclosing construct needed for a useful judgment?
  Account for deletion-triggered findings and findings whose reported line is outside the added lines.
- **Q4 — Read-time context:** Which supported read surface can expose whether a file changed and its relevant
  hunk ranges or excerpts? Determine whether existing host integration can supply this without intercepting
  every native file read or depending on one agent product.
- **Q5 — Repetition:** Where should duplicate suppression live, and what bounds its lifetime? Prefer the same
  rule, file and changed content to produce one reminder within an agent session; a subsequent relevant edit
  can produce another. Independent CLI runs should remain inspectable and deterministic.

## 3. Proposed Design & Impact

### Proposed behavior

- Keep `linter` as the execution phase and introduce `notice` as a distinct rule severity.
- Preserve existing warning behavior, including warning promotion under `--strict`.
- A rule notice alone leaves exit status successful, including under `--strict`, and does not fail a commit gate
  or workflow cleanliness check. Independent errors and execution failures retain their existing behavior.
- A notice invites consideration; it does not require a fix, acknowledgement, waiver or approval record.
- Represent change targeting separately from severity so changed-block warnings remain possible.
- Change-scoped notice rules run against relevant edits and do not participate in hygiene scans or report
  unchanged historical triggers during untargeted scans.
- Allow rules to read an enclosing function or file for context while limiting emitted notices to constructs
  affected by the selected change, including relevant deletions.
- Provide changed-file status and changed-block evidence at the selected read surface, with bounded excerpts.
- Suppress repeated read-time reminders for identical relevant changes within the chosen session boundary.
  Preserve visibility in explicit rule-check results.
- Give notices stable machine-readable identifiers, locations and a concrete consideration, such as:
  “A broad exception handler was added; check whether this fallback hides a failed operation.”

### Expected impact

The rules engine, rule authoring API and settings need a notice contract and shared change evidence. CLI and
advisory adapters need consistent text/JSON representation and severity counts. Commit gates and workflow checks
need explicit non-blocking treatment. Read-time delivery may require a bounded host integration change, depending
on Q4. Living Spec and rule-authoring guidance should describe the chosen behavior when implementation lands.

### Scope excluded

- Converting existing warning rules into notices without reviewing their semantics.
- Building a catalog of all candidate reminder rules; select one representative rule or fixture for validation.
- General-purpose interception of every host's native file reads.
- Acknowledgement databases, approval gates or permanent per-file suppression records.
- Automatic fixes for judgment-based reminders.

## 4. Lifecycle & Retirement Criteria

Keep this proposal in Backlog at `priority: low`. Start Planning when this improvement is selected; use that
stage to settle severity compatibility, change evidence and the supported read surface. Size `M` assumes one
cohesive rule-engine improvement, not a separate cross-host read interception platform.

Acceptance should require a settled contract and verification plan covering:

1. A relevant edit produces a notice; an unchanged occurrence and an unrelated edit produce none.
2. A deletion affecting the checked construct can produce a notice.
3. A notice-only run succeeds with and without `--strict`; existing warnings preserve strict behavior.
4. Hygiene does not run the change-scoped notice rule.
5. Staged and CI runs use their exact source snapshots, including partial staging.
6. Text and JSON distinguish notices from warnings with stable rule identifiers and locations.
7. The supported read surface provides changed-file and hunk context, suppresses repeated identical reminders
   within the chosen session boundary, and delivers a fresh reminder after a relevant content change.
8. Legacy `INFO` findings and severity settings follow the documented compatibility policy.

Retire or narrow the proposal if change evidence and read-time delivery cannot provide useful guidance at
proportionate cost. Implementation and Living Spec reconciliation follow acceptance and handoff.
