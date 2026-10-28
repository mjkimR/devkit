---
id: PROP-document-bundle-split
title: Install the document system without SDD
summary: "Ships document formats, authoring guidance, templates and document rules in a docs bundle, independently of the spec bundle's SDD lifecycle assets."
status: accepted
created_at: 2026-10-28
target_area: packages/devkit-docs/
priority: medium
size: M
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
boundaries:
  owns:
    - packages/devkit-docs/
    - packages/devkit-spec/
    - guides/
    - docs/capabilities/documents/
    - docs/capabilities/delivery/
    - docs/capabilities/governance/
    - docs/architecture/
    - docs/decisions/
    - docs/steering/glossary.md
    - .devkit/config.toml
    - .devkit/installation.json
    - AGENTS.md
    - pyproject.toml
    - uv.lock
    - scripts/affected_tests.py
  excludes:
    - packages/devkit-dist/src/
    - packages/devkit/src/
task_kind: feature
decomposed_from: PROP-document-layer-package
workflow: sdd-proposal
---

# [PROP-document-bundle-split] Install the document system without SDD

## 1. Background & Hypothesis

`ADR-document-package` separated the document implementation into devkit-docs. The `spec` bundle still owns all
its deployable instructions, rules, templates and skeletons. Installing devkit-docs alone therefore supplies
commands without the corresponding agent guidance and rule assets.

A document-only bundle lets another development approach use the existing formats without installing SDD entry
instructions. This is the distribution prerequisite of `MS-idea-incubation`, not its complete incubation path.
The preceding package refactor is integrated at `26a3c494`; it is not an unresolved prerequisite.

## 2. Technical Spike Questions

- **Q1 — distribution boundary**: recommend two bundles, `docs` in devkit-docs and `spec` in devkit-spec, rather
  than document/lifecycle presets in one wheel. See `PADR-document-and-sdd-bundles` and
  `materials/distribution-evidence.md`.
- **Q2 — clean guidance**: move document guidance and rewrite mixed passages, rule `related` identifiers,
  templates and seeded READMEs by meaning. Preserve SDD-only obligations in the spec constitution and skills.
  A document-only installation must contain no instruction to invoke `/spec`, create a Unit, traverse workflows,
  record approval/envelopes or preserve completed delivery artifacts.

## 3. Proposed Design & Impact

### Bundle selection and ownership

1. `devkit-docs` registers `docs = "devkit_docs.bundles.docs"` in `devkit.bundles`. Its `core` default is
   `auto_select = true`, matching the existing package-installation model. devkit-spec keeps its auto-selected
   `spec:core`. Installing devkit-spec installs devkit-docs and therefore deploys both by default.
2. `docs:core` owns the eight document authoring instructions, the nine document rule assets, shared document
   templates, a document-only constitution and a `docs-pointer` guidance fragment. It alone declares
   `context_documents = "docs/steering"`; spec removes that declaration. The pointer requires `get-context docs`
   before document work, not before every code edit.
3. `spec:core` owns lifecycle rules (`task-coverage`, `spec-lifecycle`, `spec-progress`, `reconcile-contract`,
   `proposal-boundaries`), lifecycle templates, all existing stage skills, playbooks, workflows and subagents,
   and the SDD constitution/pointer. Its constitution requires `get-context docs` once before using document
   contracts, so SDD retains those constraints without duplicating document instruction ownership.
4. The shared template set is capability, usecase, ux, decision and milestone. The proposal template remains
   in spec; these are the six existing packaged templates, not a new template family.
   No template has two bundle owners. SDD references use `.devkit/managed/docs/templates/` for shared formats
   and `.devkit/managed/spec/templates/` for lifecycle records.
5. Move `docs-skeleton` to `docs:docs-skeleton`, remaining opt-in. Split seeded guidance so it describes document
   authoring without requiring SDD. Seeded files remain project-owned: sync neither rewrites nor deletes existing
   seeded docs. Lifecycle directories can be created by lifecycle commands when needed; document-only skeletons
   contain no SDD routing or lifecycle instructions.
6. No bundle dependency resolver is introduced. The supported SDD selection is docs+spec; guides show restoring
   docs with `uv run devkit add docs` if explicitly removed. A package containing both may select document-only
   assets with `uv run devkit remove spec`, but installed devkit-spec command extensions remain installed. A
   clean document-only consumer installs devkit-docs without devkit-spec and is the isolation acceptance case.

### Rule inventory

| Owner | Existing rule assets | Judgment after the split |
| --- | --- | --- |
| docs | document-reference, id-convention, spec-format, traceability-link, document-summary, steering-documents, ux-links, ux-coverage, code-entrypoints | Unchanged document identity, format, reference, relationship and path checks. |
| spec | task-coverage, spec-lifecycle, spec-progress, reconcile-contract, proposal-boundaries | Unchanged delivery coverage, progress, completion, reconciliation and proposal checks. |

The rule IDs keep their existing `RULE-` names, including `RULE-spec-format`: that rule checks document formats
and does not make the SDD lifecycle mandatory. Rejected-proposal and milestone hygiene are runtime spec
extensions, not docs bundle assets. They are absent from the clean docs-only environment because devkit-spec
is not installed; removing selected spec assets alone does not disable those installed extensions.

### Separation of authoring and lifecycle policy

The docs constitution retains document identity, frontmatter, full-ID references, applicable structure, summaries,
namespace and steering lookup, authoring instructions and current-state documentation. It does not impose SDD
approval, immutable ADR history, completed-spec preservation or change-by-change reconciliation.

Move those lifecycle obligations out of mixed instructions into the spec constitution or relevant lifecycle
instructions. In particular, decision-writing and living-spec-writing distinguish a decision's format from
SDD's policy for superseding accepted decisions. The generic docs guidance allows the selected development
approach to decide revision and retention. Existing SDD consumers retain the original obligations through spec.
Rule behavior, document kind vocabulary, statuses and command names stay as established by `ADR-document-package`.

### Validation scenarios

- **AC-01 — document-only installation**: Given an isolated consumer environment with devkit-docs and its
  dependencies but no devkit-spec distribution, when sync and `get-context docs` run, then docs core assets,
  its steering listing and pointer are installed, the nine document rules load, `devkit docs list|resolve|refs|search`
  remain available (lexical search requires no optional embedding runtime), and no spec asset, `/spec` skill,
  SDD workflow, SDD subagent or spec pointer is installed. Assert installed distributions and receipt ownership.
- **AC-02 — existing SDD selection**: Given devkit-spec and default core selections, when sync runs, then docs
  and spec core install together without duplicate asset or projection ownership. Shared formats and lifecycle
  workflows resolve all their template/instruction references. Original SDD gates, ADR retention and completed
  artifact preservation remain explicit in spec guidance. Existing proposal and lifecycle tests pass.
- **AC-03 — steering and citations**: Given each selection, when contexts and rule explanations are read, then
  steering documents are listed by docs exactly once and rule `related` references resolve to installed owning
  instructions. All shipped and projected references to moved assets point at docs; inventory assertions guard
  known lifecycle markers and review verifies semantics of neutral instructions/templates/seeded READMEs.
- **AC-04 — optional skeleton**: Given docs core alone, when sync runs, then no skeleton is seeded. When the user
  adds `docs:docs-skeleton`, absent document skeleton files are seeded with document-only guidance. A pre-existing
  seeded file keeps its bytes through reselection and sync. No old preset alias or migration reader is added.
- **AC-05 — explicit selection**: Given both packages and defaults, when the user removes spec, then spec's
  managed/projected assets and pointer are removed and docs remains usable. The guides explicitly distinguish
  selected assets from installed command extensions. Re-adding spec restores SDD guidance; no project setting
  or runtime policy bypass is inferred from asset removal.
- **AC-06 — packaging and repository**: Built wheels contain the assets they own and discover the correct
  bundle entrypoints. This repository selects both core bundles, syncs its tracked outputs and passes
  `devkit sync --check`, affected tests, lint, type checks and the cumulative governance check.

### Scope exclusions and dependent work

- **Scope Excluded**: incubation entry skills, product clarification/research/usage-verification roles and
  resumable incubation context. Those depend on the document-only foundation.
- **Scope Excluded**: a development-approach setting, SDD command precondition changes, integration-readiness
  behavior and lifecycle rule bypasses. Asset selection alone does not solve runtime lifecycle policy.
- **Scope Excluded**: optional verified transition from an implemented product to SDD, reconstructed history,
  a new application framework, changes to generic distribution selection semantics and compatibility shims.
- **Scope Excluded**: rewriting project-owned seeded documents in consumer repositories automatically.

The Host retains milestone follow-up decomposition and tracking; no omitted milestone exit criterion is claimed
complete by this proposal. `target-docs.md` identifies the Living Spec reflection and documentation repairs.

### Planning review

The medium-effort Challenger inspected wheel ownership, manifest selection, explicit opt-outs, document rule
implementations, instructions and seeds at `9492bd01`. It returned no material findings. No open design question
requires a separate worker answer; the proposed direction remains subject to Host/user `plan-accept`.
Consumer installation and semantic text verification remain Development evidence.

## 4. Lifecycle & Retirement Criteria

Accept the direction and hand off one feature spec after the Host validates this Planning result. Retire the
proposal at handoff. Development completes only when AC-01 through AC-06 and the document-only consumer smoke
pass. The proposed direction requires `plan-accept`; this worker records no acceptance or handoff authority.
