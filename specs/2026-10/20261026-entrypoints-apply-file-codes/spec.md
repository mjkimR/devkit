---
id: SPEC-entrypoints-apply-file-codes
title: Entrypoints apply accepts or refuses file codes
summary: devkit spec entrypoints derive --apply --code <file> applies nothing and exits 0 when the file lies under a directory candidate; accept such a file or refuse each unmatched --code with a stable code.
status: planned
created: 2026-10-26
related_capabilities: [CAP-TRACE-code-entrypoints]
related_usecases: []
workflow: sdd-spec-bugfix
---

# [SPEC-entrypoints-apply-file-codes] Entrypoints apply accepts or refuses file codes

## 1. Problem Statement & Motivation

The `spec-entrypoints` skill tells an agent to keep 1-3 doorway files per document and apply them with
`devkit spec entrypoints derive --spec <dir> --apply --target <id> --code <file>`. When the bundle's `_Boundary`
candidates are directories and the chosen files lie under them, the command writes nothing, exits `0` and names no
reason, so the run reads as a success. The agent has to edit the frontmatter by hand.

### Source feedback

- `FB-entrypoints-apply-ignores-file-codes` (scope `repo`, open): accept a `--code` file under a candidate path, or
  report each unmatched `--code` with a stable code and an `[ACTION]`.

## 2. Defect Characterization

- **Current behavior**: in `spec-sync` step 4 of the `SPEC-foundation-documents` bundle, whose `_Boundary` paths are
  directories, `devkit spec entrypoints derive --spec <dir> --apply --target <CAP-ID> --code <file> --code <file>`
  printed `[SUMMARY: pairs=0 new=0 declared=0 skipped=8 applied=0]` and exited `0`. `select` keeps a pair only when a
  `--code` path equals or contains the pair's code; a file never contains its directory candidate.
  `fold_by_directory_selectors` synthesizes a pair only for a trailing-`/` selector that contains candidates. A
  `--code` that names no candidate at all (`src/nowhere`) has the same silent result, which
  `test_target_without_selected_candidates_applies_nothing` currently asserts.
- **Expected behavior and its basis**: per the agreed intent (decision `gate:plan-intent`), a `--code` path that
  lies under a candidate of a document becomes a candidate pair of that document, so `--apply` writes it; a `--code`
  that matches no candidate is refused with a stable code and a deterministic `[ACTION]`
  (`ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol`). `CAP-TRACE-code-entrypoints` section 3.5 calls
  `--code` "the review's selection", and the skill's review keeps doorway files.
- **Behavior to preserve**: `--code` equal to or containing candidates keeps them (`test_code_and_exclude_filters`);
  a trailing-`/` selector folds the candidates under it and a non-directory one fails with
  `SPEC_ENTRYPOINTS_PATH_INVALID` (`test_derive_directory_code_folds_and_applies`, `test_fold_by_directory_selectors`);
  `--target` checks, apply collapse, idempotent reruns and byte-preserving writes (`test_apply.py`, `test_cli.py`);
  runs without `--code` are unchanged.
- **Reproduction conditions**: a bundle whose task `_Boundary` is `src/pkg/` with `src/pkg/b.go` present and whose
  `reconcile.md` targets one capability; run `derive --spec <bundle> --apply --target <capability> --code
  src/pkg/b.go`.

## 3. Non-Goals

1. **Scope Excluded**: judging whether a selected file is a good doorway; the `spec-entrypoints` review decides.
2. **Scope Excluded**: changing derivation, folding or apply rules for runs without `--code`.
3. **Scope Excluded**: selecting a path outside every candidate of the document; the bundle never named it.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A selected file under a directory candidate is applied
- **Given** a bundle whose only candidate of a capability is the directory `src/pkg` and an existing `src/pkg/b.go`
- **When** `derive --spec <bundle> --apply --target <capability> --code src/pkg/b.go` runs
- **Then** it exits `0`, prints `[APPLIED: <capability> path=<doc> added=src/pkg/b.go]` and the summary
  `pairs=1 new=1 declared=0 ... applied=1`, and the document's `entrypoints` ends with `src/pkg/b.go`

### [AC-02] A selected folded candidate is applied
- **Given** a bundle whose candidates `src/pkg` and `src/pkg/sub/c.go` fold the file into the directory
- **When** `derive --spec <bundle> --apply --target <doc> --code src/pkg/sub/c.go` runs
- **Then** the file is written to the document and is not reported as `reason=folded`

### [AC-03] An unmatched --code is refused before anything is written
- **Given** a `--code` path that neither equals, contains nor lies under a candidate of the derived documents (of the
  `--target` documents when given)
- **When** `derive` runs, with or without `--apply`
- **Then** it exits `2` with `SPEC_ENTRYPOINTS_CODE_UNMATCHED` (`INPUT_ERROR`), `[TARGET]` lists every unmatched
  `--code` value, `[ACTION]` directs choosing a path from the candidates the run without `--code` lists, and no
  document is written

### [AC-04] Existing selectors are preserved
- **Given** a `--code` equal to or containing candidates, a trailing-`/` directory selector, or no `--code`
- **When** `derive` runs, with or without `--apply`
- **Then** the output and the written documents are those the existing tests assert
