---
reconcile_id: REC-historical-handed-off-references
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
---

# Historical handed-off references reconciliation

`CAP-GOV-spec-rules` section 3.3 (`RULE-document-reference`) now states that in historical files a handed-off
`PROP-<slug>`, in prose or in a unit `depends_on`, was valid when written and resolves silently through its one spec,
while a `PROP-<slug>` with no matching spec is reported there as in current documents. Section 3.2 (History) already
states that history is checked only when targeted and never rewritten; it is unchanged. The bundled rule guide
(`packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md`) says the same under
"Completed specs" and restricts the fixable "was handed off" cause to current documents; its deployed copy and
`.devkit/installation.json` are sync output.

No other Living Spec document changes. `CAP-DOCS-document-model` states the canonical mapping and which files are
historical, not how a handed-off proposal resolves, so it stays true. `UC-keep-the-living-spec-consistent` already
guarantees that no fix rewrites a historical file. `UC-plan-and-hand-off-a-proposal` describes the handoff rewrite of
live references, which is unchanged. No architecture document, glossary term, ADR or development reference states
this behavior.

## Verification

Before/after on the head with the fix disabled: at the Red commit the new regression test failed with three
unfixable "no document has the ID PROP-x" violations (`red-01`), and `uv run devkit rules check
specs/2026-10/20261030-integration-merge-moved-target` reported `errors=2`; after the fix both pass, the command
reporting `errors=0` (`green-01`). `just test-affected` passed (partial selection, 2077 passed); `just lint` and
`just check` for `devkit-docs` passed; `uv run devkit rules check` and `devkit sync --check` are clean.

Entrypoint derivation proposed `.devkit/installation.json`, the rule guide and the rule test for
`CAP-GOV-spec-rules`; none is applied: they are a receipt, documentation and a test, not doorways, and the existing
entrypoint `packages/devkit-docs/src/devkit_docs/features/governance/` already covers the changed use case.

## Deferred work

None. The stale ADR/PADR alias clause of the same rule guide is already captured as
`FB-document-reference-guide-adr-rewrite-stale` and is outside this unit's agreed scope.
