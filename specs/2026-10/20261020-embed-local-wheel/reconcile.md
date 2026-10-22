---
reconcile_id: REC-embed-local-wheel
status: resolved
targets:
  - file: docs/capabilities/search/CAP-SRCH-document-search.md
    resolution: modified
---

# Reconciliation

`CAP-SRCH-document-search` defines dense and hybrid retrieval ranking using `numpy`, `tokenizers`, and `devkit-embed` (AC-01–05). The capability documentation now accurately reflects that the prebuilt `devkit-embed` model wheel is committed directly in the repository under `models/devkit-embed/wheels/` and resolved via local path dependencies in `[tool.uv.sources]` of `packages/devkit-dist/pyproject.toml` and the root `pyproject.toml`.

This replaces the previous GitHub release asset download URL, ensuring that all `uv run` invocations, test suites, and sandboxed worktree environments execute completely offline without attempting remote DNS lookups or HTTP metadata revalidations.

The source observation `FB-planning-context-command-can-trigger-unavailable-sync` is marked resolved with disposition detailing the committed wheel resolution. No new domain term or architecture boundary is introduced. No requirements are deferred or waived.

