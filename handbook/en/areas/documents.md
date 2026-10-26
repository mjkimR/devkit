---
sources:
  ADR-document-id-aliases: 3e599afa8857afa9256843680e8ed264f56faa6b
  ADR-terminal-statuses-are-historical: 5883cd244a53a90dc71cc9dc9c6520ef7cc97093
  CAP-DOCS-document-lookup: d908536d3cc6b3c3676c21f0858e5fd4d416cca6
  CAP-DOCS-document-model: 65a68b9b0c43ddbcd7817e14d278f31c640a221a
  CAP-DOCS-document-search: b1fd38fddef38d5c97d094208acf6b5077e6f3f4
  CAP-DOCS-namespaces: dc29338809464bb54d620053a83f59245fc8cbef
  UC-find-the-right-documents: 722935d391e97c4a537ebe9d3950228b540dc591
  UC-keep-the-living-spec-consistent: 7ebdf1e2f7ae6581fa9140d1898d755de57b5667
title: Documents
---

# Documents

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

The documents area is how devkit-spec knows what a Living Spec document is and how you find one. Every capability,
use case, decision, proposal, spec and feedback record is a Markdown file with an ID in its frontmatter. devkit
builds an index of them on every call and gives you four commands over it: `resolve`, `refs`, `list` and `search`.
The Living Spec itself is introduced in [Concepts](../concepts.md); the end-to-end task of finding the documents
for a change is the journey [Find the right documents](../journeys/find-the-right-documents.md)
(`UC-find-the-right-documents`).

## What counts as a document

A file is a document when all of these hold
([CAP-DOCS-document-model](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-model.md)):

- it is a `*.md` file under `docs/` or `specs/`, not a `README.md`, a template, a symlink or under a dot directory;
- its frontmatter declares a well-formed ID in `id` (or `reconcile_id` for a reconcile record).

Files without an ID, such as a glossary or a guide, are silently left out. A file with broken frontmatter is left
out with a `SPEC_DOCUMENT_INVALID` warning, and every other document stays usable.

The ID prefix names the kind: `CAP` capability, `UC` use case, `ARCH` architecture, `ADR` decision, `PROP`
proposal, `PADR` proposal decision, `SPEC`/`PLAN`/`TASKS`/`REC` spec bundle files, `FB` feedback, `MAT` material and
`MS` milestone. IDs are unique across the whole repository. The index accepts an ID wherever it is declared; the
spec rules check that each file lives where its kind belongs.

Write a one- or two-sentence English `summary` on capabilities, use cases, decisions, architecture documents,
milestones, proposals and specs. It is the main signal of search, so titles and bodies can be in any language.

## Reference other documents

- Always reference a document by its full ID, never by a Markdown path: in frontmatter relation fields (`usecases`,
  `capabilities`, `spec`, `plan` and similar) or in prose as a single code span holding exactly one ID.
- Code blocks, link labels, HTML comments and other inline code are not references.
- `proposal`, `decomposed_from` and `supersedes` record provenance and are kept out of the reference graph.
- Reference validity (unresolved, duplicated, wrong kind) is reported by the spec rules, not by the index; see
  [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
  (`UC-keep-the-living-spec-consistent`).

### Rename a document

Move the file, set the new ID and keep the old ID in `aliases`. An alias resolves to its document everywhere an ID
argument is accepted, and `uv run devkit rules fix` then rewrites current references to the new ID
(`ADR-document-id-aliases`). An alias that two documents claim collides and is reported on both.

## Look up what you already know

| You have | Command |
| --- | --- |
| an ID (or an alias) | `uv run devkit spec resolve CAP-DOCS-document-model` |
| a document, and you want what it references | `uv run devkit spec refs <ID>` |
| a document, and you want what references it | `uv run devkit spec refs <ID> --direction in` |
| a code path | `uv run devkit spec list capability --file src/engine/` |
| a kind, status or area to browse | `uv run devkit spec list usecase --status active --area core` |
| a frontmatter field value | `uv run devkit spec list feedback --where severity=critical -n 0` |

`resolve` prints one `[DOCUMENT: ...]` line per ID and exits `2` with `SPEC_ID_UNRESOLVED` or `SPEC_ID_DUPLICATE`
for the ones it cannot settle. `refs` and `list` page their output: follow the `[NEXT_CMD: ...]` line for the next
page. Every command accepts `--format json`. Options, line fields and JSON keys are in
[CAP-DOCS-document-lookup](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-lookup.md).

### History is hidden by default

Browsing and search hide historical documents unless you pass `--history`: the files of a completed spec bundle
(its feedback aside), done or dropped milestones, and documents in a terminal status (feedback `resolved`,
`promoted`, `dismissed` or `forwarded`; decision `superseded`; proposal `rejected`;
`ADR-terminal-statuses-are-historical`). `list` reports how many it hid and prints a `[HISTORY_CMD: ...]` line to see
them. Naming a status with `--status` shows those documents too. Historical IDs always stay resolvable.

## Search when you only know the intent

```bash
uv run devkit spec search "link integrity between documents"
uv run devkit spec search "cache policy" --kind decision --kind capability --history
```

A query that equals a document's ID, alias, path or file name pins that document first. The other hits are ranked
by the ID and English summary (lexically and by meaning) and by title, area and body (lexically). An optional,
project-owned `docs/glossary.yaml` expands query terms with synonyms, useful for terms in another language. Without
the search extra the ranking is lexical; install it with `uv add 'devkit-spec[search]'` for hybrid ranking. Details
are in [CAP-DOCS-document-search](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-document-search.md);
the ranking engine itself is described in [Search](search.md).

## Work in a monorepo with namespaces

Register each package in `.devkit/config.toml`, and give it its own Living Spec under `docs/packages/<name>/` with
the same layout as `docs/`:

```toml
[[tool.spec.namespaces]]
name = "api"
path = "services/api"
```

A namespace narrows what you *browse*, never what exists
([CAP-DOCS-namespaces](https://github.com/mjkimR/devkit/blob/v0.1.4/docs/capabilities/documents/CAP-DOCS-namespaces.md)):

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
| `CAP-DOCS-document-search` | `devkit spec search`: candidates, pinning, glossary, modes |
| `CAP-DOCS-namespaces` | monorepo namespaces and their selection |
