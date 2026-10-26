---
sources:
  ADR-handbook-first-book-on-request: 07e5e9b99ca797eb88d8b1c822e867787b467d60
  ADR-handbook-staleness-from-version: 131d31e3a445b2b224f4e69911e5578b564f6fef
  ADR-viewer-planning-proposal-overlay: 9846db226f8b490434bf16f96ec8214b3771f855
  ADR-viewer-working-tree: a30f877468912cf550d6214ce4d1e219b2192950
  CAP-COLL-shared-artifacts: d000f00d3b8d672ea0473d3c6f01dafafe3b8f70
  CAP-GEN-tracked-artifacts: a934a5865acf8170b874bff2de6ddc36f5c401f4
  CAP-VIEW-repository-viewer: 72250394d5598dd6e28792b3312f0accad466f13
title: Viewer
---

# Viewer

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
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

The viewer is a local, read-only web page for the documents agents read through `devkit spec`: the Living Spec,
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

The page has a repository picker, a label for the checked-out branch and these tabs (labels as shown in the UI):

- **Dashboard**: milestones, proposals and feedback, each section loading on its own and paging with
  Load more.
- **Read**: the repository's release handbook when `handbook/manifest.json` exists, in the language you pick
  (remembered in the browser), with its tag and a note when the checkout's `VERSION` has moved past it; otherwise a
  short absence note. The **Living Spec book** control computes the book of `docs/`, grouped by chapter with links
  between documents by ID, only when you ask for it (`ADR-handbook-first-book-on-request`,
  `ADR-handbook-staleness-from-version`).
- **Proposals** and **Specs**: `docs/proposals/PROP-*/proposal.md` and the bundles under `specs/`, with their files,
  filters and task progress.
- **로드맵**: the milestones under `docs/roadmap/`, ordered active then planned, with readiness from `depends_on`
  (`done` and `dropped` appear with the history toggle).
- **파일 탐색**: the working tree, rendering Markdown, frontmatter and Mermaid.

The viewer shows the saved files of the registered working tree, including uncommitted and untracked ones, on the
branch currently checked out (`ADR-viewer-working-tree`). It never switches branches. Documents are parsed in the
browser, so repositories that pin different devkit-spec versions all render, and a document with malformed
frontmatter is listed as unreadable while the rest still show.

### Freshness

Results are cached for 30 seconds per repository and branch. Use the dashboard's Refresh button to reload at once,
or reload the browser page. There is no file watching.

## Proposals still under Planning

A proposal under Planning is edited on its own `plan-<slug>` branch, so the base checkout may hold an older copy. The
Dashboard proposal section and the Proposals tab overlay the Planning version, read from local sources only, in this
order (`ADR-viewer-planning-proposal-overlay`):

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

## Sources

- [CAP-VIEW-repository-viewer](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/viewer/CAP-VIEW-repository-viewer.md):
  serving, endpoints, Planning sources, page behaviour, roadmap, library and the review page.
- [Viewer quick reference](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/development/reference/viewer.md).
- [ADR-viewer-working-tree](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261024-viewer-working-tree.md),
  [ADR-viewer-planning-proposal-overlay](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261026-viewer-planning-proposal-overlay.md),
  [ADR-handbook-first-book-on-request](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261026-handbook-first-book-on-request.md),
  [ADR-handbook-staleness-from-version](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/decisions/2026-10/20261026-handbook-staleness-from-version.md).
