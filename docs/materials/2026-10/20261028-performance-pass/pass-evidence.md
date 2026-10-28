# Evidence from the 2026-10-27 performance pass

Source: commits `f8906778..ffb9a99a` on `main` (merge `602e0997`, `git log --format='%h %s%n%b' 4850156c..602e0997`),
the earlier shared-AST Planning measurements
(`docs/materials/2026-10/20261022-rule-shared-python-ast/measurements.md`, cited below as "AST measurements") and the
session observations the Host handed to this Planning turn (marked **H**; they are not in a commit body and were not
re-measured here, because this turn has no probe path).

## 1. What the pass changed and how it proved it

| Commit | Target and cost found | Measured (warm, unprofiled) | Preservation evidence |
| --- | --- | --- | --- |
| `f8906778` | `find_files` walked the tree per query (28 per full run), `relative_to` plus two stats per file | `find_files` 0.30 s -> 0.05 s (full check), 0.20 s -> 0.045 s (one-file check) | Old and new `find_files` over every directory to depth 4 plus special roots, with and without the Git filter: identical over 4632 and 4638 queries, with symlinks of each kind and an NFD name |
| `aabd01de` | `Path.relative_to(...).as_posix()` about 15 us a call, ~8000 calls; links listed twice | one-file rules check 0.44 s -> 0.33 s | `rules check`, targeted check and `rules fix --dry-run` JSON and exit codes identical with the previous source loaded through `PYTHONPATH`, on a temporary bundle with planted defects |
| `a2c62f84` | `extract_links` scanned all 96257 lines; only 3141 contain `](` | `RULE-markdown-link` 0.34 s -> 0.18 s | Old and new over 1270 Markdown files plus synthetic edge cases: same 3184 links |
| `89bea535` | Two scans per document for citations | `RULE-cli-contract` 0.27 s -> 0.23 s | Old and new over 1270 files: same 4035 citations |
| `f92da980` | 111k cached expression records decoded through a recursive cycle-checked walk; allocation and GC dominated | `usecase-boundaries` 0.57 s -> ~0.40 s, `architecture` 0.24 s -> ~0.19 s; cache 4.93 MB -> 4.15 MB | Byte-identical JSON cold and warm; 521 files round-trip old and new codecs; planted violations give the same findings with cache off, cold and warm; schema version bumped so old caches are dropped |
| `2fd53e1e` | 29 subprocesses per `sync --dry-run`: repeated Git queries, per-path checks, a second inventory plan | `sync --dry-run` 1.25 s -> ~0.92 s, subprocesses 29 -> 14 | stdout, stderr and exit codes of four commands and the receipt identical; new tests pin each helper to the per-path answers. Left: an MCP runtime probe (~450 ms) and two interpreter probes whose answers are not known in advance |
| `ffb9a99a` | Review regression in `f8906778` | none | Reviewer reproductions give `main`'s results; 4704 queries match `main` with loop and EACCES symlinks; new tests fail on the previous head |

## 2. The regression the review found

`f8906778` replaced `Path.is_file()` (which returns `False` on a symlink loop or a symlink into an unreadable
directory) with `DirEntry.is_file()` (which raises there) for every file of the shared scan. One such symlink anywhere
made every listing fail. The differential comparison had covered loop-free symlink kinds only; a fresh reviewer found
it. The same review found two more input classes the faster path changed: a root spelled differently than on disk
(case, Unicode normalization) and a memoized Git query with a vanished working directory.

Lesson for the playbook: a faster API often differs from the replaced one on error paths and unusual inputs, not on
the corpus. The differential input set must include the input domain's error cases, and the reviewer brief must ask
for inputs under which behavior differs.

## 3. Measurement traps

| Trap | Evidence | Consequence for the protocol |
| --- | --- | --- |
| A deterministic profiler inflates wall time and distorts shares | AST measurements §2: 11.6 s under cProfile against a 4.29 s median (2.7x); **H**: 2-3x during this pass | Report savings only from unprofiled runs; confirm a hotspot's share unprofiled before it becomes a candidate |
| Work in child processes is invisible to an in-process profiler | `2fd53e1e`: half the subprocesses removed; **H**: the profile showed only the wait | Count and time subprocesses separately |
| Allocation and garbage collection cost is not attributed to a function | `f92da980`; AST measurements §1 (0.49-0.52 s of GC in a 4.29 s run) | Measure collector time and object counts when a hotspot builds large object graphs |
| An in-process timer misses interpreter shutdown | AST measurements §3 (0.65 s at shutdown for a module-global memo) | Time the real process from outside |
| The first run after a change rebuilds caches | `f92da980` schema bump; **H** | Discard runs after a code or cache-format change; label cold and warm |
| zsh does not word-split an unquoted `$var` | **H**: a command held in a variable ran as one word | Run commands from an argument list or a script file, check each run's exit code and output |
| Concurrent agents and builds add noise | **H** | Interleave variants, record load, repeat when the range is wide |
| Before and after measured in different checkouts | **H**; `aabd01de` loaded the previous source through `PYTHONPATH` in the same checkout | Measure both variants on the same machine in the same session, the old one from an extracted copy or a separate checkout of the previous revision, never by stashing or switching the working checkout |

## 4. Per-component timing

The pass measured per-rule times inside a full `rules check` and per-function times (`find_files`) unprofiled, which
located 0.25 s of the 0.30 s listing cost in one function. AST measurements §1 shows the same pattern: per-rule wall
times summed against the total. A composite operation needs a per-component breakdown before candidates are ranked.

## 5. Route and application

The pass ran on its own branch (`dev-perf-polish`), one commit per change with the change record (target, measured
before/after, preservation) in the commit body, then a fresh review and a fix commit before integration. That is the
`review-refactor` application procedure (work item branch, one commit per change, verification, review, report),
plus a measurement per change.
