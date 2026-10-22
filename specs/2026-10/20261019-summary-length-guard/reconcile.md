---
reconcile_id: REC-summary-length-guard
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
---

# Reconciliation: Summary length guard

`CAP-DLV-proposal-incubation` states that `new` and `padr` strip surrounding whitespace and reject empty, non-English or over-300-character summaries with `ARGUMENT_INVALID` targeting `--summary`, before writes. Its option and error rows agree with the shared validator and the six library/CLI refusal cases.

`CAP-DLV-spec-bundles` states the same limit and refusal behavior for spec creation. The six accepted boundary cases demonstrate that exactly 300 stripped characters remain valid. Omission/placeholders, ordinary valid summaries, empty/non-English refusals and handoff preservation remain covered by the existing eleven tests.

No architecture, story, dependency or domain-term change is required: creation remains within the existing proposal/spec scaffolding interfaces. No agreed work is deferred. Both capability summaries are rewritten in place to reflect creation validation.

Entrypoint derivation was reviewed: the proposal capability already covers `scaffold.py` through its proposals directory; the spec capability now declares the shared validator file explicitly. Test-file candidates were excluded because they are verification coverage rather than implementation entrypoints. Task boundary markup was normalized to the existing bold-label format so derivation sees the literal paths.
