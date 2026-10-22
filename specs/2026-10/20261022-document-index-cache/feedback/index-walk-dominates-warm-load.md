---
id: FB-index-walk-dominates-warm-load
title: The index walk dominates a load with a warm parse memo
scope: repo
kind: suggestion
category: other
target: packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py
origin: agent
severity: noise
recurring: false
status: resolved
created_at: 2026-10-22
---

# [FB-index-walk-dominates-warm-load] The index walk dominates a load with a warm parse memo

Performance: with the parse memo of `SPEC-document-index-cache`, most of a warm load is the walk, not parsing.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `DocumentIndex.load` walks with `os.walk`, builds a `Path` per file, checks
  `is_symlink`/`is_file` per file and per directory, and computes `path.relative_to(root).as_posix()` per file.
- **Proposed Procedure**: Walk with `os.scandir` entries (their cached `is_symlink`/`is_file` results) and build the
  workspace-relative path as a string while descending, keeping the same order, exclusions and symbolic-link rules.
- **Expected Benefit**: The warm load is about 54 ms on this repository, against 315 ms without a memo; under the
  profiler `relative_to` alone is a large share, and `stat` and path construction most of the rest. A leaner walk
  could cut a further 10 to 20 ms per lookup call.
- **Cost & Risk**: The walk decides which files are documents; a change must keep the exclusions of
  `CAP-DOCS-document-model` 3.1 exactly. A test that compares the old and new file lists covers it.
- **Attempted**: Profiled only; not implemented (outside `SPEC-document-index-cache`, which keeps the walk).

## Diagnostic Details

- **Reproduction**: Warm the memo, clear the in-process memo, `cProfile` one `DocumentIndex.load` of this repository.
- **Expected / Actual**: Not applicable (an optimization).
- **Versions**: Python 3.12.8, PyYAML 6.0.3 with libyaml, macOS on Apple silicon.
- **Conditions**: A workspace with `.devkit/transient/` and an unchanged memo.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `specs/2026-10/20261022-document-index-cache/materials/speed.md`, `CAP-DOCS-document-model`.

## Evidence

```text
cProfile, warm load (0.164 s under the profiler), by internal time:
  _io.open 702 calls 0.019 s; posix.stat 1807 calls 0.019 s cumulative; posix.scandir 397 calls 0.009 s
  pathlib relative_to 701 calls 0.048 s cumulative; pathlib __init__ 11514 calls
In-process medians without the profiler: warm 53.3 ms, no memo 315.2 ms.
```

- **Disposition (resolved)**: Replaced `os.walk` and repetitive `pathlib.Path` relative calculations with an `os.scandir` DFS walk in `_files` that carries workspace-relative POSIX paths and leverages cached `DirEntry.is_symlink`/`is_file`/`is_dir` results, cutting walk time from ~41.5 ms down to ~6.6 ms (84% walk speedup) while preserving exact directory and file order and `CAP-DOCS-document-model` 3.1 exclusions. Covered by updated `test_only_documents_under_docs_and_specs_are_indexed`, `test_symlinked_source_directory_is_skipped`, and `test_walk_traversal_deterministic_order` in `packages/devkit-spec/tests/integration/features/documents/test_index.py`.
