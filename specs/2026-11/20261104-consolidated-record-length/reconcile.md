---
reconcile_id: REC-consolidated-record-length
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
  - file: docs/decisions/2026-11/20261104-consolidated-record-budgets.md
    resolution: modified
  - file: docs/materials/2026-11/20261104-consolidated-record-length/development-evidence.md
    resolution: modified
---

# Reconcile: `SPEC-consolidated-record-length`

## Contract comparison

- `CAP-GOV-evaluation-lifecycle` section 5 records the optional rule-local setting, valid aliases and kind guards,
  terminal feedback statuses, conservative malformed-header fallback, max-budget precedence and bounded warning.
  The existing optional-int resolver supports internal None; TOML disables by omission. Its generic null statement
  now explicitly concerns nonoptional fields. No settings-model or rule-engine change was necessary (AC-01–AC-04).
- The built-in guide and rules reference match the setting, documented ADR rename heuristic, feedback one-entry
  case, existing overrides, numeric message and fidelity-preserving remediation (AC-05).
- `ADR-consolidated-record-budgets` keeps its accepted decision and restatement traces; Confirmation names the
  owned rule and CLI tests. No existing ADR or feedback record was regrouped or shortened.
- Both source playbooks use the configured resolved budget for topic review and preserve every retained decision
  or outcome. Feedback grouping changes remain a separate authorized decision. Existing ordinary rules-check
  completion and fidelity reviews remain; no hygiene phase was added (AC-05).
- `.devkit/config.toml` selects 600 without changing the capability override. Sync updated the two ignored managed
  playbook copies and tracked `.devkit/installation.json`; only the receipt is a tracked sync output.

## Verification

The development evidence records the accepted same-head baseline: in-memory evaluator settings omit only the
option versus configured 600. Six known ADR identities disappear, ADR-document-system remains at line 601,
and four unrelated findings retain their identities and ordinary findings (AC-06). No historical checkout or
fixed-total assertion was used. The ignored probe remains with the worktree.

Independent code review verified the committed implementation; its sole P3 null wording finding is resolved in
reverify-01. Rule/CLI139, spec content633 and affected selection3956 tests passed; lint/format, both affected
package type checks, offline wheel builds, sync and CI rules passed. Independent reconcile verification passed with zero findings; its unchanged pre/post snapshot is recorded in reconcile-check-01.

## Scope and retained boundaries

No architecture, use-case flow, domain term, document model or feature dependency changed. The capability owns
this rule-local behavior; existing authoring and engine contracts stay in place. No required AC is deferred.
The feedback grouping policy remains outside this spec's scope; this budget supplies only its review signal.

## Entrypoints

Keep the capability's existing evaluator and use-case entrypoints and add the file-length rule as its concrete
rule-local doorway. Reject rule tests, integration tests, source playbook directories and generated receipt paths
as capability entrypoints because they are validation/content artifacts rather than runtime doorways.
