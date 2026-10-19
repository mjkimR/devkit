---
id: FB-generated-check-uncommitted-registry
title: devkit generated check refuses an artifact that list shows, before the registry is committed
scope: repo
kind: friction
category: tool-error
target: devkit generated check
skill: none
agent: claude-code
origin: agent
severity: workaround
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-generated-check-uncommitted-registry] devkit generated check refuses an artifact that list shows, before the registry is committed

## 1. Friction / Question (friction, question)

- **Context**: registering a new artifact (`viewer-assets`) in a new `.devkit/generated.toml` and checking it before
  committing.
- **Expectation**: the refusal's `[FIX]` leads to a working command; `list` and `check` agree on which artifacts
  exist.
- **Actual**: `devkit generated list` read the working-tree registry and printed `viewer-assets`; `devkit generated
  check viewer-assets` read the registry at `HEAD` (as `CAP-GEN-tracked-artifacts` §5 states) and refused with
  `ARGUMENT_INVALID ... unknown or disabled generated artifacts: viewer-assets`, its `[FIX]` saying to pass an ID
  `list` prints, which it had printed.
- **Workaround (or Interpretation Chosen)**: committed the registry, then ran `check`; it passed.
- **Suggestion**: when the ID is registered in the working tree but not at the checked revision, say so in the
  message and the `[FIX]` (commit the registry or pass `--rev`), or let `list` take `--rev` and name the revision it
  read.

## Diagnostic Details

- **Reproduction**: add an artifact to an uncommitted `.devkit/generated.toml`; run `devkit generated list`, then
  `devkit generated check <id>`.
- **Expected / Actual**: expected a check or a refusal naming the uncommitted registry; got `ARGUMENT_INVALID` whose
  `[FIX]` contradicts `list`.
- **Versions**: devkit-agt at this Unit's branch.
- **Conditions**: new or changed registry not yet committed.
- **Workarounds Attempted**: commit first; succeeded.
- **Related Assets**: `devkit generated list`, `devkit generated check`, `CAP-GEN-tracked-artifacts` §5.

## Evidence

```text
[GENERATED: viewer-assets source=project seed=ours paths=packages/devkit-viewer/src/devkit_viewer/static/** ...]
[ERROR]  (ARGUMENT_INVALID) unknown or disabled generated artifacts: viewer-assets
[FIX]    Pass ids that `devkit generated list` prints (registered: devkit-receipt)
```

- **Disposition**: packages/devkit/src/devkit/generated/engine.py: `devkit generated check` names an ID registered only in the working tree as not committed at the checked revision, with a `[FIX]` to commit `.devkit/generated.toml` or pass `--rev`.
