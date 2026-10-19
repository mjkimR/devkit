---
id: PROP-repository-viewer
title: Local multi-repository SDD viewer owned by devkit
summary: "Moves the autohub SDD repository viewer into devkit as its source owner, adds a roadmap view for milestone documents, and packages it with a local server that serves several repositories at once; the viewer stays read-only and grants no approvals."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-19
target_area: capabilities/viewer/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
boundaries:
  owns:
    - capabilities/viewer/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-repository-viewer] Local multi-repository SDD viewer owned by devkit

- **Origin**: proposals and milestones are now both repository documents (`ADR-roadmap-in-repository`,
  `ADR-milestone-documents`), and `ADR-roadmap-in-repository` names the cost: "no human-facing roadmap screen until a viewer renders it".
- **Source owner (decided in Backlog)**: devkit owns the viewer source; autohub consumes it as a vendored tarball (Q1).
- **Related**: `CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`, `CAP-DLV-proposal-incubation`,
  `CAP-DLV-human-interaction`, `CAP-INT-mcp-services`, `ARCH-08-1-agent-output`.

## 1. Background & Hypothesis

### 1.1 Problem

- **No screen for the plan.** Living Spec, proposals, specs and now milestones (`docs/roadmap/MS-*.md`) are files.
  An agent reads them through `devkit spec list`, `resolve` and `refs`; a person has no view of them outside autohub,
  and autohub requires a GitHub-connected project.
- **The viewer that exists lives in autohub.** `modules/hub-ui/src/lib/features/project-management/repositories/`
  holds a native Svelte viewer for `sdd` projects: `sdd/SddViewer.svelte` (1502 lines), `sdd/KnowledgeViews.svelte`
  (636), `sdd/documents.ts` (273) and `sdd/repository.ts` (53), about 2.5k lines. It depends on `marked`, `yaml`,
  `dompurify` and a lazily imported `mermaid`. Data access already goes through a `RepositoryDataSource` interface
  (`info`, `tree(path, ref)`, `blob(path, ref)`), and `httpDataSource(base)` exists beside autohub's own data source.
- **It does not know milestones.** The viewer shows the `milestone` frontmatter field as a badge only; there is no
  list of `MS-` documents, their status, their `depends_on` order or their members.
- **Base-only reads hide work in progress.** autohub reads through the GitHub API at a ref, and
  `ADR-milestone-documents` records that the base shows only merged state while Units in progress live on `plan-` and
  `dev-` branches.
- **One repository per view.** A workspace such as workbench holds many devkit repositories; a person wants one
  local place to read all of them.

### 1.2 Hypothesis

A viewer whose source devkit owns, packaged with a small local server that reads several registered repositories
through Git at any ref, gives people a screen for the Living Spec, proposals, specs and the roadmap without autohub or
network access, while autohub keeps its features by consuming the same viewer with its own data source. Keeping the
viewer read-only leaves every approval on its existing single path.

## 2. Technical Spike Questions

Answered in Planning; the decisions are `PADR-viewer-distribution-and-frontend-build` (Q1 to Q3) and
`PADR-read-only-local-server-over-git-refs` (Q4 to Q8).

- **Q1. Packaging for autohub.** No registry publication (decided in Backlog). autohub commits the `npm pack` tarball
  of devkit's viewer library, built from a pinned devkit commit, under `modules/hub-ui/vendor/` and depends on it with
  `file:vendor/<name>.tgz`, as it already does for app-common's `api-codegen` (`vendor/api-codegen.md`); npm Git
  dependencies install only a repository's root package. One frontend source yields both the component library and
  devkit's own app. What autohub removed in `0d8c05f` was runtime loading of an externally hosted Custom Element
  bundle (an HTTPS URL and SHA-256 in a Git-ignored local file, downloaded at deployment build time, published
  separately); a vendored library compiled into autohub's build brings none of it back.
- **Q2. Package and command.** A separate `devkit-viewer` distribution mounted through `devkit.commands` as
  `devkit viewer serve`, so only those who run it install its assets; it needs no `devkit-spec` code. stdout carries
  one `[VIEWER: url=... repos=...]` sentinel. The server is the standard library's `http.server`.
- **Q3. Node toolchain.** The frontend lives in `packages/devkit-viewer/frontend/`. Its built app is committed and
  registered as a tracked generated artifact (`CAP-GEN-tracked-artifacts`), so installing devkit from Git never
  needs Node; the `just` recipes gain frontend lint, type check and tests through `scripts/`, and `just smoke` checks
  the installed wheel serves its assets.
- **Q4. Registration.** `--repo PATH` (repeatable) and `--scan DIR` (direct children that are Git repositories with
  `.devkit/config.toml`). The ID is the directory name; duplicates are refused. workbench's `config/repos.txt` names
  clone targets, not checkouts, so it is not read.
- **Q5. Reading through Git.** `git ls-tree` and `git cat-file` at a ref; a new optional `refs` member of
  `RepositoryDataSource` lists local branches. The uncommitted working tree is not shown (a possible follow-up);
  nothing is fetched.
- **Q6. Version drift.** The browser parses the documents; unknown kinds and fields render as plain documents.
- **Q7. Roadmap view.** Milestones by status (history behind a toggle), `depends_on` order and readiness, and members
  on the default branch and, through `refs`, on local `plan-` and `dev-` branches, read on demand.
- **Q8. Safety.** Loopback only, a `Host` header check against DNS rebinding, no CORS headers, GET only; no token.

## 3. Proposed Design & Impact

- **Move**: the read-only viewer (`SddViewer`, `KnowledgeViews`, `documents.ts`, the `RepositoryDataSource`
  interface) becomes a Svelte component library in devkit. autohub keeps `RepositoryView`, its Git browser
  (`FileTreeTable`, `FileBlobViewer`, which use its shadcn components) and its run and decision panels
  (`SddExecution`, `SddProposals`, `SddRunLinks`, which call its execution API).
- **Add**: a roadmap view over `docs/roadmap/MS-*.md` (Q7) in the library, and a repository switcher in devkit's app.
- **Serve**: `devkit viewer serve` serves several registered repositories (Q4) through Git at a ref (Q5) and the
  committed app build (Q3).
- **autohub**: after a devkit commit carries the library, autohub replaces its copy with the vendored tarball and
  passes its existing GitHub-backed data source (Q1). That change belongs to autohub.
- **Approvals stay out** (`PADR-read-only-local-server-over-git-refs`):
  - Gate, handoff and question answers that are records (`CAP-DLV-human-interaction`) could be written by a web page
    under the contract, but the waiting agent would not see them until its next `devkit workflow next`, and the viewer
    would become a writing server with commit and token concerns.
  - The `integration_integrate` approval is bound to a request held in the memory of the stdio MCP process the host
    started (`CAP-INT-mcp-services`); a separate server cannot grant it without changing that approval path.
  - The viewer and the MCP server also differ in lifetime: one long-lived process for many repositories versus one
    process per host session.
- **Impact**: a new distribution `packages/devkit-viewer/` and its README; a new capability area
  `capabilities/viewer/`; `docs/development/reference/` gains the command; `AGENTS.md` and the README list the
  distribution; `.devkit/generated.toml` registers the assets; the layering test covers `devkit_viewer`;
  `ADR-roadmap-in-repository`'s "no human-facing roadmap screen" cost is met by the viewer.

### 3.1 Non-Goals

- **Scope Excluded**: recording approvals, gate decisions, handoff choices or question answers from the viewer, and
  any connection to the integration MCP tools.
- **Scope Excluded**: showing open workflow requests (`[REQUEST: ...]`); it needs each repository's own devkit to run
  and is a possible follow-up.
- **Scope Excluded**: editing documents, starting Planning or Development, or any other write from the viewer.
- **Scope Excluded**: showing uncommitted working tree content.
- **Scope Excluded**: remote hosting, authentication for several users, and GitHub API access in the devkit server.
- **Scope Excluded**: the autohub change that adopts the devkit-owned viewer (autohub's own work).

## 4. Lifecycle & Retirement Criteria

- On acceptance (plan-accept): record gate:plan-accept, set status: accepted and merge the Planning branch;
  Development starts with devkit spec proposal handoff repository-viewer.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
