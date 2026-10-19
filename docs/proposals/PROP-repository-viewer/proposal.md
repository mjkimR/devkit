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

- **Q1. Packaging for autohub.** Decided in Backlog: no registry publication. devkit's viewer is an npm package in
  a subdirectory; autohub commits its `npm pack` tarball built from a pinned devkit commit under
  `modules/hub-ui/vendor/` and depends on it with `file:vendor/<name>.tgz`, its integrity pinned by
  `package-lock.json`, with a note naming the source commit and rebuild steps. This is how autohub already consumes
  app-common's `api-codegen` (`vendor/api-codegen.md`); npm Git dependencies install only a repository's root
  package. Open: whether one Svelte component library covers both autohub and devkit's own server or the server
  needs a separate static build, and why autohub moved from dynamically loaded external viewer bundles (autohub
  `bfdef18`) to a native component (autohub `0d8c05f`), so the move does not reintroduce what that change removed.
- **Q2. Package and command.** Which distribution ships the server and the built assets: an extra of `devkit-spec`
  (which owns the proposal and milestone document kinds), a new distribution, or `devkit-catalog`? What is the
  command (working name `devkit spec view`), and how does its stdout stay within `ARCH-08-1-agent-output` (one
  `[KIND: ...]` sentinel with the URL, nothing else)? Which server stack keeps the runtime dependencies proportionate
  (standard library versus Starlette or similar)?
- **Q3. Node toolchain in this repository.** Building the SPA adds Node to a Python monorepo. Where does the frontend
  source live (`packages/<name>/frontend/` or similar), how do `just lint`, `just check`, `just test` and
  `just smoke` cover it, and is the built output committed, built at wheel time or published separately?
- **Q4. Multi-repository registration.** How are repositories registered: repeated `--repo` options, a user-level
  file, or reuse of an existing list (workbench `config/repos.txt`)? What is a repository's stable ID in URLs
  (`/api/repos/{id}/info|tree|blob?ref=`)?
- **Q5. Reading through Git.** Reads use `git ls-tree` and `git show <ref>:<path>` so no path outside a registered
  repository is reachable and any branch can be read. Does the viewer also offer the working tree (uncommitted
  edits), and how does it list `plan-` and `dev-` branches and registered worktrees for a milestone's members?
- **Q6. Parsing and version drift.** The viewer parses frontmatter in the browser, so the server never runs each
  repository's own devkit. Registered repositories may pin different `devkit-spec` versions; how does the viewer
  treat unknown kinds or fields (render as plain documents, never fail)?
- **Q7. Roadmap view.** What does the roadmap tab show: milestones by status, `depends_on` order and readiness,
  members per milestone (proposals and specs whose `milestone` names it, matching `refs --direction in`) with their
  settled state, across the base and Unit branches?
- **Q8. Local server safety.** Bind to `127.0.0.1` only; the server is read-only, so no write endpoint exists. Is a
  per-launch token still needed against other local pages reading repository content?

## 3. Proposed Design & Impact

A working direction for Planning to test:

- **Move**: bring the read-only parts (`SddViewer`, `KnowledgeViews`, `documents.ts`, `repository.ts`, and the file
  tree and blob views) into devkit. The autohub run and decision panels (`SddExecution`, `SddProposals`,
  `SddRunLinks`) stay in autohub, since they call autohub's execution API.
- **Add**: a roadmap tab over `docs/roadmap/MS-*.md` (Q7) and a repository switcher.
- **Serve**: one local process serves several registered repositories (Q4), reads through Git at a ref (Q5) and
  serves the built viewer assets (Q2, Q3).
- **autohub**: after this proposal, autohub replaces its copy with the devkit-owned viewer and passes its existing
  GitHub-backed data source (Q1). That change belongs to autohub and follows this package's release.
- **Approvals stay out.** The viewer neither records decisions nor talks to the integration MCP server:
  - Gate, handoff and question answers that are records (`CAP-DLV-human-interaction`) could be written by a web page
    under the contract, but the waiting agent would not see them until its next `devkit workflow next`, and the viewer
    would become a writing server with commit and token concerns.
  - The `integration_integrate` approval is bound to a request held in the memory of the stdio MCP process the host
    started (`CAP-INT-mcp-services`); a separate server cannot grant it without changing that approval path.
  - The viewer and the MCP server also differ in lifetime: one long-lived process for many repositories versus one
    process per host session.
- **Impact**: a new capability area `capabilities/viewer/`; `CAP-DLV-proposal-incubation` and
  `ADR-milestone-documents` gain a pointer to the viewer; the package README and `docs/development/reference/` gain
  the command; `AGENTS.md` lists the package if a new distribution is chosen (Q2).

### 3.1 Non-Goals

- **Scope Excluded**: recording approvals, gate decisions, handoff choices or question answers from the viewer, and
  any connection to the integration MCP tools.
- **Scope Excluded**: showing open workflow requests (`[REQUEST: ...]`); it needs each repository's own devkit to run
  and is a possible follow-up.
- **Scope Excluded**: editing documents, starting Planning or Development, or any other write from the viewer.
- **Scope Excluded**: remote hosting, authentication for several users, and GitHub API access in the devkit server.
- **Scope Excluded**: the autohub change that adopts the devkit-owned viewer (autohub's own work).

## 4. Lifecycle & Retirement Criteria

- On acceptance (plan-accept): record gate:plan-accept, set status: accepted and merge the Planning branch;
  Development starts with devkit spec proposal handoff repository-viewer.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
