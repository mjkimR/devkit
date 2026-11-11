---
sources:
  ADR-release-handbook: e3e8ebe1591bba2371628761d8af35a69ba685b7
  ADR-repository-viewer: 4cb9669212aa58f1abeefed1c5715adcb3305324
  CAP-COLL-shared-artifacts: 092d06230b033004a559d4fa72907fac6d0e0f5d
  CAP-GEN-tracked-artifacts: ff8539b14d3af5890ba656e23b0e43c1d0d05fc8
  CAP-VIEW-repository-viewer: 2d5d20c1b78e7fb0dc93c192d91d9245901f88e5
title: Viewer
---

# Viewer

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `f115e96c8059`, generated 2026-11-11. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](../journeys/advance-an-idea.md)
- [Assess a selected test suite](../journeys/assess-test-management.md)
- [Design necessary command entry points](../journeys/design-command-entrypoints.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Execute an isolated command](../journeys/execute-an-isolated-command.md)
- [Explore a design problem](../journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](../journeys/import-third-party-agent-assets.md)
- [Improve an interface and user flow](../journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Read decision supersession](../journeys/read-decision-supersession.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](../journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](../journeys/snapshot-bundle-sources.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The viewer is a local, read-only web page for the documents agents read through `devkit docs` and `devkit spec`: the Living Spec,
proposals, spec bundles, milestones and feedback, across one or more devkit repositories
(`CAP-VIEW-repository-viewer`). It ships in the optional `devkit-viewer` package and mounts `devkit viewer`. It is a
place to look, not to act: no approval, gate decision or answer is recorded there. For what these documents are, see
[Concepts](../concepts.md); to find a document from the command line instead, see the journey
[Find the right documents](../journeys/find-the-right-documents.md).

## Start it

```sh
uv run devkit viewer serve                          # the devkit project you are in
uv run devkit viewer serve --repo ../a --repo ../b  # specific repositories (Git top levels)
uv run devkit viewer serve --scan repos/            # every direct child holding .devkit/config.toml
uv run devkit viewer serve --port 0                 # any free port (default 8765)
```

It prints one line, `[VIEWER: url=http://127.0.0.1:8765/ repos=3]`, and serves in the foreground until you stop it
with Ctrl-C. It is not a daemon. Each repository is identified by its directory name, so two registered directories
with the same name are refused (`VIEWER_REPO_DUPLICATE`), as are a `--repo` that is not a Git top level
(`VIEWER_REPO_INVALID`), nothing to serve (`VIEWER_NO_REPOSITORY`) and a busy port (`VIEWER_PORT_IN_USE`). Add `-v`
for one request log line per request on stderr.

## What you see

The page has a repository picker, a label for the checked-out branch and these tabs (English descriptions of the UI labels):

- **Dashboard**: milestones, proposals and feedback, each section loading on its own and paging with
  Load more.
- **Read**: the repository's release handbook when `handbook/manifest.json` exists, in the language you pick
  (remembered in the browser), with its tag and a note when the checkout's `VERSION` has moved past it; otherwise a
  short absence note. The **Living Spec book** control computes the book of `docs/`, grouped into the chapters
  Overview, Architecture, Capabilities, Use Cases, UX, Steering, Decisions and Development, with links between
  documents by ID, only when you ask for it (`ADR-release-handbook`,
  `ADR-release-handbook`).
- **Proposals** and **Specs**: `docs/proposals/PROP-*/proposal.md` and the bundles under `specs/`, with their files,
  filters and task progress.
- **Roadmap**: the milestones under global and registered namespace roadmap roots, ordered active then planned, with readiness from `depends_on`.
  `done` and `dropped` milestones, kept in `docs/roadmap/_archive/`, appear with the history toggle; a hidden finished
  prerequisite still counts as satisfied.
- **File browser**: the working tree, rendering Markdown, frontmatter and Mermaid.

The viewer shows the saved files of the registered working tree, including uncommitted and untracked ones, on the
branch currently checked out (`ADR-repository-viewer`). It never switches branches. Documents are parsed in the
browser, so repositories that pin different devkit-docs versions all render, and a document with malformed
frontmatter is listed as unreadable while the rest still show.

### Freshness

Results are cached for 30 seconds per repository and branch. Use the dashboard's Refresh button to reload at once,
or reload the browser page. There is no file watching.

## Proposals still under Planning

A proposal under Planning is edited on its own `plan-<slug>` branch, so the base checkout may hold an older copy. The
Dashboard proposal section and the Proposals tab overlay the Planning version, read from local sources only, in this
order (`ADR-repository-viewer`):

1. another worktree on `plan-<slug>` (its saved files);
2. the local branch `plan-<slug>`;
3. a remote-tracking `<remote>/plan-<slug>`, as of your last fetch.

Branches already merged into your `HEAD` are skipped, and nothing is shown for the branch you are on. An overlaid card
carries a source badge. The viewer never fetches or calls GitHub, so fetch first if you want to see a colleague's
remote Planning branch. If the overlay fails, the checkout's cards stay with a short note. The overlay covers proposals
only; specs, milestones, feedback, the Living Spec and the file browser always read the registered working tree.

## Read a shared proposal review

`/review/<repository-id>/<generation-id>` shows one exact `proposal-review` shared artifact from that repository's
local store (`CAP-COLL-shared-artifacts`, see [Collaboration](collaboration.md)). The page shows its source commit,
language and expiry prominently, and displays the Markdown as escaped text, so nothing in it can run. An expired
report answers `410` and a missing one `404`; ask the Host to publish a fresh one. The viewer never regenerates
reports.

## Safety

- It binds `127.0.0.1` only and refuses requests whose `Host` header is not `127.0.0.1` or `localhost` with that port
  (`VIEWER_HOST_REFUSED`), which blocks DNS-rebinding pages. No CORS headers are sent.
- It answers `GET` only and never writes, commits or fetches.
- Paths with `..`, `.git` segments, backslashes or a leading `/` are refused; symlinks are neither listed nor read.
- Rendered Markdown and SVG pass through DOMPurify.

## Changing the viewer

The frontend under `packages/devkit-viewer/frontend/` is one Svelte source with two outputs:

- the page, built into `src/devkit_viewer/static/` and committed as the tracked generated artifact `viewer-assets`
  (`CAP-GEN-tracked-artifacts`). Installing devkit therefore needs no Node; only a frontend change does. After one,
  run `just viewer lint`, `just viewer check`, `just viewer test` and `just viewer build`, and
  `devkit generated check viewer-assets` confirms the committed build.
- the component library `devkit-viewer`, packed as a tarball that autohub vendors. A host supplies its own
  `RepositoryDataSource` and keeps authentication on its side. Nothing is published to a registry.

## Namespace roadmaps

The roadmap and dashboard include milestones from global `docs/roadmap/` and each registered namespace's
`docs/packages/<name>/roadmap/`, including their flat `_archive/` directories when history is selected.
Dashboard sections read candidate headers once, load only their first page of bodies and retain expanded pages
in the 30-second cache. A failed next page preserves prior cards and offers Retry; Refresh invalidates that source's cache.

## Sources

- [CAP-VIEW-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/viewer/CAP-VIEW-repository-viewer.md):
  serving, endpoints, Planning sources, page behaviour, roadmap, library and the review page.
- [Viewer quick reference](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/development/reference/viewer.md).
- [ADR-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-repository-viewer.md),
  [ADR-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-repository-viewer.md),
  [ADR-release-handbook](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-release-handbook.md),
  [ADR-release-handbook](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-release-handbook.md).
