---
reconcile_id: REC-formal-doc-authoring-checkpoints
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261116-recorded-formal-docs-assessment.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-roles.md
    resolution: waived
    rationale: Its reconcile-reviewer row defers the verification content to CAP-DLV-delivery-workflows rule 15, which now carries the four classes.
formal_docs:
  design: "none: no DESIGN describes the reconcile record or rule; DESIGN-workflow-stage-evaluation reads only reconcile.md status, whose values are unchanged"
  domain: "none: no concept, identity or lifecycle changes; DOMAIN-feedback-lifecycle names reconcile.md only as where a feedback outcome is recorded"
  operations: "none: the new violations are ordinary rule output with remediation in the rule guide; no OPS routes reconcile symptoms"
---

# Formal documentation checkpoints reconciliation

## Fact-type routing and capability guidance

`CAP-DOCS-documentation-ownership` §3.1 gains rule 7 (fact-type routing) with the nine-row table and rule 8
(observable contract, SHOULD); §3.3 gains rule 6 (datasheets, SHOULD). The summary names the fact-type and
observable-contract scope. The docs bundle restates the same rows in `instructions/living-spec-writing.md`
"Responsibility and design navigation"; `packages/devkit-spec/tests/integration/bundles/spec/test_formal_doc_checkpoints_guidance.py`
compares both tables row by row. `capability-writing` "What Stays Out", the capability template §3 comment,
`design-writing` item 6 and the design template datasheet comment carry rules 8 and 6 for agents.

## Reference template

`CAP-DOCS-document-model` "Document asset distribution" counts eight formal templates plus the reference page
template (no frontmatter or ID, code table `Code | Level | Condition | Fix`, new pages and new tables only). The
bundle's `templates/reference.md`, `test_distribution.py` stem set and projection check, both constitutions'
template lists and `test_ux_guidance.py` agree. `CAP-HARN-agent-guidance` §4.6 lists the eight formal templates and
names the reference template as frontmatter-free (a recorded scope extension; it had listed five).
`packages/devkit-docs/README.md` restates the count as a derived reference.

## Reconcile record coverage

`CAP-GOV-spec-rules` §3.10 and its rule-table row state the coverage check: role coverage through `related_*` IDs or
`formal_docs` reasons, the five form causes in every run, and the newly-resolved requirement in snapshot runs with
the base and, under `--staged`, `MERGE_HEAD`, `CHERRY_PICK_HEAD` and `REVERT_HEAD` as parents. Each statement was
compared with `packages/devkit-spec/src/devkit_spec/features/governance/usecases/reconcile_contract.py`
(`_formal_docs_problems`, `_coverage`, `_operation_heads`) and the rule guide §1 and §2 at the reviewed head.
`CAP-DLV-delivery-workflows` rule 9 states the frontmatter index of the body assessment, and rule 15 the reviewer's
four classes scoped to `diff_scope`, matching `spec-sync` steps 1 and 2 and `reconcile-reviewer` step 2.

`ADR-recorded-formal-docs-assessment` §4 traces replace "(planned update)" with the restating rules
(`CAP-GOV-spec-rules` §3.10, `CAP-DLV-delivery-workflows` rules 9 and 15); its decision is unchanged.

## Existing records

`uv run devkit rules check specs/` reports no `RULE-reconcile-contract` violation over the 260 existing records
(every record an explicit target, form only); none of them has `formal_docs`, so the new form causes cannot fire.

## Formal documents

No DESIGN, DOMAIN or OPS is affected; the frontmatter `formal_docs` reasons give the bounded source-based reasons,
and `PLAN-formal-doc-authoring-checkpoints` §5 the same assessment. The change introduces no persisted format: the
new frontmatter field is a record field whose contract `CAP-GOV-spec-rules` §3.10 owns. The parent order (base, then
operation heads) is internal; any parent with the record resolved exempts it, so order has no observable effect. The
new violation messages are rule output listed in the rule guide §2, the rule's reference.

## Deferred work

The deterministic code-condition rule (spec Non-Goal 2) is handed to Backlog as `FB-code-condition-rule-deferred`
with its restart condition (five ordinary specs after this one) and expected acceptance checks.

## Entrypoints

`CAP-DOCS-documentation-ownership` gains the entrypoint
`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md`, where its routing
guidance ships. Rejected candidates: the bundle and test directories, `AGENTS.md.jinja` and the README for every
capability (hub or broad shared paths), and `reconcile_contract.py` for `CAP-GOV-spec-rules`, whose existing
`packages/devkit-spec/src/devkit_spec/features/governance/` entrypoint already covers it.
