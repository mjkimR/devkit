---
id: PLAN-formal-doc-authoring-checkpoints
spec: SPEC-formal-doc-authoring-checkpoints
---

# Technical Plan: `SPEC-formal-doc-authoring-checkpoints` Formal documentation checkpoints: route facts, review reimplementability, record assessments

## 1. Constitution & Invariant Review

- `ADR-recorded-formal-docs-assessment` (promoted at handoff) authorizes the new `RULE-reconcile-contract` causes and
  the reviewer classes; the change implements its outcome clauses and changes no other architecture invariant.
- `ADR-formal-document-delivery-integration` keeps the formal assessment in existing records under semantic review and
  rejects a separate impact manifest. Compatible: coverage lives in the existing record and its typed `related_*`
  relation fields; `formal_docs` holds only reasons and adds no registry.
- `CAP-DOCS-documentation-ownership` §3.1 rule 1 (one primary owner): the fact-type table is canonical in the
  capability; `living-spec-writing` restates the same rows for agents because a bundle cites no repository document.
- Agent-asset self-containment: new bundle text cites no repository document ID.

## 2. Architecture Overview & Impact

| Component | Change | AC |
| --- | --- | --- |
| docs bundle `instructions/living-spec-writing.md` | Fact-type routing table under "Responsibility and design navigation" | AC-01 |
| docs bundle `instructions/capability-writing.md`, `templates/capability.md` | "What stays out" section; one §3 comment clause | AC-01 |
| docs bundle `instructions/design-writing.md` item 6, `templates/design.md` | Datasheet SHOULD condition and contents | AC-01 |
| docs bundle `instructions/document-writing.md`, new `templates/reference.md` | "Reference pages" section; template with `Code \| Level \| Condition \| Fix` | AC-01, AC-02 |
| docs `AGENTS.md`, spec `AGENTS.md.jinja` | Template list gains `reference` | AC-02 |
| `test_distribution.py`, `test_ux_guidance.py` | Pinned template set gains `reference` | AC-02 |
| `features/governance/usecases/reconcile_contract.py`, rule guide and tests | `formal_docs` form causes; snapshot coverage requirement for newly resolved records | AC-03..AC-06 |
| spec bundle `spec-sync`, `reconcile-reviewer`, `spec-plan`, `spec-review` | Schema, reviewer classes and routing sentences | AC-07 |
| `CAP-DOCS-documentation-ownership`, `CAP-DOCS-document-model`, `CAP-GOV-spec-rules`, `CAP-DLV-delivery-workflows` | Living Spec reflection | AC-08 |
| `test_worker_inspect.py`, `test_formal_document_lifecycle_scenarios.py` | Fixtures that resolve records in snapshot runs gain coverage | AC-04 |

No new dependency or feature edge: the rule reads Git through the `devkit_core.core` helpers it already uses.

## 3. Component & Interface Design

Record frontmatter (the `spec-sync` schema):

```yaml
reconcile_id: REC-<slug>
status: resolved
targets: [...]
related_designs: [DESIGN-<slug>]          # affected IDs, checked by RULE-document-reference
formal_docs:
  domain: "none: <bounded source-based reason, at least 20 non-whitespace characters>"
  operations: "none: <...>"
```

`reconcile_contract.py`:

- `_problems(data)` gains the form causes (every run, only when `formal_docs` is present):
  `formal_docs must be a mapping of design, domain and operations`; `formal_docs.<key> is not a role (design, domain,
  operations)`; `formal_docs.<role> must be a string starting "none: "`; `formal_docs.<role> needs a reason of at
  least 20 non-whitespace characters, has <n>`; `formal_docs.<role> conflicts with related_<plural>: give IDs or a
  none reason, not both`.
- `_coverage(ctx, relative, data)`: in a snapshot run, for a `resolved` record in `snapshot.changed` that no parent
  has `resolved`, report `formal_docs role <role> is not covered: list affected IDs in related_<plural> or give
  formal_docs.<role>: "none: <reason>"` per uncovered role. Parents: `snapshot.base`; in `staged` mode also every
  object ID listed in `MERGE_HEAD`, `CHERRY_PICK_HEAD` and `REVERT_HEAD` under the Git directory. A parent "has it
  resolved" when `git show <parent>:<path>` parses with `status: resolved`; an unreadable or absent parent version
  does not.
- Role fields: `design` → `related_designs`, `domain` → `related_domains`, `operations` → `related_operations`;
  a role is covered by a nonempty list or a well-formed reason.

## 4. Error Handling & Edge Cases

- A malformed `formal_docs` reports form problems and suppresses the snapshot checks, as other form problems do.
- A pending record, a record resolved at the base, a completed bundle's record in a plain run and a record resolved
  in an in-progress merge, cherry-pick or revert head are not required to carry coverage.
- Git failures reading a parent are treated as "not resolved there" so a new record is checked.

## 5. Formal Document Assessment

- **Design**: no affected DESIGN. The parent lookup is a local helper the rule guide §1 describes.
  `DESIGN-workflow-stage-evaluation` reads only `reconcile.md` `status`, whose values and meaning do not change; the
  other designs cover distribution transactions and proposal handoff.
- **Domain**: no affected DOMAIN. `DOMAIN-feedback-lifecycle` names `reconcile.md` only as where a feedback outcome is
  recorded; no concept, identity or lifecycle changes.
- **Operations**: no affected OPS. The new violations are ordinary rule output with remediation in the rule guide; no
  symptom routing changes.

## 6. Verification & Test Plan

- Rule tests in `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/reconcile_contract/tests/test_rule.py`
  for AC-03..AC-05 (staged and ci, merge head, form causes, mixes).
- `uv run devkit rules check specs/` on the base and the head, comparing `RULE-reconcile-contract` lines (AC-06).
- `test_distribution.py`, `test_ux_guidance.py` and a sync projection check (AC-02).
- Bundle text read and `rg` self-containment check (AC-01, AC-07); capability rows compared with the instruction rows
  (AC-08).
- `uv run devkit rules check --ci --base a7d96154e`, `just lint-check`, `just test-affected --base a7d96154e` with its
  full fallback.
