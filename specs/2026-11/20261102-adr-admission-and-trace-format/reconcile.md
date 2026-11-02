---
reconcile_id: REC-adr-admission-and-trace-format
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-configuration-language-and-rendering.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-delivery-decision-boundaries.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-immutable-decisions-editable-records.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-keep-uv-run-as-the-agent-facing-devkit-invocation.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-local-and-pull-request-integration.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-response-style.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-share-document-index-and-defer-catalog-build-in-rules-run.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-spec-package-on-devkit.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-test-selection-and-ci.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-writing-and-terminology-guidance.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-kind-definition-table-keyed-on-the-declared-kind-enum.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-adaptive-dev-approach-name.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-retire-stale-integration-approval-clauses.md
    resolution: modified
---

# Reconcile: `SPEC-adr-admission-and-trace-format`

- `CAP-HARN-agent-guidance` §4.3, row `decision-writing`, now describes these parts of the instruction:
  - the admission criteria that ADRs and PADRs share;
  - the declarative clause format with a trailing trace `→ <ID> <section or rule> (<keyword>)`.
- The 13 ADRs that `SPEC-adr-normative-outcomes` and `SPEC-retire-stale-integration-clauses` marked now carry 35
  traces in the new format. Each trace names the section or rule of the restating document and the keyword that
  document uses.
  - These are format-only edits. The rewrites turn the modal verb added by those specs into a declarative verb.
  - The three keywords of `ADR-delivery-decision-boundaries` that predate those specs keep their original wording.
- Bundle guidance, which is not Living Spec, follows the same rules:
  - `decision-writing` and the `decision` template carry the When to Write section and the trace format.
  - Planning creates a PADR only for an admissible decision. Handoff is unchanged and still promotes every PADR left.
  - The completion classification and `sdd-overall-refactor` send to an ADR only the decisions that meet the
    criteria. Other choices go to `plan.md`.

## Entrypoints

No capability or use case entrypoint changes; the change is documentation and guidance.
