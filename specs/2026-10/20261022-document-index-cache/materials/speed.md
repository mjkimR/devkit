# Speed and multi-process evidence

Recorded for `SPEC-document-index-cache` (AC-06, AC-10) on the `dev-document-index-cache` worktree at `5e14eca4`
(the implementation and Living Spec commits; later commits change only this Unit's records). macOS on Apple silicon,
14 cores, Python 3.12.8, PyYAML 6.0.3 with libyaml. Nothing else ran during the measurements. Wall time.

The scripts ran from the ignored `scratch/` directory of the worktree and are summarized here; they are not part of
the change.

## In-process `DocumentIndex.load` (AC-10)

Method: copy `docs/` and `specs/` into `scratch/fresh/` with an empty `.devkit/` and no `.devkit/transient/`, so
the copy has no memo. Warm the worktree's memo with one load, then one discarded load of each root, then seven
interleaved pairs: a load of the worktree (warm memo) and a load of the copy (no memo), clearing the in-process memo
before each load so every load behaves like a new process. Before timing, the warm and fresh results were compared
equal (documents with frontmatter, references and aliases, problems, historical paths).

| Load | Runs (ms) | Median |
| --- | --- | --- |
| Warm memo (worktree, 644 documents) | 53.4, 53.4, 55.1, 55.4, 53.8, 53.7, 54.8 | 53.8 ms |
| No memo (copy) | 315.2, 319.9, 361.2, 314.5, 312.9, 318.9, 317.9 | 317.9 ms |

Ratio of the medians: 0.169, within the bound of 0.35 (prototype: 0.18). A profile of the warm load shows the
existing walk (`os.walk`, `stat`, `pathlib.relative_to`) and file reads as most of the remaining time; decoding the
memo (590 KiB) is a small part.

## Commands (AC-10)

Method: seven interleaved runs of each command with `.venv/bin/devkit`, timed around `subprocess.run` in one Python
driver after one discarded run of each: `-w` the worktree (warm memo) and `-w scratch/fresh` (made its own Git
repository so that it is a devkit root; no `.devkit/transient/`, so no memo). Every run exited `0`.

| Command | Warm memo, median | No memo, median | Baseline (`baseline-profile.md`, `eb33d6cf`) |
| --- | --- | --- | --- |
| `devkit spec resolve CAP-DOCS-document-model` | 187 ms | 428 ms | 427 ms |
| `devkit spec list feedback` | 191 ms | 432 ms | 440 ms |
| `devkit --help` (no index load) | 177 ms | | 191 ms |

The baseline column quotes `docs/materials/2026-10/20261022-document-index-cache/baseline-profile.md`, measured on
the Planning worktree while another profiling ran. The proposal expected about 170 ms with a warm memo; the rest of
each call is interpreter start, click and plugin import (`devkit --help`), outside this Unit (Non-Goal 4).

## Several processes at once (AC-06)

Method: a copy of `docs/` and `specs/` with `.devkit/transient/` in `scratch/concurrency/`. Four rounds; before
rounds 1 to 3 one document changes, so every process has a changed entry to write. In each round eight processes
started with the `spawn` method wait on one barrier, then each runs `DocumentIndex.load` (which reads and writes the
memo) and returns its result. The parent compares each result with a load that has the memo disabled, then decodes
the memo left behind: `version` and `fingerprint` current and every entry rebuilt by `decode_entry`.

| Round | Processes | Results equal to a fresh build | Exit codes | Memo entries | Memo decodes |
| --- | --- | --- | --- | --- | --- |
| 0 (no memo) | 8 | 8 | all `0` | 701 | yes |
| 1 | 8 | 8 | all `0` | 701 | yes |
| 2 | 8 | 8 | all `0` | 701 | yes |
| 3 | 8 | 8 | all `0` | 701 | yes |

The integration test `test_concurrent_loads_all_equal_a_fresh_build_and_leave_a_valid_memo` runs the same check
with eight threads in one process.
