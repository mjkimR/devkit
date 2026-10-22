---
reconcile_id: REC-document-id-aliases-and-compaction
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    resolution: modified
  - file: docs/capabilities/search/CAP-SRCH-document-search.md
    resolution: modified
  - file: docs/architecture/ARCH-08-2-resource-taxonomy.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconciliation

`ADR-document-id-aliases` is reflected in `CAP-DOCS-document-model` (section 3.5: field, shape, identity-not-reference,
canonical mapping with declared-ID precedence and collisions, rename procedure; index resolution, reference queries,
frontmatter table, `SPEC_ID_DUPLICATE` for a colliding alias and the library API), `CAP-DOCS-document-lookup`
(`resolve` `alias=` sentinel field and JSON `alias`, `refs` grouping and alias-written incoming references),
`CAP-DOCS-document-search` (exact alias pinning) and `CAP-GOV-spec-rules` (`RULE-document-reference` alias fix,
decision-record and history exemption, self-mention, identity checks, glossary Owner report, canonical handed-off
target, alias-aware traceability). The bundled `living-spec-writing` instruction and the rule guide state the rename
procedure and the new findings.

`CAP-DLV-proposal-incubation` states alias carriage (`PROP-` to `SPEC-` on `spec.md`, `PADR-` to `ADR-` on promoted
ADRs), the handoff rewrite of alias-written references, the alias-aware projection, the clash refusals
(`SPEC_PROPOSAL_TARGET_EXISTS`, `SPEC_PROPOSAL_SLUG_CONFLICT`), the refusal of a proposal alias whose `SPEC-`
translation is date-based (`SPEC_PROPOSAL_INVALID`, found in review) and the `new`/`padr` alias checks
(`SPEC_PROPOSAL_EXISTS`).

`ADR-playbook-aliases-as-identifiers` is reflected in `CAP-DIST-context-and-playbooks` (header grammar and bundle
uniqueness, search over `name` and `description` only, alias resolution order in `playbook get`, the `alias` result
field, `PLAYBOOK_ALIAS_AMBIGUOUS` in the error table, and alias invocation as explicit invocation), the distribution
reference, `ARCH-08-2-resource-taxonomy` and the `CAP-SRCH-document-search` metadata example. `playbook get` is
JSON-only, so the alias is carried by the `alias` JSON field; there is no text sentinel.

No file under `docs/decisions/` changed. No story is affected. The carried planning feedback
(`FB-answer-correction-unrecorded`, `FB-padr-withdrawal-unspecified`) concerns the spec skill's Planning references,
outside this unit's write scope and not direct-fix sources of this spec; it stays open for a hygiene session. No
deferred work remains in the agreed scope.

Entrypoint derivation was reviewed (`spec-entrypoints`): candidates are the broad package directories of this
bundle's task boundaries, which span several capabilities; the touched capabilities already declare their doorway
modules or were edited for contract wording, so no entrypoint was applied.

Reconcile verification (`reconcile-check-01`) found contracts outside this record that name changed behavior.
In scope, `CAP-DOCS-document-model` section 3.5 rule 6 now states the cross-contract rule: an alias declaration
counts wherever a contract refuses or reports a declared ID (so `CAP-DLV-spec-bundles` "any document declares" covers
`devkit spec new` refusing a slug taken by an alias), and ID arguments resolved through the index accept an alias (so
`CAP-TRACE-code-entrypoints` `--target` stays correct). `CAP-DLV-proposal-incubation` states that `--milestone`
accepts an alias and writes the canonical ID, and the projected devkit-playbook skill text names alias retrieval.
Explicit wording in `CAP-DLV-spec-bundles`, `CAP-TRACE-code-entrypoints`, `CAP-DIST-manifest-spec`, the bundled
devkit `consumption` instruction and a glossary entry lie outside this unit's write scope; they are recorded as
`FB-alias-wording-outside-scope` for a follow-up edit, and none of them contradicts the implementation.
