---
sources:
  CAP-DOCS-document-lookup: f16d8d88730261a376acc66ccb8e11ce209d4b49
  CAP-DOCS-document-model: 89280a2bb6003fe052fa7ee3ed50e368270bf9c6
  CAP-DOCS-document-search: 60fc2aff10caad2a5b56dc61ad347369aafa2634
  CAP-DOCS-namespaces: ee66025d062f5c547b58bd25964db7bef2f8c39e
  UC-find-the-right-documents: fbfaa41c0802e14b1f363c666a5b4de450716895
title: Find the right documents
---

# Find the right documents

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `18b834c35c0c`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](adopt-sdd-from-incubation.md)
- [Drive development to integration](drive-development-to-integration.md)
- [Handle delivery problems and exceptions](handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](incubate-an-idea.md)
- [Incubate and hand off a proposal](incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](keep-the-living-spec-consistent.md)
- [Publish a weekly report](publish-a-weekly-report.md)
- [Reconcile Living Spec drift](reconcile-living-spec-drift.md)
- [Resolve stale activity branches](resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](review-and-refactor-accumulated-slop.md)
- [Route a development request](route-development-intent.md)
- [Run parallel work safely](run-parallel-work-safely.md)
- [Speed up selected slow operations](speed-up-selected-slow-operations.md)
- [Advisories](../areas/advisory.md)
- [Agent-first CLI toolkit](../areas/cli.md)
- [Collaboration](../areas/collaboration.md)
- [Compact command output](../areas/compact.md)
- [Delivery](../areas/delivery.md)
- [Distribution](../areas/distribution.md)
- [Documents](../areas/documents.md)
- [Commit gates](../areas/gate.md)
- [Generated Files](../areas/generated.md)
- [Governance rules](../areas/governance.md)
- [Harness](../areas/harness.md)
- [Host](../areas/host.md)
- [Integration](../areas/integration.md)
- [MCP](../areas/mcp.md)
- [Search](../areas/search.md)
- [Traceability](../areas/traceability.md)
- [Viewer](../areas/viewer.md)
- [Worktree](../areas/worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Before an agent changes code, it needs the contracts that govern that code: the capabilities, use cases, decisions
and specs. Reading the whole `docs/` tree wastes context. Instead, the agent starts from whatever handle it holds and
asks `devkit docs` for exactly the documents that matter. Everything on this page only reads; no command changes a
file.

The use case is
[`UC-find-the-right-documents`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/documents/UC-find-the-right-documents.md).
For what a document, an ID and the Living Spec are, see [Concepts](../concepts.md) and the
[Documents](../areas/documents.md) area.

## Pick your starting point

| You hold | Start with |
| --- | --- |
| An ID quoted in a task or review | `devkit docs resolve <ID>` |
| A code path you are about to change | `devkit docs list capability --file <path>` |
| Only a description of the intent | `devkit docs search "<intent>"` |
| Nothing yet, inside one package of a monorepo | `devkit docs list` |

## 1. Resolve an ID

```bash
uv run devkit docs resolve CAP-DOCS-document-model
```

You get one `[DOCUMENT: <id> kind= status= path=]` line with the workspace-relative path. An alias resolves to its
canonical document and the line says `alias=`. You can pass several IDs at once. How IDs and kinds are defined is in
[`CAP-DOCS-document-model`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-model.md).

## 2. Follow the references

```bash
uv run devkit docs refs CAP-DOCS-document-model --direction in   # who cites it
uv run devkit docs refs CAP-DOCS-document-model                  # what it cites
```

Each `[REF: ...]` line names a document on the other side and the fields that hold the reference. Results come one
page at a time: a `[PAGE: ...]` line follows, and `[NEXT_CMD: ...]` gives the exact command for the next page
([`CAP-DOCS-document-lookup`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-lookup.md)).

## 3. Read and cite

Read the documents you need, change the code against them, and cite each by its exact ID in code spans, such as
`CAP-DOCS-document-model`.

## Other ways in

**By meaning.** When you only know the intent:

```bash
uv run devkit docs search "keep references between documents valid"
```

The ranking uses each document's ID and English summary, plus the title, area and body lexically, so it works even
when bodies are written in another language. A query that equals an ID, alias, path or file name puts that document
first with `score=-`. With the optional search extra (`uv add 'devkit-docs[search]'`, which `devkit-spec[search]`
includes) the ranking is hybrid; without it, lexical
([`CAP-DOCS-document-search`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-document-search.md)).
Continue at step 2 with the hit you choose.

**By code path.** `uv run devkit docs list capability --file src/<package>/engine.py` lists documents whose
`entrypoints` equal, contain or lie under the path. It works for a deleted file too.

**Inside a monorepo package.** When a monorepo registers packages as namespaces (`[[tool.docs.namespaces]]` in
`.devkit/config.toml`), `devkit docs list` and
`devkit docs search` show the current directory's namespace plus the global documents, each line with `namespace=`.
`--namespace <name>` picks another one and `--all-namespaces` shows all. A namespace narrows browsing only:
`resolve` and `refs` stay repository-wide, so an ID from another package still resolves
([`CAP-DOCS-namespaces`](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/documents/CAP-DOCS-namespaces.md)).

## History stays out unless you ask

Completed spec bundles, done or dropped milestones and documents in a terminal status are history. `list` and `search`
leave them out by default. `list` tells you how many it hid (`hidden=` on the page line) and prints a
`[HISTORY_CMD: ...]` line with the same command plus `--history`.

## When it goes wrong

| Code | Meaning | What to do |
| --- | --- | --- |
| `DOCS_ID_UNRESOLVED` | No document declares the ID. The IDs that did resolve are printed first. | Search by meaning instead. |
| `DOCS_ID_DUPLICATE` | Several documents declare the ID; `[TARGET]` lists them. | Fix the duplicate by hand; nothing guesses which one is right. |
| `DOCS_ENTRYPOINTS_PATH_INVALID` | The `--file` path is absolute, a glob, or contains `..`. | Pass a workspace-relative path. |
| `ARGUMENT_INVALID` | An unknown `--namespace`, or `--namespace` combined with `--all-namespaces`. | Use one of the valid names the error lists. |
| `DOCS_CONFIG_INVALID` | The `[tool.docs]` namespace table is malformed. | Correct the table in `.devkit/config.toml`. |
| `DOCS_DOCUMENT_INVALID` (warning) | One file cannot be read or has malformed frontmatter. | It is left out; every other document stays usable. Fix the file. |

All of these exit `2`, except the warning, which exits `0`. Branch on the code, not on the message text.

## Related

- [Search](../areas/search.md) area for the ranking engine underneath.
- [Drive development to integration](drive-development-to-integration.md), where these lookups feed the work.
