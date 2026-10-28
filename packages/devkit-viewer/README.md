# devkit-viewer

A local, read-only page for the documents of devkit repositories: the Living Spec, proposals, specs and the
roadmap of milestone documents. It mounts `devkit viewer` under the `devkit` command line.

```sh
devkit viewer serve                         # the devkit project containing the current directory
devkit viewer serve --repo ../a --repo ../b # several repositories
devkit viewer serve --scan repos/           # every devkit repository directly under repos/
```

`serve` prints `[VIEWER: url=http://127.0.0.1:<port>/ repos=<n>]` and serves until interrupted. It reads
saved working-tree content and identifies each checkout's current branch, binds to `127.0.0.1` only, answers `GET` only and writes nothing. Approvals
stay where they are: the viewer records no decision and talks to no MCP tool.

The dashboard lists candidate frontmatter per section, then reads only the first page of full bodies (6 milestones, 9 proposals, 6 feedback). Load more appends one sorted page. Lists and displayed pages are reused across tab visits for 30 seconds from list completion; additional pages do not extend expiry. Dashboard Refresh reloads saved changes and resets the first page. Document-index and roadmap results retain their 30-second caches. Recursive metadata requests avoid one request per directory.

The **Read** tab opens the repository's release handbook (`handbook/`, where `handbook/manifest.json` exists) in
the remembered or browser language, with a note when the snapshot trails `VERSION`; the Living Spec book is computed
only after `Living Spec book` is selected, so the tab's cold load reads three small files instead of indexing `docs/`
and `specs/`.

Proposals under Planning come from their `plan-<slug>` worktree, local branch or remote-tracking ref, read locally
after the checkout's cards render, and show a source badge; the Proposals tab reads their bundle files from the same
source. Nothing is fetched.

Contract: `CAP-VIEW-repository-viewer`. Decisions: `ADR-viewer-distribution-and-frontend-build`,
`ADR-viewer-working-tree` supersedes `ADR-read-only-local-server-over-git-refs`, and
`ADR-viewer-planning-proposal-overlay` adds the Planning overlay, and `ADR-handbook-first-book-on-request` with
`ADR-handbook-staleness-from-version` shapes the reading tab. Command reference:
[viewer](../../docs/development/reference/viewer.md).

## Layout

- `src/devkit_viewer/features/browse/`: `cli/` exposes the command, `http/` serves read-only routes,
  `usecases/` selects repositories, reads documents and renders retained reports; `repositories/` reads saved
  working-tree files and Planning sources, and `models/` holds repository identity and errors. Models never import repository implementations.
- `src/devkit_viewer/static/`: the committed app build, a tracked generated artifact (`viewer-assets` in
  `.devkit/generated.toml`). Rebuild it with `just viewer build`; `devkit generated check viewer-assets` refuses a
  stale one.
- `frontend/`: one Svelte source for the page (`src/app/`) and the component library (`src/lib/`) that autohub
  vendors as an `npm pack` tarball. `just viewer <lint|check|test|build|pack>` runs its checks; only those changing
  the frontend need Node.

Dashboard and roadmap discovery includes terminal milestones in the flat `docs/roadmap/_archive/`.
Their history, prerequisite satisfaction, totals and detail paths remain available; open counts exclude done/dropped.
