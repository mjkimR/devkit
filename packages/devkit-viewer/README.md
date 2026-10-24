# devkit-viewer

A local, read-only page for the documents of devkit repositories: the Living Spec, proposals, specs and the
roadmap of milestone documents. It mounts `devkit viewer` under the `devkit` command line.

```sh
devkit viewer serve                         # the devkit project containing the current directory
devkit viewer serve --repo ../a --repo ../b # several repositories
devkit viewer serve --scan repos/           # every devkit repository directly under repos/
```

`serve` prints `[VIEWER: url=http://127.0.0.1:<port>/ repos=<n>]` and serves until interrupted. It reads committed
saved working-tree content and identifies each checkout's current branch, binds to `127.0.0.1` only, answers `GET` only and writes nothing. Approvals
stay where they are: the viewer records no decision and talks to no MCP tool.

Contract: `CAP-VIEW-repository-viewer`. Decisions: `ADR-viewer-distribution-and-frontend-build`,
`ADR-viewer-working-tree` supersedes `ADR-read-only-local-server-over-git-refs`. Command reference:
[viewer](../../docs/development/reference/viewer.md).

## Layout

- `src/devkit_viewer/features/browse/`: `cli/` exposes the command, `http/` serves read-only routes,
  `usecases/` selects repositories, reads documents and renders retained reports; `repositories/` reads committed
  working-tree files, and `models/` holds repository identity and errors. Models never import repository implementations.
- `src/devkit_viewer/static/`: the committed app build, a tracked generated artifact (`viewer-assets` in
  `.devkit/generated.toml`). Rebuild it with `just viewer build`; `devkit generated check viewer-assets` refuses a
  stale one.
- `frontend/`: one Svelte source for the page (`src/app/`) and the component library (`src/lib/`) that autohub
  vendors as an `npm pack` tarball. `just viewer <lint|check|test|build|pack>` runs its checks; only those changing
  the frontend need Node.
