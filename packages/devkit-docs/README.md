# devkit-docs

The devkit document system for AI coding agents, built on [devkit](../../README.md). One Python package ships:

- the document model: kinds, IDs, frontmatter, references, aliases, namespaces and the document index;
- the `devkit docs` command group (`devkit.commands`): `resolve`, `refs`, `list` and `search`;
- the auto-selected `docs` bundle and its document rules (`document-reference`, `id-convention`, `spec-format`,
  `traceability-link`, `document-summary`, `steering-documents`, `ux-links`, `ux-coverage`, `code-entrypoints`);
- the `[tool.docs]` settings (document namespaces) and their config template.

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
