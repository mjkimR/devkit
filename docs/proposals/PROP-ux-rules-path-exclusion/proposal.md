---
id: PROP-ux-rules-path-exclusion
title: Path-scoped opt-out of the UX document rules
summary: "Gives RULE-ux-links and RULE-ux-coverage an exclude setting so a monorepo can switch the screen contract off for a namespace whose domain it does not fit, while the identity, reference and traceability rules keep checking the same documents."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-04
target_area: governance/
namespace: global
priority: medium                      # critical | high | medium | low
size: S                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: low                       # low | medium | high (hint for Development)
milestone: MS-monorepo-namespace-support
depends_on: [PROP-ux-coverage-explicit-exceptions]
boundaries:
  owns:
    - packages/devkit-docs/src/devkit_docs/features/governance/usecases/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_links/
    - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/ux_coverage/
    - docs/capabilities/governance/
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
`PROP-ux-coverage-explicit-exceptions` (accepted 2026-11-04) covers the per-item gaps (`global:`, `off screen:`) and
leaves the contract itself in place.

Hypothesis: a rule-owned `exclude` setting, the pattern `RULE-cli-contract` already uses (workspace-relative patterns
in the `**` grammar of `[rules] exclude`), gives a monorepo a one-line, reviewable opt-out per namespace docs root
without touching the rule engine or the other rules. A relaxed element kind for viewports is a separate question that
needs a real game UX document as evidence and is out of this proposal's scope.

## 2. Technical Spike Questions

- **Q1**: Does one setting on each rule suffice, or do the two rules share a definition? `RULE-ux-coverage` reads use
  cases a UX document lists, so an excluded UX document must also stop producing coverage reports on the use cases it
  lists; Planning confirms the shared model in `governance.services.ux` needs no change (that directory is excluded
  from this proposal's scope; the setting is applied where the rules select their documents).
- **Q2**: What does an excluded UX document still owe? The expected answer: everything the other rules check
  (`id`, `area`, `summary`, resolvable `usecases` and `capabilities`, reverse links). A use case citing an excluded UX
  document is not a `RULE-ux-links` contradiction; Planning writes the precise boundary into 3.15 and 3.16.
- **Q3**: Does the exclusion belong on the use case side as well (a use case directory of a namespace whose steps cite
  no screens), or is excluding the namespace UX directory enough because coverage is reported only for use cases a
  listed UX document names?

## 3. Proposed Design & Impact

- **Setting**: `[rules.settings.RULE-ux-links] exclude = ["docs/packages/<name>/ux/**"]` and the same key on
  `RULE-ux-coverage`; default `[]`; an invalid pattern is `RULES_SETTINGS_INVALID`, as for `RULE-cli-contract`. A
  matching UX document is neither checked nor reported by that rule, and the use cases it lists are not reported for
  it by `RULE-ux-coverage`; it stays in the catalog and in every other rule. `devkit rules explain` shows the setting
  (`[SETTING: exclude=...]`).
- **Guides**: both rule guides gain a settings section with the monorepo example; `CAP-GOV-spec-rules` 3.15 and 3.16
  and its rule table name the setting.
- **Tests**: rule fixtures with an excluded namespace UX directory (no `RULE-ux-links` or `RULE-ux-coverage` finding,
  the other rules still reporting a broken reference in the same file), a non-excluded sibling still checked, and an
  invalid pattern failing the run before evaluation.

Expected affected contracts: `CAP-GOV-spec-rules` (3.1 table, 3.15, 3.16). The rule engine, `[rules] exclude`
semantics and the shared UX model are unchanged. The prerequisite `PROP-ux-coverage-explicit-exceptions` edits the same
rule modules and guides; this draft starts after its handoff spec is integrated.

## 4. Lifecycle & Retirement Criteria

Planning settles Q1 to Q3; acceptance and handoff create one feature spec. Completion requires the fixtures above and a
monorepo example in the guides.

Non-goals: a relaxed or new `element` kind (a follow-up with game evidence); localized use case or UX headings;
disabling the identity, reference or traceability rules for a namespace; per-namespace phase or severity overrides in
the rule engine.
