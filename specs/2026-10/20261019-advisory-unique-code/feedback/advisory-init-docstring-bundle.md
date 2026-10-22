---
id: FB-advisory-init-docstring-bundle
title: devkit.advisory docstring says devkit reads a bundled guide from it
scope: repo
kind: friction
category: docs-mismatch
target: packages/devkit-advisory/src/devkit/advisory/__init__.py
origin: agent
severity: noise
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-advisory-init-docstring-bundle] devkit.advisory docstring says devkit reads a bundled guide from it

## 1. Friction / Question (friction, question)

- **Context**: Deciding whether a rule in the `advisory` bundle would enter the `devkit-advisory` runtime distribution.
- **Expectation**: The runtime module describes its own packaging accurately.
- **Actual**: The module docstring says devkit imports it "to read the bundled guide under `bundle/`", but
  `devkit-advisory` ships no `bundle/` and registers no bundle; the guide bundle is `devkit.advisory_guide` in
  `devkit-agt`, whose own docstring says so. A reader can conclude that bundle content (now including a rule) is part
  of the runtime.
- **Workaround (or Interpretation Chosen)**: Checked `packages/devkit-advisory/pyproject.toml` (no dependencies, no
  entry points) and the file tree, and relied on `devkit.advisory_guide`'s docstring.
- **Suggestion**: Drop the bundled-guide clause from the `devkit.advisory` docstring, keeping "standard library only
  and free of import-time side effects", or name `devkit.advisory_guide` as where the guides live.

## Diagnostic Details

- **Reproduction**: read `packages/devkit-advisory/src/devkit/advisory/__init__.py` lines 1-5 and list the package
  directory.
- **Expected / Actual**: no claim about a bundle / a claim about `bundle/` that the package does not contain.
- **Versions**: base commit `8fc64ef`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `packages/devkit/src/devkit/advisory_guide/__init__.py`, `docs/development/reference/advisory.md`.

## Evidence

```text
packages/devkit-advisory/src/devkit/advisory/__init__.py:
    Standard library only and free of import-time side effects: devkit imports this
    module to read the bundled guide under ``bundle/``.
packages/devkit-advisory/src/devkit/advisory/: __init__.py advisory.py error.py py.typed types.py (no bundle/)
packages/devkit/src/devkit/advisory_guide/__init__.py:
    The protocol's Python library is the separate ``devkit-advisory`` distribution (``devkit.advisory``), which
    registers no bundle, ...
```

- **Disposition**: packages/devkit-advisory/src/devkit/advisory/__init__.py: the docstring drops the bundled-guide clause and names `devkit.advisory_guide` as where the guides ship.
