# Evidence: one parse per Python file and run

Measured in the `dev-rule-shared-python-ast` worktree on an Apple M4 Pro, macOS, CPython 3.12.8. "Before" is the
handoff base 47993c48 (main 8240e402 with `SPEC-lint-clean-target-scoped-rules` merged); "after" is dac9a100 with
`.devkit/managed/` synchronized. The probe script lived in the ignored `scratch/` directory; its method is described
below so a later run can repeat it.

## 1. Parse count (AC-08)

Method: a script replaced `ast.parse` with a wrapper that counts exec-mode calls by calling module and by `filename`,
then ran `devkit_dist.cli.cli` with `rules check --format json` in the same process.

| | Exec-mode `ast.parse` calls | Distinct file names | Most calls for one name |
| --- | --- | --- | --- |
| Before | 1,529 (`unique_code` 539, `architecture` 495, `usecase-boundaries` 495) | 540 (`usecase-boundaries` parsed every file as `<unknown>`) | 495 (`<unknown>`) |
| After | 539, all from `WorkspaceCache.get_python_ast` | 539 | 1 |

## 2. Byte identity (AC-09)

`.venv/bin/devkit rules check --format json` exits 0 before and after and prints the same 56 bytes
(the empty result, pretty-printed; SHA-256
`459a5ce9be4cd412219a88944ca4491b4b41e8660176fe545a8257aa1dcede91`; compared with `cmp`). The repository has no
Python file with a BOM, a coding cookie or invalid UTF-8, so no accepted edge-case change applies. Findings on valid
source are covered by each migrated rule's existing tests, which pass unchanged.

## 3. Wall time (AC-10)

Method: 7 sequential runs of `/usr/bin/time -p .venv/bin/devkit rules check --format json` (stdout discarded), the
"before" series on the base before any change and the "after" series after the change and `devkit sync`, on the same
machine and worktree. The series are not interleaved, because the worker creates no second checkout; the Host repeats
the measurement on main after integration.

| | Runs (s) | Median |
| --- | --- | --- |
| Before | 3.98, 4.02, 4.00, 4.01, 4.03, 4.02, 4.06 | 4.02 s |
| After | 3.03, 3.07, 3.07, 3.05, 3.05, 3.05, 3.07 | 3.05 s |

The median is 0.97 s (24 %) lower, above the 0.8 s target.
