---
reconcile_id: REC-advisory-unique-code
feature: SPEC-advisory-unique-code
status: resolved
targets:
  - file: docs/capabilities/advisory/CAP-ADV-agent-advisory-protocol.md
    resolution: modified
---

# Reconcile: `SPEC-advisory-unique-code`

`CAP-ADV-agent-advisory-protocol` §10 (Authoring Checklist, "Headline") names `RULE-advisory-unique-code` as the Python
enforcement of "`code` uniquely identifies the condition". The protocol itself does not change: principle 4 already
requires stable codes that name one condition, and the rule checks it for Python implementations.

The rule's behavior (what is analyzed, the covering condition, settings) is canonical in its guide
(`packages/devkit/src/devkit/advisory_guide/bundle/rules/unique_code/guide.md`), as for every bundle rule
(`CAP-GOV-rule-authoring` §1, Optional `guide`); the reference catalogs (`docs/development/reference/advisory.md`,
`rules.md`, `distribution.md`) and `guides/install/bundle-recommendations.md` point to it.

No other Living Spec document changes:

- `CAP-GOV-rule-authoring` and `CAP-GOV-rules-engine`: the rule uses the existing plugin-package contract and public
  API unchanged; the rules engine is not modified.
- `docs/architecture/`: no document describes the `advisory_guide` layering allowance; it is stated in `AGENTS.md`
  and enforced by `packages/devkit/tests/test_layering.py`, both updated.
- No story covers rule catalogs; no ADR is required (no `MUST` changes).

Entrypoints: none written. The derived candidates for `CAP-ADV-agent-advisory-protocol` (configuration, agent guide,
the bundle's files and the layering test) are not the code that implements the protocol, which is the runtime
`devkit.advisory`; the capability was touched only for one checklist sentence.
