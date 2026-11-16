---
id: PROP-viewer-internal-simplification
title: 'Viewer as an internal tool: drop the library surface and trim unused features'
summary: autohub no longer vendors the viewer library, so remove the npm library surface and generic-host fallbacks and trim viewer features nothing in the repository uses.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: viewer/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-viewer/
    - docs/capabilities/viewer/
    - docs/usecases/viewer/
    - docs/development/reference/viewer.md
    - scripts/viewer.sh
  excludes:
    - handbook/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-viewer-internal-simplification] Viewer as an internal tool: drop the library surface and trim unused features

## 1. Background & Hypothesis

`ADR-repository-viewer` built the viewer as one Svelte source with two hosts: devkit's local server and autohub's
SvelteKit UI, which vendored an `npm pack` tarball of the component library. autohub now builds its own viewer and no
longer consumes the library. The viewer remains this repository's internal Living Spec browser, served by
`devkit viewer`.

Hypothesis: every accommodation that exists only for a foreign host can go, and several features sized for a remote
host or for retired producers can be trimmed, without losing what the repository uses (book, proposals and specs,
handbook, roadmap, dashboard, formal references, supersession, explorer, Mermaid).

Accommodations that exist only for the external host (from a read-only audit at `b0b4e2a09`):

- npm library packaging: `frontend/package.json` `exports`/`files`/`svelte`/`types`, `peerDependencies.svelte`,
  the `svelte-package` step; `just viewer pack` and its tarball check (`scripts/viewer.sh`); the CI pack step
  (`.github/workflows/ci.yml`); `&& just viewer pack` in `scripts/affected_tests.py`.
- The library barrel `frontend/src/lib/index.ts` and its wrappers/shims; the `lib/` and `app/` split.
- Optional `RepositoryDataSource` members (`treeRecursive?`, `dashboardList?`, `planningProposals?`, `refs?`), the
  no-`dashboardList` discovery path with its six-worker queue, and the `ref` parameter the local server ignores.
- Host props and events: `initialView`/`initialPath` book deep links, `sdd:path-change`, bindable `bookRequested`.
- Docs: CAP-VIEW §6 "The library for autohub" and the autohub mentions in it; `ARCH-05-1-containers` "Svelte library tarball" and
  the vendored-library edge; `ADR-repository-viewer` (two hosts, autohub section, data-source interface consequence);
  `ADR-release-handbook` library-host clauses; the package README and `docs/development/reference/viewer.md`.

Kept regardless: the wheel that ships the committed static build and the `viewer-assets` generated artifact (they let a
Git install run without Node, not autohub), the `devkit.commands` entry point, loopback/GET-only server guards, the
frontend lint/check/test/build/probe checks.

Trim candidates beyond the library surface:

1. **Shared tab and `/review/<repo>/<generation>`** (about 1.3k frontend and 350 backend lines with tests): nothing in
   the repository produces `proposal-review` shared artifacts since the proposal report was decoupled; removing them
   also drops the backend's dependency on `devkit_dist` shared APIs.
2. **Dashboard paging and caching** (about 600-900 lines plus tests): 6/9/6 pages, Load more, per-page Retry, 30 s
   list/page caches and the purpose cap were sized for a remote host's cold load; locally `dashboard-list` plus full
   reads are cheap.
3. **Planning overlay** (simplify or drop): keep worktree and local-branch proposal sources, drop remote-tracking
   precedence, merged-ref exclusion, overlay caching and order seeding; or remove the overlay entirely.
4. **Small optional ones**: multi-repo `--scan` and the repo picker; the Mermaid fullscreen modal; restricting
   bundled Mermaid diagram types to shrink the 5.5 MB static build.

## 2. Technical Spike Questions

- **Q1**: Which trim candidates (1-4) are in scope? Shared tab and `/review` are recommended; dashboard paging and the
  planning overlay need a decision on how much remote-host behavior to keep.
- **Q2**: Collapse `frontend/src/lib` into an app-only structure, or keep the split with only the barrel removed?
- **Q3**: Supersede `ADR-repository-viewer` with a new decision (viewer is internal-only, one host) or amend it?
  Its immutable proposal review clauses go if `/review` goes.
- **Q4**: Keep the internal URL deep links (book `initialView`/`initialPath`) for the local app, or remove them with the
  host event?
- **Q5**: Does the change split into two specs (library removal and docs; feature trims) or stay one unit?

## 3. Proposed Design & Impact

- Remove the npm library surface, its CI and affected-test steps, and the generic-host fallbacks; make the data-source
  members the local server provides required.
- Trim the features Q1 selects, with their backend routes, usecases, error codes, tests and docs.
- Update CAP-VIEW, `docs/usecases/viewer/*`, `ARCH-05-1-containers` and `ARCH-05-2-components` viewer text, the package README and the viewer reference;
  record the decision that the viewer serves one internal host.
- Regenerate `viewer-assets` after the frontend change; `just viewer` checks and `just test-affected` must pass.
- No change to `devkit viewer` command names or the wheel's static-build shipping.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1-Q5 with the user and, if Q5 says so, records the split.
- Accepted with handoff to Development once the plan is reviewed; integrated locally under `dev-integration=auto`.
- Retire the proposal when the trimmed viewer lands and the docs no longer mention a library host.
