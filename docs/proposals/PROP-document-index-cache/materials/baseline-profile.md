# Baseline profile and parse-memo prototype

Measured on the `plan-document-index-cache` worktree at `eb33d6cf` (macOS, 14 cores, Python 3.12.8, PyYAML 6.0.3 with
libyaml), with another worktree's profiling running at the same time. Numbers are wall time; treat them as ratios.

## Commands (fresh process each, `.venv/bin/devkit`, 7 runs)

| Command | Median | Min |
| --- | --- | --- |
| `spec resolve CAP-DOCS-document-model` | 427 ms | 422 ms |
| `spec list feedback` | 440 ms | 432 ms |
| `spec refs CAP-DOCS-document-model` | 435 ms | 426 ms |
| `spec list capability` | 443 ms | 428 ms |
| `spec search cache` | 613 ms | 594 ms |
| `--help` | 191 ms | 178 ms |
| `--version` | 43 ms | 42 ms |

## Where `resolve` spends its time

`cProfile` of `devkit spec resolve` (1.07 s under the profiler): `DocumentIndex.load` 0.90 s, of which
`parse_document` 0.74 s over 693 files; `devkit_core.core.frontmatter.load_header` (pure-Python `SafeLoader`
subclass for duplicate-key checks) 0.40 s; prose scanning (`markdown.visible_lines` and the reference regexes)
0.24 s; plugin import 0.17 s.

In process, without the profiler:

| Step | Time |
| --- | --- |
| Import of the documents feature | 18 to 22 ms |
| Walk of `docs/` and `specs/` (693 files) | 12 to 16 ms |
| `os.stat` of every file | 1 to 2 ms |
| Read of every file (3.5 MiB) | 8 to 53 ms (page cache dependent) |
| BLAKE2b-128 of every file | 2.3 to 2.8 ms |
| `DocumentIndex.load` (fresh) | 294 to 327 ms |

Frontmatter value types over 637 documents: 9272 `str`, 1092 `dict`, 385 `list`, 375 `datetime.date`, 151 `bool`.
JSON cannot hold `date` without tagging. 3510 references in total.

## Serialization

| Format | Size | Decode | Rebuild `Document` objects |
| --- | --- | --- | --- |
| pickle (highest protocol) | 508 KiB | 5.2 to 5.5 ms | included |
| JSON, dates tagged `{"$d": ...}` | 917 KiB | 2.5 to 2.7 ms | 2.6 to 6.3 ms |

The JSON round trip compared equal (`==`) to the original documents.

## Prototype

A content-keyed memo (path to BLAKE2b digest and stored document, JSON) consulted through the `read` hook of
`DocumentIndex.load`, in a fresh process each run:

| Run | Memo decode | Index load with memo | Fresh index load | Identical |
| --- | --- | --- | --- | --- |
| 1 | 3.0 ms | 52 ms | 306 ms | yes |
| 2 | 2.9 ms | 58 ms | 327 ms | yes |
| 3 | 3.0 ms | 52 ms | 318 ms | yes |

Expected command time with a warm memo: about 427 - 310 + 55, so about 170 ms for `resolve`; the rest is interpreter
start, click and plugin import. A stat-signature key would skip the read and hash (10 to 50 ms more), at the cost
described in `PADR-content-keyed-document-parse-memo`.

## Related observations

- `devkit-viewer` reads documents from Git commits and does not use `DocumentIndex`.
- `WorkspaceCache.get_catalog` (`packages/devkit/src/devkit_agt/features/rules/repositories/workspace/`) builds a
  generic `DocumentCatalog` from `devkit_core` frontmatter, without the document model; devkit-agt cannot import
  devkit-spec, so it cannot share the memo.
- The spec rules load the index through `governance/services/documents.py` with a file list and reader from the
  rules workspace cache; content keys make the memo valid for those loads too.
- A libyaml-backed strict loader in `devkit_core.core.frontmatter` would cut the fresh parse, but it lies outside
  this proposal's boundary and leaves the per-call parse in place.
