---
id: PLAN-viewer-handbook-first-knowledge
spec: SPEC-viewer-handbook-first-knowledge
---

# Technical Plan: `SPEC-viewer-handbook-first-knowledge` Handbook-first knowledge view with on-demand book

## 1. Constitution & Invariant Review

None. The design is `ADR-handbook-first-book-on-request` and `ADR-handbook-staleness-from-version`. It adds no
endpoint, Git process or write path (`CAP-VIEW-repository-viewer` §2, §3, `ADR-viewer-working-tree`), and keeps
`RepositoryDataSource` unchanged (§6). `CAP-DLV-release-handbook` §2 loses only its viewer Out-of-Scope line.

## 2. Architecture Overview & Impact

- Target Area: viewer/ (frontend only; the server already serves `handbook/` through `tree` and `blob`).
- `frontend/src/lib/api/handbook.ts` (new): manifest, `VERSION` and page reads through `blob`, the absent-path
  convention `/^HTTP 404(?:\b|:)/`, staleness ordering, language choice and page rendering with link rewriting.
- `frontend/src/lib/features/knowledge/HandbookView.svelte` (new): handbook mode of the reading tab: header with
  staleness, sidebar (Handbook home, language switch, `Living Spec book` control, page headings), the page, and the
  absence or error state.
- `KnowledgeViews.svelte`: bindable `bookRequested` prop; index latch; book rendering gate; handbook mode.
- `KnowledgeSidebar.svelte`: a `Handbook` control in book mode.
- `SddViewer.svelte`: owns `bookRequested`, resets it with `source`/`branch`, derives it from a host deep link.
- `NavigationRail.svelte`: the `book` tab is labeled `Read`, titled `Handbook and Living Spec book`.
- No new dependency.

## 3. Component & Interface Design

```text
SddViewer (bookRequested state) ──bind──▶ KnowledgeViews(view, bookRequested)
                                            ├─ view=book ∧ ¬bookRequested ─▶ HandbookView ─▶ api/handbook (blob only)
                                            └─ otherwise ─▶ index latch ─▶ indexDocuments ─▶ book / bundles
```

```ts
// api/handbook.ts
export interface HandbookManifest { tag: string; langs: string[]; generated?: string; repository?: string }
export type Staleness = 'ahead' | 'equal' | 'behind' | 'absent';
export const isAbsent: (error: unknown) => boolean;                 // /^HTTP 404(?:\b|:)/ on the message
export function loadManifest(source, ref, signal): Promise<HandbookManifest | null>; // null: absent
export function loadVersion(source, ref, signal): Promise<string | null>;            // null: absent or unparsable
export function staleness(tag: string, version: string | null): Staleness;
export function initialLanguage(langs: string[]): string;           // stored, browser, else 'en'
export function rememberLanguage(lang: string): void;
export function renderHandbookPage(doc: RepositoryDocument, lang: string, page: string): RenderedDocument;
export function fragmentTarget(root: ParentNode, fragment: string): HTMLElement | null;
```

`KnowledgeViews` props gain `bookRequested?: boolean` (`$bindable`, default `false`). `onLocation(path, anchor, view,
meta)` keeps its signature; in handbook mode `path` is `handbook/<lang>/<page>` and `view` is `book`.

- **Index latch**: the index for a `source`/`branch` pair starts when `view !== 'book' || bookRequested` first holds
  and stays loaded while that pair is unchanged, so view changes never rescan or drop it.
- **Book gate**: `visibleDocs` is the book only when `view === 'book' && bookRequested`; handbook mode renders no
  `ChapterSection`.
- **Deep link**: `bookRequested` starts `initialView === 'book' && /^docs\/.*[^/]$/.test(initialPath)`, recomputed
  when `source`, `branch`, `initialView` or `initialPath` changes. A `handbook/<lang>/<page>` request is passed to
  `HandbookView`.
- **Links**: after DOMPurify, `https?:` links get `target="_blank" rel="noopener noreferrer"`; a relative `.md` link
  resolving inside `handbook/<lang>/` gets `data-handbook-page` and `data-fragment`; a fragment-only link stays on the
  page; any other relative link loses `href` and gains `class="unavailable"` and `aria-disabled="true"`. Headings get
  ids `handbook--<slug>` (deduplicated); raw ids from the page are kept, so `fragmentTarget` tries the raw id first,
  then `handbook--<fragment>`.

## 4. Storage & State Management

- `bookRequested` lives in `SddViewer` (component lifetime); the page remounts `SddViewer` per repository and branch.
- The chosen language is stored under `localStorage` key `sdd-handbook-lang` for all repositories.
- Handbook reads are not cached (three small reads); the index keeps its 30-second cache.

## 5. Error Handling & Edge Cases

- Manifest absent: absence note and the book control. Other manifest failure, invalid JSON, a missing `tag` or
  `langs` without `en`: the error message and the book control.
- `VERSION` failure of any kind or an unparsable value: staleness `absent` (tag and date only).
- Page read failure: the error with a `Handbook home` button; switching language to a page that is missing behaves the
  same.
- A requested language not in `langs` falls back to the initial language.
- Aborted reads never publish (an `AbortController` per load, as the other views).

## 6. Verification & Test Plan

- `frontend/src/lib/api/handbook.test.ts`: staleness (four states), DOMPurify keeps raw `id` anchors and our
  post-sanitize `target`/`rel` on external links, link classification, fragment targets, language choice.
- `frontend/src/lib/features/knowledge/KnowledgeViews.test.ts`: read budget with and without a manifest, error states,
  no `section.chapter` before the control also after Proposals, one index scan across Book, Proposals and Book,
  computed chapter order, header states, link behavior and cross-page fragments in `en` and `ko`, language memory,
  bindable request.
- `frontend/src/lib/SddViewer.test.ts`: rail label, request surviving a Dashboard visit, deep links and
  `sdd:path-change` in handbook mode.
- `tests/integration/features/browse/test_handbook.py`: `handbook/` reads through `blob`/`tree` with symlink and `..`
  refusals.
- Checks: `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer build` (commit the page),
  `uv run devkit generated check viewer-assets`, `just lint-check devkit-viewer`, `just check devkit-viewer`,
  `just test-affected`, `uv run devkit rules check --ci --base 3b219724`.
- Measurement: `coldload-probe.mjs` of `MAT-viewer-handbook-cold-load` against `devkit viewer serve` of this worktree
  with `Read` and `.handbook-page` as arguments, recorded as `cold-load-after.json` with a results section in the
  material.
