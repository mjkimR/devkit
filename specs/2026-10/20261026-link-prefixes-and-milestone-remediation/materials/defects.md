# Agreed defects

The user decided in PROP-table-driven-document-kinds Planning (q2=a, q3=a, 2026-10-26) that these two defects are fixed
in a separate bugfix, so that refactor stays output-identical.

1. Viewer ID link prefixes (`FB-viewer-link-prefixes-drift`, recorded on the `plan-table-driven-document-kinds`
   branch; not yet on main, so this unit does not edit it: the Host resolves it after that proposal's handoff).
   `packages/devkit-viewer/frontend/src/lib/api/documents.ts` (about line 246) links `[CAP|US|ARCH|ADR|PROP|SPEC|PLAN|
   TASKS|REC|MAT|PADR-...]`; `US` is the retired use case prefix and `UC`, `FB`, `MS` references render as plain text.
   Make the list match `PREFIXES` in `packages/devkit-spec/src/devkit_spec/features/documents/models/ids.py`. A
   reference that resolves to no document stays plain text as today. Rebuild the committed page.
2. Misplaced milestone remediation: `_target` in
   `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/id_convention/` (governance usecases
   `id_convention.py` around :291-294) gives the dated-partition remediation to any target outside `_LIVING_SPEC`, so
   a misplaced milestone is told to move into a dated partition, although milestones live flat under `docs/roadmap/`
   (global only). The remediation names the milestone's real location; other kinds' messages stay byte-identical.
Reproduce each with a failing test first.
