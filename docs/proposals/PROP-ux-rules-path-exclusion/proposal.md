---
id: PROP-ux-rules-path-exclusion
title: Path-scoped opt-out of the UX document rules
summary: "Gives RULE-ux-links and RULE-ux-coverage an exclude setting so a monorepo can switch the screen contract off for a namespace whose domain it does not fit, while the identity, reference and traceability rules keep checking the same documents."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
namespace: global
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-monorepo-namespace-support
depends_on: [SPEC-ux-coverage-explicit-exceptions]
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/
    - docs/capabilities/governance/
    - docs/capabilities/documents/CAP-DOCS-namespaces.md
  excludes:
    - .devkit/managed/
    - packages/devkit-docs/src/devkit_docs/features/governance/services/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-ux-rules-path-exclusion] Path-scoped opt-out of the UX document rules

## 1. Background & Hypothesis

`RULE-ux-links` and `RULE-ux-coverage` encode a screen contract written for web and app interfaces: `element` is
`screen`, `modal` or `panel`, and every UX document carries a `Trigger | Step | From | To | Target | Capability |
Feedback` Interactions table whose rows drive the exit and reachability checks (`CAP-GOV-spec-rules` 3.15, 3.16,
`ADR-ux-screens`). In a game package, where controls and a real-time viewport mix on one surface, the table describes
the interface worse than prose, and the rules report the mismatch as errors.

Today a project has three levers, none of which fits a namespace. `[rules] exclude` is path-scoped but switches off
every rule for the path, including `RULE-id-convention`, `RULE-document-reference` and `RULE-traceability-link`, which
the same documents should keep. `[rules.phase_overrides]` and `[rules.severity_overrides]` are per rule and global, so
one package cannot differ from another (`CAP-GOV-evaluation-lifecycle` 3 to 5). The two UX rules declare no settings.
`SPEC-ux-coverage-explicit-exceptions` (accepted 2026-11-04) covers the per-item gaps (`global:`, `off screen:`) and
leaves the contract itself in place.

Hypothesis: a rule-owned `exclude` setting, the pattern `RULE-cli-contract` already uses (workspace-relative patterns
in the `**` grammar of `[rules] exclude`), gives a monorepo a one-line, reviewable opt-out per namespace docs root
without touching the rule engine or the other rules. A relaxed element kind for viewports is a separate question that
needs a real game UX document as evidence and is out of this proposal's scope.

## 2. Technical Spike Questions

Planning settled the three questions by reading the two rules, the shared model and the settings engine; the
decision is `PADR-ux-rules-path-exclusion`.

- **Q1**: Does one setting on each rule suffice, or do the two rules share a definition? **One setting per rule, same
  key, same semantics.** The engine resolves `[rules.settings.<RULE-id>]` per rule and per file
  (`CAP-GOV-evaluation-lifecycle` 5), so a shared definition would need a new engine concept. Each rule applies
  `exclude` where it iterates the model's UX documents: `RULE-ux-links` skips an excluded document's own checks, its
  links and its flow; `RULE-ux-coverage` skips its row reports and leaves it out of the use-case listing that drives
  the step reports. The shared model in `governance.services.ux` needs no change: an excluded document stays a node of
  the flow graph (its interactions remain edges and its ID a valid Target for the documents still checked), which is
  exactly what the checked documents need.
- **Q2**: What does an excluded UX document still owe? **Everything the other rules check, and nothing of the screen
  contract.** `RULE-id-convention` (path, stem, `area`), `RULE-document-reference` (resolvable `usecases`,
  `capabilities` and body references, canonical IDs) and `RULE-document-summary` keep checking it;
  `RULE-traceability-link` covers only use case and capability links, so no rule checks the `usecases` reverse link
  of an excluded document, and a use case step citing it is not a `RULE-ux-links` finding. Its `element` may be
  absent or any value, since `ADR-ux-screens` makes `RULE-ux-links` the only reader of that field. The guides state
  this boundary; 3.15 and 3.16 restate it as MUST NOT clauses.
- **Q3**: Does the exclusion belong on the use case side as well? **No.** Both rules reach a use case only through a
  current UX document that lists it or that its steps cite: coverage reports exist only for listed use cases, and
  every link finding concerns one UX document. Excluding the namespace's UX directory therefore silences both rules
  for the namespace's use cases, while a namespace use case that a checked (global) UX document lists is still
  reported, which is the right outcome because that document claims the screen contract for it.

## 3. Proposed Design & Impact

- **Setting**: `[rules.settings.RULE-ux-links] exclude = ["docs/packages/<name>/ux/**"]` and the same key on
  `RULE-ux-coverage`; a list of workspace-relative patterns in the `**` grammar of `[rules] exclude`, default `[]`,
  validated with the engine's pattern validator so an invalid pattern is `RULES_SETTINGS_INVALID` before any rule
  runs, as for `RULE-cli-contract`. Each rule declares its own settings dataclass (`UxLinksSettings`,
  `UxCoverageSettings`) in its use case module and reads the effective value per UX document path, so
  `[[rules.settings.<RULE-id>.overrides]]` apply. `devkit rules explain` shows the setting (`[SETTING: exclude=...]`)
  with no further work.
- **Effect** (`PADR-ux-rules-path-exclusion`): a UX document the pattern matches is neither checked nor reported by
  that rule, wherever the finding would land (UX document or use case); the use cases it lists are not reported for
  it by `RULE-ux-coverage`; it stays in the catalog, in the shared model (as a flow-graph node) and in every other
  rule. The two rules are configured independently: a project may exclude a path from one and keep the other.
- **Guides**: section 4 of both rule guides becomes a settings table in the shape of `RULE-document-reference`'s,
  with the monorepo example and the boundary of Q2 and Q3; section 5 names `exclude` beside `[rules] exclude`.
- **Contracts**: `CAP-GOV-spec-rules` 3.1 (the table rows of both rules name the setting), 3.15 and 3.16 (a MUST for
  the setting and MUST NOT clauses for the excluded document, as the PADR traces them); `CAP-DOCS-namespaces` 3.4
  (the sentence on how the UX rules read a namespace gains the opt-out). `docs/development/reference/rules.md` lists
  no docs-bundle rule, so it needs no change; the `ux-writing` and `usecase-writing` instructions describe how to
  write a document and are unchanged, since the opt-out is project configuration.
- **Tests**: rule fixtures in `rules/ux_links/tests/` and `rules/ux_coverage/tests/` with an excluded namespace UX
  directory (no finding of either rule; a broken reference in the same file still reported by
  `RULE-document-reference`, shown in a test of that fixture under the existing document-reference tests or by
  loading both rules), a non-excluded sibling still checked, a use case listed by both an excluded and a checked
  document still reported, an excluded document still serving as a Target and a graph node for a checked one, and an
  invalid pattern failing the run before evaluation.

Expected affected contracts: `CAP-GOV-spec-rules` (3.1 table, 3.15, 3.16) and `CAP-DOCS-namespaces` (3.4). The rule
engine, `[rules] exclude` semantics and the shared UX model are unchanged. The prerequisite
`SPEC-ux-coverage-explicit-exceptions` is completed and integrated, so the rule modules and guides are at their
final shape.

### Planning decisions

- The settings predicate (resolve the effective settings for the document path, match each pattern) is written in
  each rule's use case module, as `RULE-cli-contract` and `RULE-document-reference` write theirs; a shared helper
  would belong to `governance.services`, which this proposal does not touch.
- `dev_effort` is raised from `low` to `medium`: the change edits an accepted contract in two capability documents
  and two rules, so one `code-reviewer` pass is the default thoroughness.
- Owned paths gain `docs/capabilities/documents/CAP-DOCS-namespaces.md` for the one sentence of 3.4.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the fixtures above and a
monorepo example in the guides.

Non-goals: a relaxed or new `element` kind (a follow-up with game evidence); localized use case or UX headings;
disabling the identity, reference or traceability rules for a namespace; per-namespace phase or severity overrides in
the rule engine.
