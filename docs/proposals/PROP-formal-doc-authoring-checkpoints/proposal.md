---
id: PROP-formal-doc-authoring-checkpoints
title: 'Formal documentation checkpoints: route facts, review reimplementability, record assessments'
summary: Make formal documentation get filled during ordinary delivery by adding fact-type routing, a reconcile formal-docs assessment field, reimplementability questions for the reconcile reviewer, a capability observable-contract rule and a reference template.
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/
    - packages/devkit-docs/tests/integration/bundles/docs/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/reconcile-reviewer.md
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/reconcile_contract/
    - packages/devkit-spec/src/devkit_spec/features/governance/usecases/reconcile_contract.py
    - packages/devkit-spec/tests/integration/features/governance/
    - packages/devkit-spec/tests/integration/bundles/spec/
    - packages/devkit-spec/tests/integration/features/worker/test_worker_inspect.py
    - packages/devkit-spec/tests/e2e/bundles/spec/test_formal_document_lifecycle_scenarios.py
    - docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
    - docs/capabilities/documents/CAP-DOCS-document-model.md
    - docs/capabilities/governance/CAP-GOV-spec-rules.md
    - docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    - docs/proposals/PROP-formal-doc-authoring-checkpoints/
  excludes:
    - handbook/
    - .devkit/managed/
    - docs/development/reference/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-doc-authoring-checkpoints] Formal documentation checkpoints: route facts, review reimplementability, record assessments

## 1. Background & Hypothesis

A reimplementability review of 17 capability areas found that the documentation layers are sufficient. The gaps are
content nobody wrote, not missing layers:

- on-disk byte formats and identity derivations (MCP registration entries, host hook groups, shared-artifact files,
  scope-registry tokens, the distribution journal) appear nowhere, although the DESIGN template has an optional
  "Example or datasheet" section;
- ordering and tie-break contracts (rule violation order, search ties, generated topological order) are unstated;
- reference code tables often lack a trigger condition, and their columns differ page by page;
- capability documents carry implementation pseudocode, private formats and duplicated paragraphs that belong in
  DESIGN or nowhere.

The existing guidance already asks for most of this. `spec-plan`, `spec-review` and `spec-sync` ask for a
design/domain/operations assessment, and `design-writing.md` mentions datasheets. Authors still skip it, because the
only reliably present content is what something checks:

- the reconcile record schema has `targets` only;
- `reconcile-reviewer` checks behavior, capability and constraint changes, never formal documents;
- 10 of 260 `reconcile.md` files mention a formal document, all from the 2026-11-16 formal-document specs
  ([evidence](materials/planning-evidence.md));
- routing exists per responsibility (`CAP-DOCS-documentation-ownership` §3.1 rule 5), not per fact type;
- nothing says what stays out of a capability;
- reference pages have no template.

Hypothesis: guidance that routes each fact type to its owner, plus two checkpoints that make a skipped assessment
visible, gets formal documents written during ordinary delivery without a periodic sweep. The checkpoints are a
recorded assessment and an independent reviewer question.

The formal-document steps in plan, review and sync landed on 2026-11-16, so no ordinary spec has run under them yet.
Planning should keep the change proportionate to that.


## 2. Technical Spike Questions

Each question is settled; the reasons are under Planning decisions.

- **Q1**: Where does the fact-type routing table live? **Answer**: `CAP-DOCS-documentation-ownership` §3.1 stays
  canonical and gains a fact-type table beside the responsibility table; `living-spec-writing` carries the same rows
  as its agent-facing projection without citing the capability, because the bundle ships to projects that lack it.
- **Q2**: What shape does a `formal_docs` assessment take, what checks it, and how do existing records stay valid?
  **Answer**: each of the design, domain and operations roles is covered either by affected IDs in the record's
  existing typed `related_designs`, `related_domains` or `related_operations` list, or by
  `formal_docs.<role>: "none: <reason>"`; never both. `RULE-reconcile-contract` checks the coverage and the reason
  form; `RULE-document-reference` already checks that the listed IDs exist, and `devkit rules fix` repairs them on a
  rename. Coverage is required only in a snapshot run, for a record that the commit newly resolves (no parent of the
  commit has it `resolved`); anywhere else a present `formal_docs` is checked for form and absence is accepted, so
  the 260 existing records stay valid.
- **Q3**: Which reviewer finding classes carry severity, and do they block `resolved`? **Answer**: four classes on
  what `diff_scope` adds or changes, never on older gaps: a role's recorded coverage (IDs or `none:` reason) the diff
  contradicts (P1, the existing
  contradicted no-impact class); a new persisted format, identity derivation or ordering without a statement in its
  owner (P2); a new code without a documented trigger condition (P2); new capability text that restates mechanism
  (P3). Severity changes no check: like every reconcile finding they hold the `living-spec-draft` exit until fixed,
  and P2 or P3 may be waived with a reason.
- **Q4**: What does the capability observable-contract rule say? **Answer**: a capability states what a consumer can
  observe or rely on, and leaves out implementation pseudocode, internal algorithm steps, formats only the
  implementation reads back and paragraphs another document owns. It is guidance only: a SHOULD rule in
  `CAP-DOCS-documentation-ownership`, a section in `capability-writing` and one clause in the template comment.
- **Q5**: Add a reference page template? **Answer**: yes, `templates/reference.md`, with no frontmatter or ID (reference
  pages are not formal documents) and a code table `Code | Level | Condition | Fix`, plus a reference section in
  `document-writing`. It applies to new reference pages and new code tables; a row added to an existing table states
  its condition. Existing pages are not migrated.
- **Q6**: Should the DESIGN datasheet section become required when a mechanism persists data? **Answer**: no required
  section, because no check can recognize one. `design-writing` and the template comment say that a design SHOULD carry
  a datasheet WHEN its mechanism writes data that a later run, another process or another tool reads back; the
  reviewer's P2 class applies when such data is new.
- **Q7**: Is the deterministic code-condition rule deferred? **Answer**: yes. The spec hands it to Backlog as deferred
  work, to be evaluated once the reference code table shape has landed and five ordinary specs have completed under
  the checkpoints.

## 3. Proposed Design & Impact

### Docs bundle (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`)

- `instructions/living-spec-writing.md`, "Responsibility and design navigation": add the fact-type routing table:

  | Fact type | Owner |
  | --- | --- |
  | Behavior, limit, output order or tie-break a consumer can observe | Capability |
  | That a code is raised, and when, as a guarantee | Capability rule; trigger condition, level and fix in a reference code table |
  | Command, flag, configuration key or payload field syntax | Reference; the capability lists the interface |
  | Data that a later run, another process or another tool reads back: location pattern, encoding, fields, example | Design datasheet; a format consumers author or parse is also a capability interface |
  | How an ID, key, hash, token or name is derived | Design; what the identity means belongs to the domain model |
  | Internal processing order, algorithm or pseudocode | Design, or the source alone |
  | Concept meaning, identity and lifecycle | Domain model; glossary for terms |
  | Rationale and rejected options | ADR |
  | Measurement or experiment | Materials |

- `instructions/capability-writing.md`: a section "What stays out" with the Q4 rule, routing excluded content by the
  table above.
- `templates/capability.md`: one clause in the §3 comment ("observable contract only; route mechanism by
  `living-spec-writing`").
- `instructions/design-writing.md` item 6 and `templates/design.md` datasheet comment: the Q6 condition and the
  datasheet contents (location pattern, encoding, fields or layout, identity derivation, ordering, one example).
- `templates/reference.md` (new) and a "Reference pages" section in `instructions/document-writing.md`: purpose line
  naming the owning capability, usage, configuration and the code table; Condition states the observable trigger,
  Fix the next action.
- `AGENTS.md` template list gains `reference`.

### Spec bundle (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`)

- `skills/spec-sync/SKILL.md`: step 1 records the design/domain/operations coverage in the record's frontmatter;
  step 2's schema shows it:

  ```yaml
  related_designs: [DESIGN-<slug>]   # affected IDs created, changed or retired by the change
  formal_docs:
    domain: "none: <bounded source-based reason>"
    operations: "none: <bounded source-based reason>"
  ```

  The body keeps the detailed assessment (statements, source identity, owner, action, evidence); the frontmatter is
  its index.
- `rules/reconcile_contract/guide.md` and the implementation
  (`features/governance/usecases/reconcile_contract.py`): new causes, in every run for a present value: `formal_docs`
  not a mapping; an unknown key; a value that is not a string starting `none: ` with a reason of at least 20
  non-whitespace characters; a role with both a nonempty `related_*` list and a `none:` reason. In a snapshot run,
  a `resolved` record that the diff changes and that no parent of the commit has `resolved` (the base, and in a
  staged run also `MERGE_HEAD`, `CHERRY_PICK_HEAD` or `REVERT_HEAD` when present, as
  `devkit_agt.features.generated` already detects) MUST cover every role. A merge that brings in a record resolved on
  the base branch therefore never requires the field of a record the branch did not author.
- `subagents/reconcile-reviewer.md` step 2: the four Q3 classes with their severities, scoped to `diff_scope`.
- `skills/spec-plan/SKILL.md` step 3 and `skills/spec-review/SKILL.md` step 4: one sentence each naming the persisted
  formats, identity derivations, orderings and codes the change introduces, routed by the fact-type table.
- `AGENTS.md.jinja` template list gains `reference`.

### Living Spec

- `CAP-DOCS-documentation-ownership` §3.1: the fact-type table (Q1) and an "Observable contract" SHOULD rule (Q4).
- `CAP-DOCS-document-model`: the template inventory names the reference template beside the eight formal templates.
- `CAP-GOV-spec-rules`: the `RULE-reconcile-contract` row names the role-coverage check.
- `CAP-DLV-delivery-workflows` rule 9 (the assessment is indexed in `reconcile.md` by `related_*` IDs or
  `formal_docs` reasons) and rule 15 (the reviewer's reimplementability classes).
- New ADR from `PADR-recorded-formal-docs-assessment`.

### Out of scope

- Migrating existing reference pages, capability text or formal documents; a sweep of older gaps.
- A rule that every declared code has a documented condition (Q7).
- `docs/development/reference/`: existing pages are not migrated (Q5). `.devkit/managed/` is regenerated by
  `devkit sync`, never edited.

## Planning decisions

- **Q1, canonical owner**: the capability holds the contract and the instruction is what agents read; keeping the
  capability canonical matches §3.1 rule 1, and the instruction stays self-contained because consumer projects do not
  have devkit's capability. Ordering is split by observability: an order a consumer sees is a capability rule (the
  rule violation order, search ties, a generated order consumers diff), internal order is design.
- **Q2, check owner and validity of old records**: `RULE-reconcile-contract` owns the record form; `RULE-spec-progress`
  is a warning-level progress hint on another file. Requiring coverage only for a record the commit newly resolves
  reuses the rule's snapshot comparison with the base, so no date cutoff, setting or migration is needed. A historical
  record edited by a link or path repair keeps `resolved` at its base and stays exempt; an explicitly targeted plain
  run of a completed record checks form only. All 260 existing bundles are completed, so no in-flight record is
  affected.
- **Q2, shape**: reusing the typed `related_*` fields gives the IDs existence checks, alias repair and incoming
  references in `devkit docs refs` and the viewer, which IDs inside a new field would lack; `formal_docs` then holds
  only what no existing field can, the per-role `none:` reason, and keeps the "bounded unaffected reason" model
  without requiring an empty document. The detailed assessment stays in the body, as `CAP-DLV-delivery-workflows`
  rule 9 already requires.
- **Q2, merges**: the commit gate runs when a conflicted merge is concluded, with the HEAD tree as its base; checking
  every parent keeps a record resolved on the base branch from refusing that merge.
- **Q2, relation to `ADR-formal-document-delivery-integration`**: compatible. That decision keeps the assessment in
  existing records under semantic review and rejected a separate impact manifest as a second registry. The coverage
  lives in the existing record and existing relation fields, and it only makes a skipped role visible; semantic
  agreement stays with the author and `reconcile-reviewer`.
- **Q3, severity**: the classes reuse the existing reconcile severity meanings (contradiction P1, incomplete
  reflection P2, improvement P3), so no new blocking mechanism is added; the formal-document steps are new and a P1
  for an omission would make them a hard gate before any ordinary spec has run under them.
- **Q5, template file**: a separate template keeps the shape copyable and shipped with the other templates; it costs
  three pinned lists and one count, updated in the same change.
- **Q6**: a required section would need a check that cannot tell a datasheet from prose; the reviewer class covers new
  persisted data at P2.
- **Q7**: the deferred rule depends on a uniform table shape that only new pages will have; five ordinary specs give a
  first measure of whether the reviewer class alone keeps conditions written.
- **PADR**: `PADR-recorded-formal-docs-assessment` records the record field, its check and the reviewer classes,
  because it changes an existing rule contract and spans the spec and docs bundles. The guidance changes (Q1, Q4, Q5,
  Q6) change no contract or check and stay here.
- **Concurrent work**: `PROP-handoff-rewrite-overlap-scheduling` (draft) owns `packages/devkit-spec/tests/`, which
  contains this proposal's owned test paths, including `test_worker_inspect.py` and
  `test_formal_document_lifecycle_scenarios.py`, whose fixtures resolve records in snapshot runs and gain coverage; no sequencing decision is needed while it is a draft.

## Spec boundaries, acceptance evidence and size

One spec, `sdd-spec-feature`, size M, `dev_effort: medium`. No split: the guidance, the record field and the
reviewer classes describe one fact-type model and land together; four tasks fit one spec:

1. Docs bundle guidance and templates (Q1, Q4, Q5, Q6) with the template-list pins.
2. `RULE-reconcile-contract`: role coverage, `formal_docs` form and the newly-resolved requirement, guide, tests
   and the two existing fixtures that resolve records in snapshot runs.
3. Spec bundle: `spec-sync`, `reconcile-reviewer`, `spec-plan`, `spec-review` wording.
4. Living Spec capabilities and the promoted ADR; the spec's own `reconcile.md` covers every role.

Acceptance evidence:

- Rule tests: in `--staged` and `--ci` snapshot runs, a new or newly resolved record with a role uncovered is
  reported; a record `resolved` at the base and edited, a `pending` record, a record resolved in a merge parent
  (`MERGE_HEAD`) and a plain explicitly targeted completed record without coverage are not; each malformed form (not a
  mapping, unknown key, missing `none: ` prefix, short reason, a role with both IDs and a reason) is reported; full
  coverage through `related_*` lists, `none:` reasons or a mix passes.
- `uv run devkit rules check specs/` (every record an explicit target) reports no new `RULE-reconcile-contract`
  violation over the 260 existing records, and the spec's own record passes `--ci` with every role covered.
- The template distribution and constitution tests list `reference`; `devkit sync` projects `templates/reference.md`.
- Reviewed text: `reconcile-reviewer` names the four classes with severities and the `diff_scope` limit; the
  fact-type rows in `CAP-DOCS-documentation-ownership` and `living-spec-writing` agree.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1-Q7 and the spec boundaries; acceptance hands off to Development and integrates locally under
  `dev-integration=auto`.
- Retire when the guidance and checkpoints land. After five ordinary specs complete under them, evaluate the effect
  before proposing the deferred code-condition rule.
