# Planning measurements for PROP-persistent-python-facts-cache

Measured on `main` at `ae108957` (Linux, CPython 3.12, 826 tracked Python files, 539 parsed AST modules).
Incorporates state after `SPEC-rule-shared-python-ast`, `SPEC-shared-python-node-index`, `SPEC-spec-rules-shared-document-index`, and `SPEC-snapshot-scoped-rules`.

## 1. Measured Baseline After In-Memory Optimizations

While in-memory AST caching (`_ast_cache`) and AST node indexing (`_nodes_cache`) eliminate duplicate parsing and walking across rules **within a single process**, each new CLI invocation (`devkit rules check`, commit gates, workflow steps) is a new process that starts cold.

| Rule | Cold Run (unprimed AST cache) | Warm Run (primed in-memory AST cache) | Cold-start AST & Walk Penalty |
| --- | --- | --- | --- |
| `RULE-architecture` | 1,552.8 ms | 228.2 ms | 1,324.6 ms |
| `RULE-advisory-unique-code` | 1,236.8 ms | 426.4 ms | 810.4 ms |
| `RULE-usecase-boundaries` | 433.0 ms | ~70.0 ms | ~363.0 ms |
| **Combined 3 Python Rules** | **~3,222.6 ms** | **~724.6 ms** | **~2,498.0 ms (~2.5 s)** |

Total `devkit rules check` runtime on an unchanged working tree: **~6.0 s** (~6,170 ms rule execution).
Cold AST parsing and node traversal across the 539 Python files account for **~2.5 s (~41 %)** of the total check duration.

## 2. Synthetic Facts Persistence Benchmark

To verify whether persistent facts loading is fast enough to replace per-run AST parsing:

- Simulation: 550 Python files with typical extracted facts (module names, package hierarchy, import tuples, and symbol declarations).
- Serialized JSON payload: **95.9 KB** (single file) or ~180 bytes per file.
- `json.loads` decode time: **0.84 ms** (< 1 ms).

Comparison:
- Cold AST parse + `get_python_nodes` walk across 539 files: **~2,500 ms**.
- Loading pre-extracted facts from `.devkit/transient/` on disk: **~1 ms**.
- Net saving on unchanged files: **~2,490 ms (~2.5 s)**.

## 3. Rule Analysis & Fact Extraction Scope (Spike Q1)

| Rule | File-Level Facts (Pure, Content-Digest Keyed) | Cross-File Judgment |
| --- | --- | --- |
| `RULE-architecture` | `(module_name, package, is_package, imports: list[tuple[str, int]], attribute_bindings: list[tuple[str, str]])` | Builds global package import graph; checks directional boundaries against `.devkit/architecture.toml`. |
| `RULE-advisory-unique-code` | `(codes: list[tuple[str, str, int, bool]], owner_classes: list[str], function_calls: list[tuple[str, str, int]])` | Resolves inheritance and checks that advisory codes are unique across all declared classes. |
| `RULE-usecase-boundaries` | `(module_name, layer, imports: dict[str, str], usecase_classes: list[str])` | Verifies that use cases do not import transports or prohibited layers. |

Each of the three rules splits cleanly: per-file facts depend solely on the single file's text/AST, while violations arise only during cross-file graph aggregation.

## 4. Storage & Invalidation Architecture (Spike Q2)

Reusing the decisions from `ADR-content-keyed-document-parse-memo` and `ADR-parse-memo-location-and-format`:

- **Location**: `<root>/.devkit/transient/rules/facts/<rule-id>.json`. Storing per-rule JSON files ensures that modifying one rule's logic only invalidates that rule's cache without purging others.
- **Cache Key**: Per-file entry keyed by workspace-relative POSIX path and BLAKE2b digest of the file's UTF-8 text.
- **Fingerprint**: Format version + rule module source bytes hash + devkit version + Python version. Any code edit to `rule.py` or helper modules automatically invalidates stored facts.
- **In-Memory Retention**: The loaded facts dictionary is placed in `ctx.cache.get_or_compute("rules.facts.<rule_id>", ...)` so subsequent passes or rechecks within the same run never re-read disk facts.

## 5. Snapshot Integration (Spike Q3)

Under `SPEC-snapshot-scoped-rules`, staged and CI runs execute against temporary directories (`/tmp/devkit-rules-snapshot-...`) without a local `.devkit/transient/`.
Because entries are keyed by content digest (BLAKE2b of file content), a snapshot run can safely read the host repository's facts cache in read-only mode for unchanged files, avoiding a ~2.5 s full re-parse in pre-commit and CI gates when any Python file changes.

