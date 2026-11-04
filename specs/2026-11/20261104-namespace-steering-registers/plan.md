---
id: PLAN-namespace-steering-registers
spec: SPEC-namespace-steering-registers
---

# Technical Plan: `SPEC-namespace-steering-registers`

## 1. Constitution & Invariant Review

`ARCH-05-2-components` layering and existing feature dependencies remain unchanged. A new
ADR-namespace-steering-registers partially supersedes the glossary exclusions and deferred-register clauses of
`ADR-namespace-steering-directories`. Document identity and reference resolution remain global.

## 2. Architecture Overview & Impact

The documents feature owns search expansion and selected namespaces. Governance owns steering and reference
validation. Docs and spec bundles own the agent's glossary/UX register choices. No new package or feature edge.

## 3. Component & Interface Design

Search receives explicit glossary paths derived from its existing NamespaceScope. Paths are root followed by the
selected registered namespace or all registered namespaces sorted by name. Existing load_glossary(root) retains
root-only behavior for callers that pass no paths; the search use case supplies the paths. Synonym clusters union
in file order, preserving tokenizer collision behavior. An invalid file overrides the advisory target and fix.
Steering validation applies one contract to root and registered namespace files. A targeted legacy glossary is a
migration finding; no fallback or automatic move creates two canonical locations. Reference validation recognizes
Owner cells in all registered canonical glossaries and deduplicates by path, line and ID.

## 4. Storage & State Management

No persisted schema changes. Namespace glossary and UX register files are optional and project-authored.
Existing namespace glossaries move explicitly into steering with title and English summary frontmatter; guide
users to merge if both locations exist. Root glossary stays in place.

## 5. Error Handling & Edge Cases

Missing glossary files are empty; invalid selected YAML raises DOCS_GLOSSARY_INVALID for that exact file.
Unselected/unregistered YAML is never loaded. Global mode excludes local synonyms. Context selection remains its
existing root-plus-current-namespace behavior. UX object semantics remain a review concern, not a new rule.

## 6. Verification & Test Plan

Focused documents search/namespace tests, deployed steering/reference rule tests after sync, and docs/spec guidance
tests cover AC-01–AC-06. Capture RED before source changes, GREEN afterward. Run lint-check and Pyright for
both affected wheels, just test-affected --base 4c6298983f5febeca7cfee8d27bc4708688551c7 with full fallback,
sync --check, cumulative CI rules against 700c339bba8e89b4d70f63c5628d14d25bd3ffdd, and wheel builds offline.
Independent medium code and reconcile reviews verify the final diff and all reflected targets.

## Host-authorized reflection boundary

The Host added `docs/decisions/2026-11/20261102-ux-screens.md` to initial Tier A scope for a partial-supersession
annotation and link repair only. Its historical decision text remains intact. The new ADR precisely supersedes the
root-only object-register location, unconditional creation and root-only sync-write clauses; all other UX decisions
remain. This is an initial grant, not an adjacent Development extension.
