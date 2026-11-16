---
id: FB-resolve-package-path-anchor
title: Clarify the root anchor of resolved document paths for package readers
scope: repo
kind: suggestion
category: other
target: devkit docs resolve --help
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-16
---

# [FB-resolve-package-path-anchor] Clarify the root anchor of resolved document paths for package readers

## 2. Suggestion / Change Request

The observation concerns path interpretation during package-local document navigation.

- **Current Procedure**: `devkit docs resolve` returns a workspace-relative document path. Its help says it prints document paths without explaining the root anchor.
- **Proposed Procedure**: State the workspace-root anchor in resolver help or its path contract so a package-local reader can open the returned path directly against the root.
- **Expected Benefit**: Avoid a failed read when the reader runs the resolver from a registered package source cwd.
- **Cost & Risk**: A wording clarification should preserve output paths and compatibility. Any output-format change needs separate scope and evidence.
- **Attempted**: A fresh D3 reader resolved the package owner, first read the returned path relative to package cwd and failed, then anchored it to the known fixture root and succeeded. The selected relative link and required conceptual route passed.

## Diagnostic Details

- **Reproduction**: From `<fixture>/packages/alpha`, resolve CAP-FIX-alpha-relationships; attempt to read returned `docs/packages/alpha/capabilities/fixture/CAP-FIX-alpha-relationships.md` against cwd.
- **Expected / Actual**: The reader expected a directly openable cwd-relative path. Actual output is correctly repository-relative; its first read failed.
- **Versions**: Reviewed source `970fa15cb336703ff60e9d4e8796be0b37d867dc`.
- **Conditions**: Registered alpha and beta namespaces in an ignored disposable fixture with an independent Git root.
- **Workarounds Attempted**: Prefixing the known fixture root succeeded. No runtime or required-route change was needed.
- **Related Assets**: `devkit docs resolve --help`, `CAP-DOCS-document-lookup`; Development evidence D3 records the reader steps.

## Evidence

```text
cwd: <fixture>/packages/alpha
resolve CAP-FIX-alpha-relationships: success, repository-relative path returned
cat docs/packages/alpha/capabilities/fixture/CAP-FIX-alpha-relationships.md: no such file
cat <fixture>/docs/packages/alpha/capabilities/fixture/CAP-FIX-alpha-relationships.md: success
selected ../../domain/grouping.md: success; correct distinction and validity owner located
```

This is optional efficiency feedback. No D3 criterion is waived and no defective resolver behavior is asserted.

- **Disposition**: `SPEC-open-feedback-fixes`: `devkit docs resolve --help` reads "Print the workspace-relative path of each document ID.", restating `CAP-DOCS-document-lookup` §3.1; output is unchanged.
