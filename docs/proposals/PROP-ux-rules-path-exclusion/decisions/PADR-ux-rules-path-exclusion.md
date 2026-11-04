---
id: PADR-ux-rules-path-exclusion
title: Rule-owned path exclusion for the UX document rules
summary: For a namespace the screen contract does not fit, we give RULE-ux-links and RULE-ux-coverage a rule-owned exclude setting rather than an engine override or a relaxed element kind, to keep the other rules on the same documents, accepting unchecked elements and tables there.
proposal: PROP-ux-rules-path-exclusion
# supersedes: [ADR-<slug>]   # an ADR this decision replaces, wholly or in part; name the replaced clauses in Decision Outcome
status: draft
created_at: 2026-11-04
---

# [PADR-ux-rules-path-exclusion] Rule-owned path exclusion for the UX document rules

- **Status**: Draft
- **Date**: 2026-11-04

---

## 1. Context & Problem Statement

`RULE-ux-links` and `RULE-ux-coverage` check every current UX document against the screen contract of
`ADR-ux-screens`: `element` is `screen`, `modal` or `panel`, and an Interactions table with the columns
`Trigger | Step | From | To | Target | Capability | Feedback` links each row to a use case step
(`CAP-GOV-spec-rules` 3.15, 3.16). A monorepo may register a namespace (`CAP-DOCS-namespaces`) whose interfaces the
contract describes worse than prose, such as a game package where controls and a real-time viewport share one
surface; there the rules report the mismatch as errors on every UX document.

The levers a project has today do not fit a namespace. `[rules] exclude` removes a path from every rule, so the
namespace's UX documents would also lose `RULE-id-convention`, `RULE-document-reference` and `RULE-document-summary`.
`[rules.phase_overrides]` and `[rules.severity_overrides]` are per rule and repository-wide, so one namespace cannot
differ from another (`CAP-GOV-evaluation-lifecycle` 4, 5). The two UX rules declare no settings.
`SPEC-ux-coverage-explicit-exceptions` classifies single gaps (`global:`, `off screen:`) and keeps the contract.

## 2. Decision Drivers

- The identity, reference and summary rules keep checking the namespace's UX documents unchanged
  (`MS-monorepo-namespace-support` non-goals).
- One reviewable line of project configuration per namespace, visible in `devkit rules explain`.
- No change to the rule engine, to `[rules] exclude` semantics or to the shared UX model in
  `governance.services.ux`.
- The pattern already exists for a devkit rule, so authors and projects learn nothing new.
- A domain-specific screen contract is a separate decision that needs evidence from a real document.

## 3. Considered Options

- **A rule-owned `exclude` setting on each UX rule** (selected): `[rules.settings.RULE-ux-links] exclude = [...]`
  and the same key on `RULE-ux-coverage`, workspace-relative patterns in the `**` grammar of `[rules] exclude`, as
  `RULE-cli-contract` and the `quick_references` setting of `RULE-document-reference` already take. The engine
  validates and resolves it per path; each rule skips the UX documents it matches. Cost: two settings to keep in step,
  and an excluded document's `element` and table go unchecked.
- **`[rules] exclude` on the namespace UX directory** (rejected): no code, but it switches every rule off for the
  path, including the identity and reference rules the documents should keep.
- **Per-namespace phase or severity overrides in the engine** (rejected): a new override dimension in
  `CAP-GOV-evaluation-lifecycle` for every rule, to serve two; lowering the two UX rules to warnings also keeps
  reporting a contract the namespace does not follow.
- **A relaxed or new `element` kind for mixed surfaces** (rejected for now): changes the screen contract of
  `ADR-ux-screens` for every project on the evidence of a hypothesis; it stays a follow-up once a real document of
  such a namespace exists.
- **Keep the current state** (rejected): a namespace either writes documents that fit the contract badly or carries
  permanent errors.

## 4. Decision Outcome

Rule-owned path exclusion, one setting per rule, applied where each rule selects its documents.

- `RULE-ux-links` and `RULE-ux-coverage` each declare the setting `exclude`, a list of workspace-relative path
  patterns in the `**` grammar of `[rules] exclude`, default `[]`; an invalid pattern fails the run with
  `RULES_SETTINGS_INVALID`, and `devkit rules explain` shows the effective value. → `CAP-GOV-spec-rules` 3.15, 3.16
  (MUST)
- A UX document whose path a rule's `exclude` matches (resolved per file, so path overrides apply) is neither
  checked nor reported by that rule, in whichever document the finding would land. It stays in the document catalog,
  in the shared UX model and in every other rule. → `CAP-GOV-spec-rules` 3.15, 3.16 (MUST NOT)
- `RULE-ux-coverage` does not report, for an excluded UX document, the steps of the use cases it lists; a use case
  that only excluded UX documents list is not reported, and one that a checked UX document also lists is reported as
  before. → `CAP-GOV-spec-rules` 3.16 (MUST NOT)
- `RULE-ux-links` reads an excluded UX document as a node of the flow graph: its interactions remain edges and its ID
  remains a valid Target for the documents it still checks. → `CAP-GOV-spec-rules` 3.15 (MUST)
- The setting names UX documents only: a use case is excluded with the UX documents that list it, and a use case no
  current UX document lists is never reported by either rule. No use-case-side setting exists.
- The shared model `governance.services.ux` and the engine's `[rules] exclude` semantics are unchanged.

## 5. Consequences

- Positive: a namespace opts out of the screen contract with one configuration line per rule, keeps its UX documents
  in the catalog and under the identity, reference and summary rules, and the opt-out is visible in
  `devkit rules explain`.
- Negative: an excluded UX document's `element`, Interactions table and step links are checked by nothing, so a
  namespace that excludes its UX directory owns that contract itself. Two rules carry the same key: a project that
  excludes a path from one rule and not the other gets contradictions without coverage hints, or hints without
  contradictions, which the guides state as intended.
- Risk: the first project with a mixed-surface namespace documents it in prose where a table would have served.
  Follow-up: a relaxed `element` kind becomes a proposal once a real UX document of such a namespace exists as
  evidence.

## 6. Confirmation

`RULE-ux-links` and `RULE-ux-coverage` rule tests (`rules/ux_links/tests/`, `rules/ux_coverage/tests/`): an excluded
namespace UX directory produces no finding of either rule while `RULE-document-reference` still reports a broken
reference in the same file; a non-excluded sibling is still checked; an invalid pattern fails before evaluation.
`CAP-GOV-spec-rules` 3.15 and 3.16 restate the clauses above.
