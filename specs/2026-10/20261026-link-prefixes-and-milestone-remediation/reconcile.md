---
reconcile_id: REC-link-prefixes-and-milestone-remediation
status: resolved
targets: []
---

# [REC-link-prefixes-and-milestone-remediation] Viewer ID link prefixes and milestone path remediation

No Living Spec document changes. Both fixes restore behavior the current contracts already require, and no contract
states the replaced text:

- `CAP-VIEW-repository-viewer` §4 promises in-page links between documents by ID and lists no prefix set; the ID
  grammar the viewer now follows is the one `CAP-DOCS-document-model` defines through `PREFIXES`.
- `CAP-GOV-spec-rules` states that a milestone lives at `docs/roadmap/MS-{slug}.md` and quotes no path remediation
  text; the rule guide's remediation step already says a milestone's ID is its file stem, which the new remediation
  now matches. `CAP-DOCS-document-model` states no remediation.

Entrypoints: with no target, `devkit spec entrypoints derive` has no document to pair, so no entrypoint changes.

Source feedback: the viewer link prefix feedback recorded on the `plan-table-driven-document-kinds` branch is not on
this branch's base, so this unit does not edit it; the Host resolves it after that proposal's handoff
(`materials/defects.md`).
