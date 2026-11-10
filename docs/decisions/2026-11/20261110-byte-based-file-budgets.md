---
id: ADR-byte-based-file-budgets
title: Use raw bytes for file hygiene budgets
summary: "For file-size hygiene, we use raw byte budgets instead of line counts, to reflect loaded content without wrapping bias, accepting explicit migration of line-based settings."
status: accepted
created_at: 2026-11-10
supersedes: [ADR-consolidated-record-budgets]
---

# [ADR-byte-based-file-budgets] Use raw bytes for file hygiene budgets

## 1. Context & Problem Statement

Line counts change with wrapping and table formatting. Files of similar byte size can receive very different
findings. The hygiene warning is a review signal for content size, not a rule that authorizes deleting contracts.
The builtin already has snapshot-aware byte access and rule-local consolidated selection.

## 2. Decision Drivers

- Measure evaluated content independently of line wrapping.
- Preserve deterministic snapshot evaluation and existing rule identity.
- Preserve consolidated-record fidelity and path-specific budget precedence.
- Make the setting-unit change explicit rather than guessing a conversion.

## 3. Considered Options

- Raise line limits: reduces some warnings but retains formatting bias.
- Add a byte mode beside lines: retains two metrics and ambiguous configuration.
- Replace line limits with byte limits: one metric and explicit migration; selected.

## 4. Decision Outcome

Supersedes in part `ADR-consolidated-record-budgets`: the line-count metric, line-based setting names and the repository's 600-line limits. Alias eligibility, optional rule-local budgeting, max precedence and pure settings resolution remain.

- `RULE-file-length` counts raw evaluated bytes through its workspace cache and reports a file-level finding at
  line 1 with actual/limit bytes. → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- The ordinary default is 49152 bytes; the optional consolidated field remains omitted by default and retains
  its alias eligibility and larger-budget precedence. → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- `max_bytes` and `consolidated_max_bytes` replace the line-based keys; obsolete settings fail existing validation
  without conversion. → `CAP-GOV-evaluation-lifecycle` section 5 (MUST).
- This repository configures 65536 bytes for capabilities and consolidated records. Warnings remain hygiene
  observations and authorize no content deletion or automatic splitting.

## 5. Consequences

Byte budgets better approximate loaded volume, but are not token counts or a proof of topic cohesion. Existing
line settings require an intentional byte value. Rule ID, phase, severity, targeting, eligibility and resolver
ownership remain stable. Historical specs and old outcome text retain their original units behind the partial
pointer.

## 6. Confirmation

Builtin byte-boundary and consolidated tests, snapshot regression, rules CLI settings/output tests and source
playbook checks verify the contract. `CAP-GOV-evaluation-lifecycle` section 5 restates the behavior; the project
configuration records its thresholds.
