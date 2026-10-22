---
id: FB-package-ownership-adrs-lag-code
title: Package ownership ADR statements lag the package layout
scope: repo
kind: friction
category: docs-mismatch
target: ADR-dist-foundation-ownership; ADR-package-split-and-namespaces
skill: adr-compaction
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-package-ownership-adrs-lag-code] Package ownership ADR statements lag the package layout

## 1. Friction / Question (friction, question)

- **Context**: An ADR compaction run grouped the package split ADRs.
- **Expectation**: In-effect ADR statements match the package layout, or a later ADR records the change.
- **Actual**: `ADR-dist-foundation-ownership` says `devkit-dist` MUST own the shared foundation; `devkit-core` (`devkit_core`) owns it, and no ADR records the move. The retired module-split decision (now an alias of `ADR-package-split-and-namespaces`) declared a `devkit-dist` `mcp` extra; the code has `devkit-agt[mcp]` -> `devkit-mcp`, also without an ADR stating the change.
- **Workaround (or Interpretation Chosen)**: `ADR-dist-foundation-ownership` was left out of compaction; the `mcp` extra clause was not carried into `ADR-package-split-and-namespaces`.
- **Suggestion**: Record the foundation move to `devkit-core` and the `mcp` extra placement in an ADR that supersedes `ADR-dist-foundation-ownership`.

## Diagnostic Details

- **Reproduction**: Compare the ADR text with `packages/devkit-core/` and the `devkit-agt` extras.
- **Expected / Actual**: Recorded ownership; unrecorded changes.
- **Versions**: main at dd008f2b.
- **Conditions**: not applicable.
- **Workarounds Attempted**: Left out of compaction.
- **Related Assets**: `ADR-dist-foundation-ownership`, `ADR-package-split-and-namespaces`.

## Evidence

```text
ADR-dist-foundation-ownership: "devkit-dist MUST own the shared foundation"
packages/devkit-core/: devkit_core owns base/ and core/
```

- **Disposition (resolved)**: `SPEC-contract-alignment` added `ADR-foundation-and-mcp-package-ownership`, which
  supersedes `ADR-dist-foundation-ownership` (now `status: superseded`): `devkit-core` (`devkit_core`) owns the
  shared foundation, `devkit-agt` declares the `mcp` extra requiring `devkit-mcp` and `devkit-dist` declares none; the
  standalone-scope, executable and dependency-direction rules are carried over. Verified against the `pyproject.toml`
  files of the four wheels, `devkit rules check --ci` and the unit's review; `ARCH-05-1-containers` and
  `CAP-DIST-content-packages` cite the successor.
