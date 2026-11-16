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

The dashboard lists candidate frontmatter per section, then reads the body of every eligible entry and shows all cards in sorted order; a failed body read shows its path and error beside the others. Dashboard sections are not cached; Dashboard Refresh reloads saved changes. Document-index and roadmap results retain their 30-second caches across tab switches. Recursive metadata requests avoid one request per directory.

The **Read** tab opens the repository's release handbook (`handbook/`, where `handbook/manifest.json` exists) in
the remembered or browser language, with a note when the snapshot trails `VERSION`; the Living Spec book is computed
only after `Living Spec book` is selected, so the tab's cold load reads three small files instead of indexing `docs/`
and `specs/`.

Proposals under Planning come from their `plan-<slug>` worktree, else their local branch, read locally after the
checkout's cards render on every dashboard or Proposals load, and show a source badge; the Proposals tab reads their
bundle files from the same source. Remote-tracking refs are not read and nothing is fetched.

Contract: `CAP-VIEW-repository-viewer`. Decisions: `ADR-internal-repository-viewer` (single host, server, working
tree and Planning overlay) and `ADR-release-handbook` (reading tab). Command reference:
[viewer](../../docs/development/reference/viewer.md).

## Layout

- `src/devkit_viewer/features/browse/`: `cli/` exposes the command, `http/` serves read-only routes,
  `usecases/` selects repositories and reads documents; `repositories/` reads saved
  working-tree files and Planning sources, and `models/` holds repository identity and errors. Models never import repository implementations.
- `src/devkit_viewer/static/`: the committed app build, a tracked generated artifact (`viewer-assets` in
  `.devkit/generated.toml`). Rebuild it with `just viewer build`; `devkit generated check viewer-assets` refuses a
  stale one.
- `frontend/`: the page, one Svelte Vite application with one source tree under `frontend/src/`. It is an internal
  app, not a library. `just viewer <lint|check|test|build>` runs its checks; only those changing the frontend need
  Node.

Dashboard and roadmap discover global `docs/roadmap/` and direct `docs/packages/<name>/roadmap/` roots, including
each flat `_archive/`. Discovery follows structural paths without a namespace registry, so unregistered directories
also appear; it does not certify document validity. Cross-root dependencies and direct proposals resolve over the
combined set before history filtering. History, totals and detail paths remain available; open counts exclude
done/dropped. Missing optional roots are empty and failed roots retain errors alongside successful results.


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
