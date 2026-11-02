---
reconcile_id: REC-adr-normative-outcomes
status: pending
targets:
  - file: docs/architecture/ARCH-05-1-containers.md
    resolution: modified
  - file: docs/architecture/ARCH-07-deployment.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-development.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-content-packages.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
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
  - file: docs/decisions/2026-10/20261022-roadmap-and-milestones.md
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
  - file: docs/decisions/2026-11/20261102-retire-scheduled-roadmap-review.md
    resolution: modified
---

# Reconcile: `SPEC-adr-normative-outcomes`

## Authoring rule (AC-01 to AC-03)

- The docs bundle's `decision-writing` instruction and `decision` template define clause-level Decision Outcomes. A
  normative clause carries one RFC 2119 keyword and its restating capability or architecture ID. A rationale clause
  carries no keyword. The restating document is authoritative.
- The spec bundle's completion classification and the `sdd-overall-refactor` workflow route lasting rules to
  capabilities or architecture with keywords, and their reasons to an ADR that cites the restating ID.
- `CAP-HARN-agent-guidance` §4.3 describes the `decision-writing` row with the clause format.

## Restated ADR-only clauses (AC-04)

| ADR | Restated in | Keywords |
| --- | --- | --- |
| `ADR-adaptive-dev-approach-name` | `CAP-DLV-adaptive-development` rule 18 | MUST, MUST NOT |
| `ADR-kind-definition-table-keyed-on-the-declared-kind-enum` | `CAP-DOCS-document-model` §3.2 | MUST, MUST NOT |
| `ADR-response-style` | `CAP-DIST-content-packages` §5 | MUST, MUST NOT |
| `ADR-share-document-index-and-defer-catalog-build-in-rules-run` | `CAP-GOV-rule-authoring` §2 | MUST NOT |
| `ADR-spec-package-on-devkit` | `ARCH-05-1-containers` §2.5 | MUST |
| `ADR-test-selection-and-ci` | `ARCH-07-deployment` §1.3 | MUST, MUST NOT, SHOULD |
| `ADR-writing-and-terminology-guidance` | `CAP-HARN-agent-guidance` §4.3 | MUST |
| `ADR-configuration-language-and-rendering` | `CAP-DIST-content-packages` §1 (cloud text, installation guides) | MUST, MAY |
| `ADR-delivery-decision-boundaries` | `CAP-DLV-project-policy` rule 10 | MUST, MUST NOT, SHOULD, MAY |
| `ADR-immutable-decisions-editable-records` | `CAP-DOCS-document-model` §Decision supersession, scoped to `sdd` | MUST, MAY |
| `ADR-keep-uv-run-as-the-agent-facing-devkit-invocation` | `CAP-DIST-context-and-playbooks` §1 | MUST, MAY |
| `ADR-local-and-pull-request-integration` | `CAP-INT-mcp-services` §Authority and route limits, codes table | MUST, MUST NOT |

In each ADR, the restated clauses carry the keyword and `→ <ID>` as a format-only edit. Items were split only where
a marked item held more than one keyword or mixed normative and rationale sentences.

Owner choices that differ from spec §5 are listed in `PLAN-adr-normative-outcomes` §5.

### Clauses classified, not restated

- **`ADR-roadmap-and-milestones` Review (stale).** Commit `e9f589c4` removed the `spec-next` idle step that reported
  the review, and no guidance reports it any more. The user decided to retire it: `ADR-retire-scheduled-roadmap-review`
  supersedes that clause only (AC-07). The Consequences line of `ADR-milestone-merging` that mentions the review's date
  trigger is history of that decision and stays as written.
- **`ADR-configuration-language-and-rendering` approval-form text (stale).** It describes the MCP confirmation
  channel, which `2a491881` and `8f570521` removed. The still-valid domain-owned English and Korean copy is already in
  `CAP-DIST-sync-and-transactions` and `CAP-DLV-proposal-planning`. Handed off as `FB-stale-approval-form-clause`.
- **`ADR-local-and-pull-request-integration` "`--auto`/`--admin` refused before the confirmation" (contradicted).**
  The code refuses these cases after approval (`INTEGRATION_CHECKS_PENDING`, `INTEGRATION_MERGE_REFUSED`).
  `CAP-INT-mcp-services` states the code's behavior, and the ADR sentence stays unmarked. Handed off as
  `FB-pr-auto-admin-refusal-point`. The `integration_resume` sentence is unmarked because `ADR-host-cli-lifecycle-authority`
  superseded it.
- **One-off clauses.** The following stay unmarked as rationale:
  - `ADR-response-style`: candidate tracking and the measurement scope.
  - `ADR-test-selection-and-ci`: the helper-extraction limit.

### Observations kept as written

- `ADR-kind-definition-table-keyed-on-the-declared-kind-enum` names `ID_SOURCE` and `ID_PATTERN` as the import-time
  exceptions. `PREFIXES` is also built at import (`ids.py:20`), and `CAP-DOCS-document-model` §4.4 states this.
- The Follow-ups line of `ADR-delivery-decision-boundaries` says the principle remains in the ADR.
  `CAP-DLV-project-policy` rule 10 now restates it. The line is history of the decision.

## Snapshot-gate contradiction (AC-05)

`CAP-GOV-rule-authoring` §Optional `inputs` now agrees with `CAP-GOV-evaluation-lifecycle` and `evaluator.py`
`scope_rules`:

- Git snapshot runs skip a rule when no diff candidate path matches its `inputs`.
- Deleted paths count as candidates.
- A `.devkit/config.toml` or `.devkit/installation.json` candidate keeps every rule.

## Deferred work handoff

- Non-Goal 2 (prose rules without keywords in 28 capability and architecture documents): `FB-contract-docs-without-rfc-keywords`.
  The user plans it as an `overall-refactor` after this spec lands.
- `FB-bundle-text-bare-devkit-commands`: whether bundle prose counts as documented agent-facing commands under
  `CAP-DIST-context-and-playbooks`.

## Entrypoints

This change modifies no code path, so it has no capability or use case entrypoint to derive.
