---
id: PLAN-adr-normative-outcomes
spec: SPEC-adr-normative-outcomes
---

# Technical Plan: `SPEC-adr-normative-outcomes` ADR normative outcomes and Living Spec restatement

## 1. Constitution & Invariant Review

None.

- The change adds an authoring rule for future ADRs. It also moves existing lasting clauses into the documents that
  already own their feature areas. It changes no decision, so it needs no new ADR.
- The in-place ADR edits change format only (keyword and restating ID on existing clauses). That is the edit class
  `ADR-immutable-decisions-editable-records` allows.
- Bundle text cites no real document ID of this repository (agent-asset-writing self-containment).

## 2. Architecture Overview & Impact

Documentation and agent guidance only. No code path changes.

| Component | Change | Serves |
| --- | --- | --- |
| docs bundle `instructions/decision-writing.md` | Decision Outcome as one list item per clause. A normative clause carries one RFC 2119 keyword and its restating ID; a clause with no restating ID carries no keyword. The restating document is authoritative. `Confirmation` may cite those IDs. | AC-01 |
| docs bundle `templates/decision.md` | The Decision Outcome example shows one normative clause and one rationale clause, with placeholder IDs. | AC-02 |
| spec bundle `skills/spec/references/completion.md.jinja` | Living Spec classification: lasting rules → capabilities or architecture with keywords; their reasons → ADR citing the restating ID. | AC-03 |
| `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py` | Asserts the new decision-writing and template rules. | AC-01, AC-02 |
| `CAP-HARN-agent-guidance` | Updates the `decision-writing` row. Restates the `ADR-roadmap-and-milestones` and `ADR-writing-and-terminology-guidance` clauses. | AC-01, AC-04 |
| `CAP-GOV-rule-authoring` | Fixes §Optional `inputs` to match `CAP-GOV-evaluation-lifecycle`. Restates the read-only shared `DocumentIndex` rule. | AC-04, AC-05 |
| `CAP-DOCS-document-model` | Restates the kind-table accessor rule and the allowed in-place ADR edits and decision-change definition. | AC-04 |
| `CAP-DLV-adaptive-development`, `CAP-DLV-project-policy` | Restates the naming rule and the helper-autonomy and escalation rules. | AC-04 |
| `CAP-DIST-content-packages`, `CAP-DIST-sync-and-transactions`, `CAP-DIST-context-and-playbooks` | Restates the response-style limits, the approval-text and cloud/local text rules, and the `uv run devkit` invocation rule. | AC-04 |
| `CAP-INT-mcp-services` | Restates the GitHub adapter limits and the checks-pending flow. | AC-04 |
| `ARCH-05-1-containers`, `ARCH-07-deployment` | Restates generic-first and the test-selection graph rules. | AC-04 |
| The 13 ADRs of `SPEC-adr-normative-outcomes` §5 | Each restated clause gets its keyword and restating ID in Decision Outcome. | AC-04 |

### Choices

- **Verify before restating.** Before writing a clause, check it against the current code, bundle text and
  capabilities. If a clause is stale, superseded or one-off, record it in `reconcile.md` with evidence instead of
  restating it.
- **Keyword strength.** Use MUST or MUST NOT where the ADR states an obligation or prohibition that a check, review or
  hard-to-undo consequence backs. Use SHOULD for working habits. Use MAY for permissions. This follows
  `contract-authoring`.
- **Owner documents.** Start from `SPEC-adr-normative-outcomes` §5. Move a clause to a better owner only when the
  initial owner does not cover that feature area, and record the move in `reconcile.md`.
- **File length.** Keep each capability within `RULE-file-length` (600 lines). Restate tersely, and cite an existing
  section instead of duplicating it.

## 3. Error Handling & Edge Cases

- **Clause contradicted by the code.** Do not restate it. Report it in `reconcile.md` as a finding for the user,
  because it changes no decision here.
- **Clause already partly restated.** Add only the missing part, next to the existing text.
- **ADR with a "Superseded in part" line.** Leave the replaced clauses untouched.

## 4. Verification & Test Plan

- `uv run devkit rules check` in the worktree: document identity, references, file length, task coverage.
- `uv run devkit rules check --phase hygiene` on the edited bundle assets: no `RULE-agent-asset-wording` warning.
- `rg -n '\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9]'` on the edited bundle files: placeholders only.
- `just test-affected`: covers `test_writing_guidance.py` and any guidance test that touches the edited files.
