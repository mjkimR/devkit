# Agreed feedback items

The user asked to process the open feedback (2026-10-26); these two are decision-free and follow their suggestions.
The handbook is no longer refreshed for this work.

1. `FB-selection-edits-rewrite-crlf-line-endings`
   (specs/2026-10/20261026-approval-mode-and-crlf-template/feedback/selection-edits-rewrite-crlf-line-endings.md).
   Defect: selection edits (`_document`, `prepare_config_update`, used by `devkit add` and the other selection
   commands) parse the untranslated text so existing lines keep their bytes, and an added entry uses CRLF when every
   line ending of the file is CRLF, LF otherwise, the same rule `devkit config template` follows. Reuse that rule
   rather than duplicating it. Reproduce with a failing CRLF regression test first. Targets: the distribution
   installation config service, its tests, `CAP-DIST-sync-and-transactions` (Selection edits) and the distribution
   reference if it states the result.
2. `FB-viewer-review-probes-outside-vitest-include`
   (specs/2026-10/20261026-viewer-handbook-first-knowledge/feedback/viewer-review-probes-outside-vitest-include.md).
   Give `scripts/viewer.sh` a `probe <dir>` action (and the `just viewer` pass-through, if the recipe needs one) that
   runs vitest on the `*.test.ts` files of an absolute directory outside `src/` with the package's normal
   resolution, so a reviewer runs `just viewer probe <worktree>/scratch/review-NN` without writing its own config.
   Name it in the viewer reference (`docs/development/reference/viewer.md`) and in the code-reviewer contract's probe
   sentence for frontend changes. Verify it on a throwaway probe.
