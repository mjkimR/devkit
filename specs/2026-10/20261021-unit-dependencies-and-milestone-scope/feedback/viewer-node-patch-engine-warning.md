---
id: FB-viewer-node-patch-engine-warning
title: Viewer locked dependencies warn on the available Node patch
scope: repo
kind: friction
category: other
target: packages/devkit-viewer/frontend/package-lock.json
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-21
---

# [FB-viewer-node-patch-engine-warning] Viewer locked dependencies warn on the available Node patch

## 1. Friction / Question

Toolchain patch compatibility creates installation warning noise.

- **Context**: Running the affected selector's required viewer verification sequence.
- **Expectation**: The locked dependency install supports the available Node environment without engine warnings.
- **Actual**: Installation succeeded but npm reported EBADENGINE for dependencies requiring a newer Node patch.
- **Workaround**: Continued verification; lint, check, 17 tests, pack and build all passed. No dependency or engine setting changed.
- **Suggestion**: Align the documented or provisioned Node patch with the locked dependency requirements. The successful checks make this noise rather than a demonstrated functional failure.

## Diagnostic Details

- **Reproduction**: Observed once during `just viewer install`; no repeat installation solely for feedback.
- **Expected / Actual**: Clean locked installation / successful installation with engine compatibility warnings.
- **Versions**: Node v22.22.0; locked packages included jsdom 30.1.3 and w3c-xmlserializer 6.0.0. npm version unknown.
- **Conditions**: Local viewer frontend verification after the direct proposal membership correction.
- **Workarounds Attempted**: Continued the prescribed verification sequence successfully; no engine override attempted.
- **Related Assets**: `packages/devkit-viewer/frontend/package-lock.json`, `just viewer install`.

## Evidence

```text
npm WARN EBADENGINE
current Node: v22.22.0
reported required Node: ^22.22.2 || ^24.15.0 || >=26.0.0
installation completed; viewer lint/check/test/pack/build passed
```

- **Disposition**: resolved. Session change `packages/devkit-viewer/frontend/package.json`, its `package-lock.json` and `docs/development/setup.md`: the declared and documented Node range is now the locked dependencies' `^22.22.2 || ^24.15.0 || >=26.0.0`, so a Node below it is reported as unsupported for the viewer itself; the viewer install, lint, check, test, pack and build sequence passes.
