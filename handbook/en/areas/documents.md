---
sources:
  ADR-document-id-aliases: 3e599afa8857afa9256843680e8ed264f56faa6b
  ADR-document-package: 0160b060aa43c940edb5c3af25f4b96a4444698e
  ADR-steering-documents-directory: f37962558ebd8e15985df6f217330c322b389e97
  ADR-terminal-statuses-are-historical: 5883cd244a53a90dc71cc9dc9c6520ef7cc97093
  CAP-DOCS-document-lookup: f16d8d88730261a376acc66ccb8e11ce209d4b49
  CAP-DOCS-document-model: 89280a2bb6003fe052fa7ee3ed50e368270bf9c6
  CAP-DOCS-document-search: 60fc2aff10caad2a5b56dc61ad347369aafa2634
  CAP-DOCS-namespaces: ee66025d062f5c547b58bd25964db7bef2f8c39e
  UC-find-the-right-documents: fbfaa41c0802e14b1f363c666a5b4de450716895
  UC-keep-the-living-spec-consistent: 6aa78b77ed1eb5a1f7f8b59742048c01319abccc
title: Documents
---

# Documents

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The documents area is how devkit knows what a Living Spec document is and how you find one. It is owned by the
`devkit-docs` package (`ADR-document-package`), which works without the spec-driven delivery package `devkit-spec`.
Every capability, use case, UX document, decision, proposal, spec and feedback record is a Markdown file with an ID
in its frontmatter. devkit builds an index of them on every call and gives you four commands over it:
`devkit docs resolve`, `refs`, `list` and `search`.
The Living Spec itself is introduced in [Concepts](../concepts.md); the end-to-end task of finding the documents
for a change is the journey [Find the right documents](../journeys/find-the-right-documents.md)
(`UC-find-the-right-documents`).

## What counts as a document

A file is a document when all of these hold
([CAP-DOCS-document-model](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md)):

- it is a `*.md` file under `docs/` or `specs/`, not a `README.md`, a template, a symlink or under a dot directory;
- its frontmatter declares a well-formed ID in `id` (or `reconcile_id` for a reconcile record).

Files without an ID, such as a glossary or a guide, are silently left out. A file with broken frontmatter is left
out with a `DOCS_DOCUMENT_INVALID` warning, and every other document stays usable.

The ID prefix names the kind: `CAP` capability, `UC` use case, `UX` UX document (a screen, modal or panel under
`docs/ux/<area>/`), `ARCH` architecture, `ADR` decision, `PROP` proposal, `PADR` proposal decision,
`SPEC`/`PLAN`/`TASKS`/`REC` spec bundle files, `FB` feedback, `MAT` material and `MS` milestone. IDs are unique
across the whole repository. The index accepts an ID wherever it is declared; the document rules check that each
file lives where its kind belongs. Planned and active milestones live in `docs/roadmap/`, done and dropped ones in
its flat `docs/roadmap/_archive/` with the same file name and ID.

Write a one- or two-sentence English `summary` on capabilities, use cases, UX documents, decisions, architecture
documents, milestones, proposals and specs. It is the main signal of search, so titles and bodies can be in any
language.

### Steering documents

`docs/steering/` holds project-wide background that is neither a contract nor evidence, such as the glossary
(`ADR-steering-documents-directory`). Each file has only `title` and `summary` frontmatter and no ID, so it is not
a document and not a search candidate. `devkit get-context docs` lists every steering file's title and summary, so
an agent reads one only when it concerns the work; the document rules bound the directory and check the IDs it cites.

## Reference other documents

- Always reference a document by its full ID, never by a Markdown path: in frontmatter relation fields (`usecases`,
  `capabilities`, `spec`, `plan` and similar) or in prose as a single code span holding exactly one ID.
- Code blocks, link labels, HTML comments and other inline code are not references.
- `proposal`, `decomposed_from` and `supersedes` record provenance and are kept out of the reference graph.
- Reference validity (unresolved, duplicated, wrong kind) is reported by the document rules, not by the index; see
  [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
  (`UC-keep-the-living-spec-consistent`).

### Rename a document

Move the file, set the new ID and keep the old ID in `aliases`. An alias resolves to its document everywhere an ID
argument is accepted, and `uv run devkit rules fix` then rewrites current references to the new ID
(`ADR-document-id-aliases`). An alias that two documents claim collides and is reported on both.

## Look up what you already know

| You have | Command |
| --- | --- |
| an ID (or an alias) | `uv run devkit docs resolve CAP-DOCS-document-model` |
| a document, and you want what it references | `uv run devkit docs refs <ID>` |
| a document, and you want what references it | `uv run devkit docs refs <ID> --direction in` |
| a code path | `uv run devkit docs list capability --file src/engine/` |
| a kind, status or area to browse | `uv run devkit docs list usecase --status active --area core` |
| a frontmatter field value | `uv run devkit docs list feedback --where severity=critical -n 0` |

`resolve` prints one `[DOCUMENT: ...]` line per ID and exits `2` with `DOCS_ID_UNRESOLVED` or `DOCS_ID_DUPLICATE`
for the ones it cannot settle. `refs` and `list` page their output: follow the `[NEXT_CMD: ...]` line for the next
page. Every command accepts `--format json`. Options, line fields and JSON keys are in
[CAP-DOCS-document-lookup](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-lookup.md).

### History is hidden by default

Browsing and search hide historical documents unless you pass `--history`: the files of a completed spec bundle
(its feedback aside), done or dropped milestones, and documents in a terminal status (feedback `resolved`,
`promoted`, `dismissed` or `forwarded`; decision `superseded`; proposal `rejected`;
`ADR-terminal-statuses-are-historical`). `list` reports how many it hid and prints a `[HISTORY_CMD: ...]` line to see
them. Naming a status with `--status` shows those documents too. Historical IDs always stay resolvable.

### Status shown by installed packages

Other packages can add display-only status to `list` through a status overlay. With devkit-spec installed, a draft
proposal whose `plan-<slug>` branch exists is listed as `status=reviewing` with its `planning_branch`, and
`--status reviewing` selects it. The file itself is not changed, and `resolve`, `refs`, `search` and the rules keep
reading the declared status. An overlay that fails is left out with a `DOCS_OVERLAY_FAILED` warning.

## Search when you only know the intent

```bash
uv run devkit docs search "link integrity between documents"
uv run devkit docs search "cache policy" --kind decision --kind capability --history
```

A query that equals a document's ID, alias, path or file name pins that document first. The other hits are ranked
by the ID and English summary (lexically and by meaning) and by title, area and body (lexically). An optional,
project-owned `docs/steering/glossary.yaml` expands query terms with synonyms, useful for terms in another language.
Without the search extra the ranking is lexical; install it with `uv add 'devkit-docs[search]'` (included in
`devkit-spec[search]`) for hybrid ranking. Details
are in [CAP-DOCS-document-search](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-search.md);
the ranking engine itself is described in [Search](search.md).

## Work in a monorepo with namespaces

Register each package in `.devkit/config.toml`, and give it its own Living Spec under `docs/packages/<name>/` with
the same layout as `docs/`:

```toml
[[tool.docs.namespaces]]
name = "api"
path = "services/api"
```

The `[tool.docs]` table holds only `namespaces`; a malformed table fails every command that reads it, and a rules
run, with `DOCS_CONFIG_INVALID`.

A namespace narrows what you *browse*, never what exists
([CAP-DOCS-namespaces](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-namespaces.md)):

- `list` and `search` show the current directory's namespace plus the global documents by default;
  `--namespace NAME` picks one, `--namespace global` only global documents, `--all-namespaces` everything.
- `resolve`, `refs` and the reference rules ignore namespaces: IDs stay repository-wide and references cross
  packages freely. Use `--all-namespaces` to see cross-package impact.
- A spec or proposal bundle belongs to the namespace in its `namespace` field, which `devkit spec new --namespace`
  and `devkit spec proposal new --namespace` write.

## Capabilities in this area

| Capability | Read it when you need |
| --- | --- |
| `CAP-DOCS-document-model` | what a document is, IDs, references, aliases, the index and its parse memo |
| `CAP-DOCS-document-lookup` | `resolve`, `refs` and `list`: options, output, codes |
| `CAP-DOCS-document-search` | `devkit docs search`: candidates, pinning, glossary, modes |
| `CAP-DOCS-namespaces` | monorepo namespaces and their selection |
