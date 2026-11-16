# devkit-docs

The devkit document system for AI coding agents, built on [devkit](../../README.md). One Python package ships:

- the document model: kinds, IDs, frontmatter, references, aliases, namespaces and the document index;
- the `devkit docs` command group (`devkit.commands`): `resolve`, `refs`, `list` and `search`;
- the auto-selected `docs` bundle and its document rules (`document-reference`, `id-convention`, `spec-format`,
  `traceability-link`, `document-summary`, `steering-documents`, `ux-links`, `ux-coverage`, `code-entrypoints`);
- the `[tool.docs]` settings (document namespaces) and their config template;
- the `devkit.context_documents` provider (`features/documents/services/context_documents.py`): `devkit get-context`
  lists a registered namespace's mirror of a `docs/`-rooted context directory (`docs/packages/<name>/steering/`)
  when the working directory lies in that package, and names the other namespaces' under `documents_elsewhere`.

It knows no delivery process. devkit-spec builds on it and adds proposals, spec bundles, workflows and the
lifecycle rules; it registers how `devkit docs list` shows proposals under Planning through the
`devkit.docs.status_overlay` entry point. Contracts start at `CAP-DOCS-document-model`; repository documentation
starts at [docs/README.md](../../docs/README.md).

## Use in a project

devkit-spec depends on devkit-docs, so installing devkit-spec installs it. To use it on its own:

```bash
uv add --dev "devkit-docs @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-docs"
uv run devkit sync            # deploy docs:core without SDD lifecycle assets
uv run devkit add docs:docs-skeleton  # optional absent document scaffolds
uv run devkit docs --version   # [VERSION: devkit-docs <version>]
uv run devkit docs list        # the current Living Spec documents
```

The `search` extra enables dense and hybrid `devkit docs search` (devkit's embedding runtime).

## Modules

- `features/documents/`: the document model (`models/`), the index and its memo (`repositories/`), namespaces,
  references and dependencies (`services/`), browsing and search (`usecases/`) and the commands (`cli/`).
- `features/governance/`: the document rules' implementations and the services they share.
- `base/`: the `DOCS_` errors and the document layout vocabulary.

The docs context owns shared writing instructions, steering discovery and templates. Run
`uv run devkit get-context docs` before document work. Installing devkit-spec additionally selects its lifecycle
assets. `uv run devkit remove spec` removes selected assets, not installed Python command extensions.
A clean document-only runtime installs devkit-docs without devkit-spec.

A milestone lives at one roadmap root, global `docs/roadmap/` or a registered namespace's `docs/packages/<name>/roadmap/`: planned/active at the root and done/dropped in that root's flat `_archive/`.
The same IDs and aliases resolve in either location; history visibility remains status-derived.
Document rules report invalid placement without moving files or changing lifecycle status.

## Formal role documents

Kind.DESIGN (`design`, DESIGN), Kind.DOMAIN (`domain`, DOMAIN) and Kind.OPERATIONS (`operations`, OPS) append to
existing public Kind values. In global or registered package docs roots, write a designs/AREA/DESIGN-slug/design.md
bundle, domain/AREA/DOMAIN-slug.md or flat operations/OPS-slug.md with id, title, status and a double-quoted English
summary (plus `area` matching the area directory for a design or domain document), then
`# [ID] title`. Status is draft, active or retired; history browsing exposes retired nodes while resolve/refs still work.
Optional typed related_designs, related_domains and related_operations lists work on every indexed kind. Same-prefix
aliases retain identity; no reciprocal role links are required. Existing Document/Reference JSON keys stay unchanged.

Use the shipped design/domain/operations templates and writing instructions. Independent Markdown detail has its
own formal ID (a peer bundle for a design); ID-free parent-owned support belongs in the design bundle, or under
PARENT-ID/artifacts/ beside a domain or operations document, and supporting Markdown names its parent. Rename, area
and root moves carry support and repair ordinary links. Only DESIGN accepts optional safe existing
workspace-relative entrypoints for source reading and reverse --file lookup; DOMAIN/OPS use body links instead.
The docs core bundle ships eleven instructions, eight formal templates and the reference page template.
