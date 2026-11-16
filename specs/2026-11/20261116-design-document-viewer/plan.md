---
id: PLAN-design-document-viewer
spec: SPEC-design-document-viewer
---

# Technical Plan: `SPEC-design-document-viewer`

## 1. Constitution & Invariant Review

Preserve `ARCH-05-2-components`, existing viewer browser parsing and structural namespace discovery,
`CAP-VIEW-repository-viewer` loading/cache/source guards and decision-only supersession UI. No feature edge,
package dependency or new ADR is needed. Core implementation at 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4
matches the pinned core contract and supplies all five active migrated nodes.

## 2. Architecture Overview & Impact

Extend the existing browser document layer and shared document components. Identity resolution is shared by
rendering and reference projection; current graph rows use canonical targets without alias edges. Book filters
operate on visible results while retaining the full loaded identity index. A source-bound artifact reader uses
existing blob callbacks, byte decoding and bounded disposable URLs. Both Read and Files use the same sanitized
renderer and formal panel. Generic Python browse behavior remains unchanged with new-kind guard/byte tests.
Handbook source lookup recognizes formal identities without extending generated membership.

## 3. Component & Interface Design

- `api/documents.ts`: permissive ID recognition, canonical/alias ambiguity resolution, groups and relative links.
- `features/document/references.ts` and shared panel: typed/current/prose references versus provenance, metadata,
  loaded-index completeness and retry; decision supersession remains a separate interpretation.
- `api/artifacts.ts` and supporting-file component: source-bound blob read, safe MIME/format handling, abort and
  URL disposal, raw/preview/download and contextual Back; no required RepositoryDataSource addition.
- Knowledge views/sidebar/chapters: search, Include retired, selected hidden target, raw/back context and shared panel.
- Files integration: rendered formal index trigger, shared renderer/link handling and non-text blob display.

## 4. Storage & State Management

Retain the existing per-source/ref cache and cancellation generation. Artifact URLs are bounded per renderer
and revoked on replacement/disposal. Return context records source identity, branch, document path and anchor;
a source change clears it. No persistent state or migration is added.

## 5. Error Handling & Edge Cases

Missing/ambiguous IDs keep written identities without arbitrary links. Malformed known metadata yields visible
incomplete rows; unknown metadata remains inspectable. Missing/unsupported artifacts show path/format and Back,
with download only when bytes exist. Decoding errors never turn binary bytes into replacement text. Planning
source reads require planningBlob and never silently use checkout data. Preserve path and symlink guards.

## 6. Verification & Test Plan

Map AC-01/02/03 to document, supersession, KnowledgeViews and SddViewer tests; AC-04/05 to artifact API/component
and composed maintenance fixtures; AC-06 to backend tree/blob regressions, public library import/pack, wheel
static inspection and declared generated check; AC-07 to handbook script tests and reconciled UX contracts.
Run `just lint-check devkit-viewer`, `just check devkit-viewer`, focused handbook/backend tests and
`just test-affected --base 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4 --tier unit-integration` preserving full fallback.
Run `just viewer install`, `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer pack`,
`just viewer build`, and `uv run devkit generated check viewer-assets`. Native tests run synchronously here.
The Host owns integrated-result verification. HIGH independent code and reconcile reviews use frozen snapshots.
