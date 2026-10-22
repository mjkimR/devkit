---
id: FB-presentation-warning-missing-from-notice-table
title: The sync notice table in the distribution quick reference lacks PRESENTATION_LANGUAGE_UNSUPPORTED
scope: repo
kind: suggestion
category: docs-mismatch
target: docs/development/reference/distribution.md (sync output and notices table)
skill: spec-sync
agent: claude-code
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-22
---

# [FB-presentation-warning-missing-from-notice-table] The sync notice table in the distribution quick reference lacks PRESENTATION_LANGUAGE_UNSUPPORTED

## 2. Suggestion / Change Request

- **Current Procedure**: `devkit sync` now returns a `PRESENTATION_LANGUAGE_UNSUPPORTED` warning
  (`PresentationLanguageUnsupportedNotice`) under `notices`. The quick reference's sync notice table lists every
  other sync notice code with its level, class, trigger and fields, but not this one; only the presentation
  paragraph of the same file names the code.
- **Proposed Procedure**: Add one table row: `PRESENTATION_LANGUAGE_UNSUPPORTED`, `WARNING`,
  `PresentationLanguageUnsupportedNotice`, "a shared or local `[presentation] language` other than `auto`, `en` or
  `ko` fell back to `en`; also in `devkit status` and `devkit config show` `notices`", fields `target_files` (the
  configuration file) and `fix` (the accepted values and the file).
- **Expected Benefit**: An agent looking up a code in the table finds every sync warning in one place.
- **Cost & Risk**: One documentation line; none.
- **Attempted**: Not attempted. The worker payload allowed edits to the quick references only where their fallback
  field description changes, so only the presentation paragraph was updated.

## Diagnostic Details

- **Reproduction**: Search the sync notice table of the distribution quick reference for `PRESENTATION_LANGUAGE`.
- **Expected / Actual**: Expected a row like `HARNESS_ENGINE_MISSING`'s; actual has none.
- **Versions**: Unit `SPEC-feedback-quick-fixes`, rework turn on base 48e6479d.
- **Conditions**: Local-orchestrated Development worker, activity-effort low.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `docs/development/reference/distribution.md`,
  `packages/devkit-dist/src/devkit_dist/features/project/models/presentation.py`, `CAP-DIST-sync-and-transactions`.

## Evidence

```text
distribution.md table rows: ORPHAN_LEFT, OVERRIDE_DRIFT, MANAGED_FILE_STRAY, ..., HARNESS_ENGINE_MISSING, ...,
POST_SYNC_NOTICE; no PRESENTATION_LANGUAGE_UNSUPPORTED row.
Payload write scope: docs/development/reference/{distribution,host,integration}.md only if their fallback field
description needs to change.
```
