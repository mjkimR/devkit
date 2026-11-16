---
id: PLAN-formal-document-templates
spec: SPEC-formal-document-templates
---

# Technical Plan: `SPEC-formal-document-templates` Template alignment for formal design, domain and operations documents

## 1. Constitution & Invariant Review

- `ADR-problem-first-formal-document-openings` (accepted at handoff) changes the authoring rule; this plan
  implements its Decision Outcome and Confirmation. No further ADR is needed.
- `CAP-DOCS-documentation-ownership` §3.3 item 2 is a SHOULD that the ADR rewords; the change lands with the ADR's
  restatement trace. §4 and `CAP-DOCS-document-model` (§3.2 template count, "Document asset distribution") change
  only in the template inventory.
- `ADR-linked-domain-relationship-views` already carries the "Superseded in part" pointer (handoff commit); its
  `§3.4` traces stay as history.
- `ADR-formal-role-document-identities` and `ADR-area-scoped-design-bundles` own paths, identity and frontmatter
  schema; templates keep the same fields, only their presentation changes (comments, quoting).
- Bundle self-containment (`agent-asset-writing`): templates and instructions cite no repository document ID.

## 2. Architecture Overview & Impact

- Target area: the docs core bundle (`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/`), its tests and
  the Living Spec documents of kinds design, domain and operations. No Python source changes; no new dependency or
  feature edge.
- Managed projection: `devkit sync` rewrites `.devkit/managed/docs/templates/*` and
  `.devkit/managed/docs/instructions/*` and updates `.devkit/installation.json`; removing `design-template.md`
  removes its managed copy and receipt entries.

## 3. Component & Interface Design

### Templates (AC-01, AC-02)

Shared shape for `design.md`, `domain.md`, `operations.md`:

```markdown
---
id: <PREFIX>-<slug>
title: "<Title>"
status: draft  # draft | active | retired
summary: "<English sentence stating the subject and boundary.>"
area: <area>   # design and domain only
# related_capabilities: [CAP-<AREA>-<slug>]   # optional typed links; list only useful IDs
# ...
---

# [<PREFIX>-<slug>] <Title>

<!-- per-kind problem prompt (one or two lines) -->

<kind body headings, each with a one/two-line comment; tables as placeholder rows>

## Authority boundary
<!-- what this document does not settle and the owner that does, by full ID -->

## Maintenance and next action
<!-- the change that requires an update and the next useful reader action -->
```

| Kind | Body | Table skeleton |
| --- | --- | --- |
| design | `## <Mechanism topic>`, `## <Example or datasheet topic>` placeholders | none |
| domain | `## Relationship overview` (+ optional worked example comment) | `Concept or relationship \| Distinction \| Authoritative owner` |
| operations | `## Routing`, `## Normal-state observation` | `Symptom or state \| Discriminating evidence \| Next useful owner` |

Placeholders stay compatible with the e2e substitutions (`<slug>`, `<area>`, `<Title>`, summary sentence).

### Instructions (AC-03)

Each of `design-writing.md`, `domain-writing.md`, `operations-writing.md` gains: a scoping step after step 1, an
opening/body/closing step matching its template (replacing the current step 4 wording), a kind-specific addition
(operations: normal-state observation; domain: distinguishing example and glossary pointer) and a final step to
delete HTML comments before `devkit rules check`. Existing identity, relation, support and entrypoint steps stay.

### Capability, model and README (AC-04, AC-06)

- `CAP-DOCS-documentation-ownership` §3.3 item 2 reworded per the ADR; §4 drops the compatibility pointer sentence.
- `CAP-DOCS-document-model`: "three formal role files and the legacy design-template compatibility pointer, for nine
  total files" becomes eight total files; "eight formal templates plus the design-template compatibility pointer"
  drops the pointer.
- `packages/devkit-docs/README.md`: "nine templates including the design-template compatibility pointer" becomes
  "eight templates".

### Delivered documents (AC-05)

Reorganize per the Planning decision table (spec §7): label or `## Question` removed; lead paragraph states the
problem; design topic headings kept; authority prose moved under `## Authority boundary`; maintenance sections
renamed `## Maintenance and next action`; domain tables re-columned to `Concept or relationship | Distinction |
Authoritative owner`; `OPS-distribution-sync` table under `## Routing` with the skeleton columns. Every full ID and
link is kept; verification compares the sorted ID/link sets before and after.

Design impact: the two DESIGN documents change form only; their mechanism statements, source links and entrypoints
are unchanged. Domain and operations impact: same, form only. Statement owner remains as before.

### Tests (AC-02, AC-06, AC-07)

- `test_distribution.py`: drop `design-template` from the stem set and the managed-copy byte comparison (use
  `design.md` instead, still asserting it starts with frontmatter as a formal template).
- `test_installed_consumer.py`: cut the instantiated template after the H1 line `# [<PREFIX>-sample] Sample`,
  asserting the cut point and that no `<slug>`/`<area>`/`<Title>` placeholder remains in the kept part.

## 4. Error Handling & Edge Cases

- A leftover HTML comment in an authored document is invisible in rendered output but visible to agents; the
  instructions require deleting comments, and no rule checks it (Non-Goal 2).
- YAML comments in frontmatter must not break parsing: `status: draft  # ...` and commented `related_*` lines parse
  as `status: draft` and absent fields; the e2e consumer and `devkit rules check` prove it.

## 6. Verification & Test Plan

- `uv run pytest packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` (AC-02, AC-06).
- `uv run pytest packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py` (AC-07, builds wheels).
- `uv run devkit rules check --phase hygiene` on the three instructions (AC-03).
- `rg` checks named in AC-05 and AC-06; `uv run devkit rules check --ci --base main`; `uv run devkit sync --check`.
- Lint, pyright and `just test-affected --base 93e72152c` per the repository policy.
