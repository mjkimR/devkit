---
id: FB-spec-readme-and-mcp-guide-native-handoff
title: The devkit-spec README and MCP install guide describe a native handoff runtime
scope: repo
kind: change-request
category: docs-mismatch
target: packages/devkit-spec/README.md, guides/install/mcp.md
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-spec-readme-and-mcp-guide-native-handoff] The devkit-spec README and MCP install guide describe a native handoff runtime

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: the devkit-spec README lists `devkit-mcp` as "the native handoff runtime" and mentions
  "native handoff/acceptance tools"; `guides/install/mcp.md` says installing `devkit-spec` includes `devkit-mcp` for
  source-bound proposal report publication. devkit-spec depends only on `devkit-core`, `click` and `devkit-agt`
  (`devkit-mcp` is the `mcp` extra of `devkit-agt`), and acceptance and handoff run through the Host-authorized
  `devkit spec proposal` CLI (`ADR-host-cli-lifecycle-authority`, `ARCH-05-1-containers`).
- **Proposed Procedure**: correct both mirrors to the CLI route and the real dependencies, keeping the guide's
  install commands in step with `docs/`.
- **Expected Benefit**: an agent following the install guide does not expect `devkit-mcp` from `devkit-spec` or
  native handoff tools that are not registered.
- **Cost & Risk**: a few lines in a README and a guide; no behavior.
- **Attempted**: not edited: package READMEs and `guides/` are outside the write scope of
  `SPEC-living-spec-consistency-sweep`, whose reconcile review found them (`reconcile-check-01.yaml`, finding 1).

## Diagnostic Details

- **Reproduction**: `rg -n "native handoff|includes .devkit-mcp" packages/devkit-spec/README.md guides/install/mcp.md`.
- **Expected / Actual**: CLI lifecycle and no `devkit-mcp` dependency / native runtime and an implied dependency.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-DLV-proposal-planning`, `ARCH-05-1-containers`.

## Evidence

```text
packages/devkit-spec/README.md:13-14 devkit-mcp (the native handoff runtime); :78 native handoff/acceptance tools
guides/install/mcp.md:3 Installing devkit-spec includes devkit-mcp for source-bound proposal report publication
packages/devkit-spec/pyproject.toml dependencies: devkit-core, click, devkit-agt
```

## Disposition

Resolved by `SPEC-feedback-guidance-and-scope` (item 5): `packages/devkit-spec/README.md` and `guides/install/mcp.md` no longer claim a native handoff runtime, a `devkit-mcp` dependency of devkit-spec or a devkit-spec MCP service; acceptance and handoff run through the `devkit spec proposal` CLI and `devkit-mcp` (via `devkit-agt[mcp]`) serves devkit-dist's shared artifact tools. Verified by the code review (`review-01`, `reverify-01`) against `pyproject.toml` and the registered `devkit.host.services` entry points.
