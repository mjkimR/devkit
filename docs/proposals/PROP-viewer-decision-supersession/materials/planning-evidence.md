# Viewer supersession Planning evidence

Baseline: `7ed35b755138e9460e1de6f42d10b390886f448b`. Scout read at
`aa6e739f8ccb7ba3689a468ebf2edc8a78a25e72`; only proposal intent/status changed between them.

| Question | Evidence | Conclusion |
| --- | --- | --- |
| Shared data source | `frontend/src/lib/api/documents.ts:140-163` under `packages/devkit-viewer/`; `CAP-VIEW-repository-viewer` section 4 | Read already indexes docs/specs. Browser relation derivation works for local and library hosts without a new API. Existing idIndex alone omits aliases. |
| Read placement | `packages/devkit-viewer/frontend/src/lib/features/knowledge/ChapterSection.svelte:38-58` | Chapter header precedes the body and is the natural summary boundary. |
| Files placement | `packages/devkit-viewer/frontend/src/lib/features/document/DocumentViewer.svelte:49-64`; `packages/devkit-viewer/frontend/src/lib/SddViewer.svelte:197-238` | Files has no repository index; lazy decision-only index loading is necessary for reverse relations. |
| Existing metadata | `packages/devkit-viewer/frontend/src/lib/features/document/FrontmatterHeader.svelte:7-40` | The draft's header describes Files, so book-only implementation would omit that surface. |
| Query semantics | `packages/devkit-docs/src/devkit_docs/features/documents/usecases/supersession.py:31-77` | Preserve unresolved outgoing targets; whole needs matching status and superseded_by; incoming candidates are ADRs, not PADRs. |
| Source statement | `packages/devkit-docs/src/devkit_docs/features/documents/models/supersession.py:13-64`; `packages/devkit-docs/src/devkit_docs/features/documents/models/markdown.py:1-18` | Use the later statement's source text, excluding hidden examples and ending at paragraph/item/heading boundaries. |
| Partial reads | `packages/devkit-viewer/frontend/src/lib/api/documents.ts:90-151` | Preserve errors and successful relations without claiming a complete reverse list. |
| Planning source | `packages/devkit-viewer/frontend/src/lib/features/knowledge/KnowledgeViews.svelte:210-273`; `CAP-VIEW-repository-viewer` section 4.2 | PADR source must remain the selected bundle; current ADR incoming relations must not absorb proposals. |
| UX obligations | `ADR-ux-screens`; `docs/ux/README.md`; `.devkit/managed/docs/instructions/ux-writing.md` | Draft screen/panel, a narrow use case and register rows before code; write retained documents during spec-sync. |
| Build verification | `packages/devkit-viewer/frontend/package.json`; `.devkit/generated.toml` | Native frontend checks and the tracked viewer-assets build are required in Development. |

The scout's read-only snapshots both equal `3fcf427f381a203f03f82ed60d4e4f5107a6871f`; HEAD remained
`aa6e739f8ccb7ba3689a468ebf2edc8a78a25e72`. Codex isolation is emulated: explicit paths, snapshots and
per-operation approval substitute for native confinement. No outside-worktree read was reported.

Browser index derivation avoids a local-only endpoint and new host API requirements. A Python endpoint would reuse
one parser, but would add runtime coupling and need an equivalent interface for remote library hosts. Retain the
browser approach with parity fixtures. No performance measurement or production test is claimed by Planning.

Mandatory challenger at `2456098ee37cf9bc646511611735ec94fef60499` found two P2 gaps.
The design now derives subject metadata/statements from the exact displayed document rather than its cached
index copy; relation reload retains that subject version. Proposal-detail PADR target links explicitly open the
checkout ADR in Files, using the existing outside-bundle navigation path. Development AC-4/AC-5 and the Screens
carry both regressions. Challenger snapshots both equal `287e05920bb406c5a26f4ed2a4dbfc3990fcd988` and HEAD
remained unchanged; no outside-worktree read was reported.
