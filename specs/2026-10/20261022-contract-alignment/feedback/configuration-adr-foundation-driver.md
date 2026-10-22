---
id: FB-configuration-adr-foundation-driver
title: A configuration ADR driver still names devkit-dist as the foundation owner
scope: repo
kind: friction
category: docs-mismatch
target: ADR-configuration-language-and-rendering
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-configuration-adr-foundation-driver] A configuration ADR driver still names devkit-dist as the foundation owner

## 1. Friction / Question (friction, question)

- **Context**: `SPEC-contract-alignment` superseded `ADR-dist-foundation-ownership` with
  `ADR-foundation-and-mcp-package-ownership` and repointed references that cite the current rule.
- **Expectation**: In-effect ADRs name the current foundation owner, or cite the decision of their time as history.
- **Actual**: A decision driver of `ADR-configuration-language-and-rendering` reads "The foundation belongs to
  devkit-dist and cannot import the harness, following `ADR-dist-foundation-ownership`." The foundation is
  `devkit-core`; what devkit-dist owns here is project configuration (its project feature).
- **Workaround (or Interpretation Chosen)**: Left unchanged: the unit's write scope allowed only link repair there, and
  repointing the citation alone would make the driver claim an owner the successor does not state.
- **Suggestion**: Reword the driver editorially to "Project configuration belongs to devkit-dist, which cannot import
  the harness (`ADR-foundation-and-mcp-package-ownership`)", under `ADR-immutable-decisions-editable-records`.

## Evidence

```text
docs/decisions/2026-10/20261022-configuration-language-and-rendering.md section 2:
"The foundation belongs to devkit-dist and cannot import the harness, following ADR-dist-foundation-ownership."
packages/devkit-core/pyproject.toml: name = "devkit-core", the shared foundation
```
