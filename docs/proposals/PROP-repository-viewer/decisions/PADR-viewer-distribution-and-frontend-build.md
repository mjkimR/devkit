---
id: PADR-viewer-distribution-and-frontend-build
title: Viewer distribution and frontend build
summary: Ships the viewer as a separate devkit-viewer distribution that mounts a devkit viewer command, commits the built assets as a tracked generated artifact so installs need no Node, and gives autohub the Svelte component library as a vendored npm pack tarball.
proposal: PROP-repository-viewer
status: draft
created_at: 2026-10-19
---

# [PADR-viewer-distribution-and-frontend-build] Viewer distribution and frontend build

- **Status**: Draft
- **Date**: 2026-10-19

---

## 1. Context & Problem Statement

devkit owns the viewer source (decided in Backlog). devkit is a Python monorepo: consumers install its distributions
from Git subdirectories at a pinned commit (autohub's `pyproject.toml` pins `devkit-agt` and `devkit-advisory` with
`git`, `subdirectory` and `rev`), so `uv` builds them from source on every install. The viewer is a Svelte 5
component that two hosts need: devkit's own local server and autohub's SvelteKit UI. This decision chooses the
distribution, where the built assets come from, and how autohub receives the component.

---

## 2. Decision Drivers

- Installing devkit from Git never needs Node or npm network access.
- One source for both hosts; no registry publication.
- People who do not run the viewer do not install its assets (the lazily loaded `mermaid` alone is several MB).
- One `devkit` executable (`ADR-mount-under-the-devkit-command-line`).
- Do not reintroduce what autohub removed in `0d8c05f`: runtime loading of an externally hosted Custom Element bundle
  named by an HTTPS URL and SHA-256 in a Git-ignored local file, downloaded at deployment build time, and published
  as a separate operation.

---

## 3. Considered Options

### Distribution

- **Inside `devkit-spec`, behind an extra**: an extra adds dependencies only, so the built assets would ship in every
  `devkit-spec` install.
- **`devkit-catalog`**: holds data-only content bundles; runtime Python code belongs elsewhere
  (`MS-catalog-and-context-scaling` non-goals).
- **A separate `devkit-viewer` distribution (Selected)**: mounted through the `devkit.commands` entry point like
  `devkit spec`; installed only by those who run it. It needs no `devkit-spec` code, because the browser parses the
  documents (`PADR-read-only-local-server-over-git-refs`).

### Built assets

- **Build at wheel build time**: every Git install would need Node and npm network access.
- **Download a release artifact at run time**: a publication step and network access at run time.
- **Commit the built assets as a tracked generated artifact (Selected)**: registered in `.devkit/generated.toml`
  (`CAP-GEN-tracked-artifacts`), so `devkit generated check` in CI refuses stale assets and a merge conflict in them
  is settled by regenerating. Node is needed only to change the frontend.

### autohub consumption

- **npm registry**: excluded (no publication).
- **`git+https` dependency**: npm installs only a repository's root package, and the viewer lives in a subdirectory.
- **Runtime-loaded Custom Element bundle**: what autohub removed in `0d8c05f`.
- **Vendored `npm pack` tarball (Selected)**: autohub commits the tarball under `modules/hub-ui/vendor/`, depends on
  it with `file:vendor/<name>.tgz`, pins its integrity in `package-lock.json` and documents the source commit and
  rebuild steps, as it already does for app-common's `api-codegen` (`vendor/api-codegen.md`). The component is
  compiled into autohub's own build, so none of the removed runtime-loading machinery returns.

---

## 4. Decision Outcome

- **Python**: `packages/devkit-viewer/`, distribution `devkit-viewer`, import package `devkit_viewer`, depending on
  `devkit-agt` for `devkit.core.cli`. Entry point `devkit.commands` `viewer`; the command is `devkit viewer serve`.
- **Frontend**: one npm project under `packages/devkit-viewer/frontend/` with two outputs from one source:
  - a Svelte component library (`svelte-package`): the viewer moved from autohub (`SddViewer`, `KnowledgeViews`,
    `documents.ts`, the `RepositoryDataSource` interface) plus the new roadmap view; `svelte` is a peer dependency;
  - a Vite single-page app that imports the library, adds the repository switcher, and builds into
    `src/devkit_viewer/static/`.
- **Assets**: the app build output is committed and registered as a generated artifact whose inputs are the frontend
  sources and lockfile. Development verifies that the build is reproducible from the lockfile before relying on
  `devkit generated check`.
- **autohub**: keeps `RepositoryView`, its Git browser (`FileTreeTable`, `FileBlobViewer`) and its run and decision
  panels (`SddExecution`, `SddProposals`, `SddRunLinks`), and passes its existing GitHub-backed data source to the
  library component. Adopting the tarball is autohub's own change, made after a devkit commit carries the library.
- **Checks**: the `just` recipes gain the frontend (lint, type check, unit tests) through `scripts/`; `just smoke`
  checks that the installed wheel serves its assets.

---

## 5. Consequences

- The repository gains its first Node toolchain, for frontend contributors only.
- The library's props and `RepositoryDataSource` become an interface autohub depends on. The vendored tarball pins a
  commit, so a breaking change reaches autohub only when it refreshes the tarball; the release note of such a change
  names it.
- Refreshing the tarball in autohub is a manual step, documented beside the tarball.
- `AGENTS.md` and the README list the new distribution, and the layering test covers `devkit_viewer`.
