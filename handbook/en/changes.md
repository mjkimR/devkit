---
generated: true
---
# Changes

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.7` at source commit `c03315d43325`, generated 2026-11-17. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated page -->
Since the handbook snapshot `v0.1.6`:

### New decisions

- [`ADR-area-scoped-design-bundles`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-area-scoped-design-bundles.md): Formal designs live in area-scoped directory bundles with a design.md anchor and in-bundle support, and domain documents in area directories; IDs stay area-free, and operations stay flat.
- [`ADR-documentation-ownership-and-linked-design-entries`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-documentation-ownership-and-linked-design-entries.md): For distinct documentation responsibilities, we retain unique owners and linked ID-free design entries, to expose mechanisms without widening identity contracts, accepting discovery through selected owner links.
- [`ADR-formal-document-closings`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261117-formal-document-closings.md): For formal design, domain and operations documents, we close with limits the body does not state and an Update triggers section, and state shared authoring steps once, to stop template-induced padding, accepting that next-read pointers live only in related_* fields and body links.
- [`ADR-formal-document-delivery-integration`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-formal-document-delivery-integration.md): For formal document maintenance across delivery approaches, we consume shared document policy at existing delivery boundaries, to preserve complete impact coverage and ownership, accepting explicit per-change semantic review.
- [`ADR-formal-role-document-identities`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-formal-role-document-identities.md): For independently maintained role documents, we register design, domain and operations with canonical IDs and complete tool support, to enable direct discovery and references, accepting schema and migration work.
- [`ADR-frontmatter-only-decision-status`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261117-frontmatter-only-decision-status.md): For ADR and PADR status, date and whole supersession, we keep them only in the frontmatter and drop the body metadata block from the template, scaffold, handoff and existing ADRs, to remove a synchronization path and rote fields, accepting a one-time edit of 71 ADR bodies.
- [`ADR-internal-repository-viewer`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-internal-repository-viewer.md): For a viewer only devkit's local server hosts, we drop the Svelte library, generic-host fallbacks and remote-host features but keep the committed-build wheel and read-only working-tree server, to cut code and contract surface, accepting that no other host can embed it.
- [`ADR-linked-domain-relationship-views`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-linked-domain-relationship-views.md): For maintained conceptual relationships, we use linked ID-free domain entries with existing contract owners, to give question-specific understanding, accepting owner-led discovery and review-only link checks.
- [`ADR-problem-first-formal-document-openings`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-problem-first-formal-document-openings.md): For formal design, domain and operations documents, we open with the problem the document answers and keep the reader question as an authoring scoping step, to stop restating the summary, accepting that the question is no longer a visible section.
- [`ADR-recorded-formal-docs-assessment`](https://github.com/mjkimR/devkit/blob/v0.1.7/docs/decisions/2026-11/20261116-recorded-formal-docs-assessment.md): For reconcile records, we require design, domain and operations coverage (related_* IDs or a formal_docs none reason) when a commit newly resolves a record, checked by RULE-reconcile-contract, plus reviewer reimplementability findings, accepting one field and more review.

### Completed specs

- [`SPEC-adaptive-documenter`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261113-adaptive-documenter/spec.md): Adaptive documenter role
- [`SPEC-adr-body-metadata-removal`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-adr-body-metadata-removal/spec.md): Remove the ADR body metadata block and trim the ADR template
- [`SPEC-design-bundle-layout`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-design-bundle-layout/spec.md): Area-scoped directory bundles for formal design documents
- [`SPEC-design-document-foundation`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-design-document-foundation/spec.md): Documentation ownership and minimal design foundation
- [`SPEC-design-document-lifecycle`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-design-document-lifecycle/spec.md): Formal documentation authoring and reconciliation lifecycle
- [`SPEC-design-document-pilot`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-design-document-pilot/spec.md): Early content pilot for domain, design and operations
- [`SPEC-design-document-viewer`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-design-document-viewer/spec.md): First-class formal documentation in the repository viewer
- [`SPEC-domain-model-documents`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-domain-model-documents/spec.md): Domain-model documentation
- [`SPEC-envelope-commit-file-path`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-envelope-commit-file-path/spec.md): Envelope commit accepts a workspace-relative --file path
- [`SPEC-formal-doc-authoring-checkpoints`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-formal-doc-authoring-checkpoints/spec.md): Formal documentation checkpoints: route facts, review reimplementability, record assessments
- [`SPEC-formal-doc-padding-trim`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-formal-doc-padding-trim/spec.md): Trim padding from formal document guidance and documents
- [`SPEC-formal-docs-feedback-handoff`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-formal-docs-feedback-handoff/spec.md): Feedback lifecycle domain and proposal handoff design documents
- [`SPEC-formal-document-coverage`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-formal-document-coverage/spec.md): Formal document coverage across capability areas
- [`SPEC-formal-document-kinds`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-formal-document-kinds/spec.md): First-class design, domain and operations document kinds
- [`SPEC-formal-document-templates`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-formal-document-templates/spec.md): Template alignment for formal design, domain and operations documents
- [`SPEC-handoff-rewrite-overlap-scheduling`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-handoff-rewrite-overlap-scheduling/spec.md): Handoff rewrites as integration evidence in scope scheduling
- [`SPEC-handoff-sibling-alias-rewrite`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-handoff-sibling-alias-rewrite/spec.md): Handoff rewrites alias references to already handed-off proposals
- [`SPEC-open-feedback-fixes`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-open-feedback-fixes/spec.md): Fixes for four open feedback items
- [`SPEC-proposal-precedence-edges`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-proposal-precedence-edges/spec.md): Ordering claims between proposals checked when made
- [`SPEC-remaining-feedback-fixes`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-remaining-feedback-fixes/spec.md): Remaining formal-document-coverage feedback fixes
- [`SPEC-reverify-summary-required`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-reverify-summary-required/spec.md): envelope reverify requires a summary that envelope commit accepts
- [`SPEC-viewer-adr-summary-wording`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-viewer-adr-summary-wording/spec.md): Reword viewer ADR summaries that name library hosts
- [`SPEC-viewer-host-wording`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-viewer-host-wording/spec.md): Reword viewer documents still written for library hosts
- [`SPEC-viewer-internal-simplification`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261116-viewer-internal-simplification/spec.md): Viewer as an internal tool: drop the library surface and trim unused features
- [`SPEC-viewer-roadmap-plumbing`](https://github.com/mjkimR/devkit/blob/v0.1.7/specs/2026-11/20261117-viewer-roadmap-plumbing/spec.md): Remove dead other-branch plumbing from the viewer roadmap
<!-- /handbook:generated -->
