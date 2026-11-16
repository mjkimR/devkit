# devkit-viewer frontend

The page that `devkit viewer serve` serves: one Svelte 5 Vite application for the Living Spec, proposals, specs,
roadmap and file tabs of devkit repositories. It is an internal app with one host; it is not packaged or published as
a library. Vite builds it into `../src/devkit_viewer/static/`, which is committed as the `viewer-assets` generated
artifact so a Git install of `devkit-viewer` needs no Node. Contract: `CAP-VIEW-repository-viewer`.

```sh
just viewer install   # npm ci
just viewer lint      # prettier --check
just viewer check     # svelte-check
just viewer test      # vitest
just viewer build     # rebuild the committed page; commit it with the sources
```

## Layout

- `src/main.ts` and `src/App.svelte`: the application entry and the repository picker. The page always opens on the
  Dashboard, and the URL hash holds only the repository.
- `src/SddViewer.svelte`: the tabs (Dashboard, Read, Proposals, Specs, roadmap and Files). The Read tab's view id is
  `book`; its Living Spec book request is internal to `SddViewer` and lasts across rail switches for the source and
  branch it was made for.
- `src/api/`: the data source and readers. `repository.ts` declares `RepositoryDataSource` and `httpDataSource`, its
  implementation over the local HTTP API; `local.ts` lists repositories and reads and writes the URL hash; and
  `documents.ts`, `milestones.ts`, `roadmap.ts`, `planning.ts`, `handbook.ts`, `artifacts.ts` and `cache.ts` read and
  cache documents.
- `src/features/<feature>/`: `dashboard`, `knowledge`, `document`, `roadmap`, `explorer` and `diagrams` views;
  `src/components/` and `src/state/` hold shared components and state.
- Tests sit beside their sources as `*.test.ts`.

## Data source

`RepositoryDataSource` has only required members, each taking an optional `AbortSignal`: `info`, `tree(path)`,
`treeRecursive(path)`, `blob(path)`, `dashboardList(section)`, `planningProposals()`, `planningTree(source, path)` and
`planningBlob(source, path)`. There is no `refs` member and no `ref` argument. `blob` rejects an absent file with an
error whose message starts with `HTTP 404`; the Read tab treats that as "no handbook".

`dashboardList` returns `{items, errors}` for `milestones`, `proposals` or `feedback`, each item holding only UTF-8
frontmatter. A dashboard section sorts and counts from it, then reads the body of every eligible entry and shows all
cards; a failed body read shows its path and error and still counts. Sections are not cached; Dashboard Refresh clears
the source's caches. The document index and roadmap are reused for 30 seconds within a page.

`planningProposals` returns `{sources, items, errors}`: each Planning source (`{id, kind, label, slug}`, a worktree or
local branch) and its own `docs/proposals/PROP-<slug>/proposal.md`. The Dashboard and Proposals tab request it on
every load after the checkout's cards render and update matching proposals in place with the source label, appending
Planning-only ones; `planningTree` and `planningBlob` read an overlaid proposal's bundle from that source. The overlay
is never cached and never orders the checkout list.

Formal DESIGN, DOMAIN and OPS entries have explicit book chapters, canonical/alias search and an Include retired
control. Direct references retain selected historical targets. Read and rendered Files share current incoming/
outgoing reference context and separately labelled provenance. View raw retains the reading context.
Parent-linked Markdown/Mermaid, CSV/source text and safe image previews use the existing `blob` reads; unsupported
bytes keep an explicit download state. Source/branch cancellation and object-URL cleanup apply, and Planning
supporting reads never use checkout fallback. No additional data-source member or document-engine dependency is required.

Designs and Domain are grouped by area. Design anchors are area-scoped `<ID>/design.md` bundles, labelled by
canonical ID. The shared context lists every other bundle file at any depth as supporting content; Domain/OPS
list adjacent ID/artifacts support. The source tree inventory is reused without prefetching support blobs.
Invalid identified support, nested design anchors and orphan files never become canonical nodes or graph identities.
