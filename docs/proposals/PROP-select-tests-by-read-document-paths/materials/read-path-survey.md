# Read-path survey (Q1, Q3)

Measured on the Planning worktree at `af3bd7e3` (selector and tests identical to `eb2d5dba`), Apple M4 Pro,
Python 3.12, with throwaway static probes under the ignored `tmp/probe/`. The first probe (`scan_reads.py`) recorded
only outermost path expressions and missed reads nested in calls (`challenger-01` finding 1); the figures below
come from the second probe (`scan_v2.py`, `check_v2.py`). The probes never import test code; they reuse
`scripts/affected_tests.py` only to ask what the current selector selects.

## Method

- Files: every `*.py` under a `tests` directory of `packages/*` and `tools/*` (441 files: test modules, embedded rule
  tests, conftests and helpers).
- A read is a root-anchored path expression: evaluated statically from `Path(__file__)` through `.resolve()`,
  `.parent`, `.parents[N]`, `/ "<literal>"`, `.joinpath(...)`, `Path(<anchored>, "<literal>")` and names bound once
  to such an expression. Every maximal such expression counts wherever it occurs (call receiver or argument
  included); binding it to a name does not count, its uses do. Loop variables over literal tuples expand.
- Glob, `rglob` and `iterdir` calls record their base and pattern; a join with a runtime segment records its base.
- A miss: change one representative existing file at the read path, run `select(root, [file], tier="all")`, and the
  reading test is absent. A helper's read is checked for each test module importing the helper (4 helpers have
  reads; their importers are found by module name in 0.2 s).

## Q1: path forms and static recoverability

| Form | Reads | Statically recoverable |
| --- | --- | --- |
| Exact `<anchored> / "a/b"` chains (incl. inside `.read_text()`, `str(...)`, `shutil.copy(...)`) | 324 (199 distinct file-path pairs) | yes, to an exact path |
| `glob` / `rglob` with a literal pattern | 45 | base and pattern |
| `iterdir` | 1 | base directory |
| Join with a runtime segment | 26 | base directory only |
| Join based at the repository root itself after loop expansion | 0 | n/a |
| `Path("docs/...")` relative to the working directory | 0 repository reads (the matches build `tmp_path` repositories) | n/a |

- 54 of 441 files read root-anchored paths. Exact reads by top directory: `packages/` 270, `scripts/` 23, `tools/` 7,
  `docs/` 7, `guides/` 7, `examples/` 5, `.devkit/` 3, `models/` 2.
- The draft's "about 30 test files read `docs/capabilities` by literal path" does not hold: 48 files mention
  `capabilities`, but almost every literal builds a fixture repository under `tmp_path`. Every literal read under
  `docs/`, `examples/` and `models/` is already selected through `DATA`.
- 14 reads name a package root directory (`packages/<name>`, `tools/devkit-dev`), for example a package directory
  passed as a working directory. As directory reads they make `packages/<name>/README.md` select those tests.
- Not recoverable by a literal scan, and kept as explicit mappings: readers by document ID or index
  (`test_bundle_citations`, `test_documented_codes`, `test_docs`), subprocess runs in the repository root
  (`test_version_script.py` runs `scripts/release.sh` and `just release-build` and is selected by neither file
  today), and source-tree scans with an unresolved base (`test_agent_output_contract`'s `[FIX]` scan, the
  `FB-affected-selection-misses-cross-package-fix-scan` case, which `ALL_SOURCES_TESTS` now covers).

## Measured misses at this head

37 missed pairs among 272 checked. Grouped:

| Changed file | Reading test (via) | Current result |
| --- | --- | --- |
| `.devkit/architecture.toml` | `packages/devkit-dist/tests/unit/architecture/test_layering.py`, `packages/devkit-dist/tests/integration/cli/test_cli_imports.py` (helper `distsupport/layering.py`); `packages/devkit/tests/integration/package/test_layering.py`, `test_mounted_commands.py` (helper `testsupport/layering.py`) | partial, tests absent |
| `.devkit/config.toml` | `tools/devkit-dev/tests/integration/test_handbook_script.py` | none (`.devkit/` selects nothing) |
| `scripts/viewer.sh` | `packages/devkit/tests/integration/package/test_viewer_script.py` | none (frontend) |
| `scripts/module.sh` | `packages/devkit/tests/e2e/package/test_affected_tests.py` | partial, test absent |
| `guides/INSTALL_GUIDE.md`, `guides/install/*.md` | `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` | none (`guides/` selects nothing) |
| `devkit-spec` bundle `skills/spec/SKILL.md.jinja`, `references/proposals-catalog.md` | `test_deep_research.py` | partial, test absent |
| `devkit-spec` bundle `AGENTS.md.jinja` | `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` | partial, test absent |
| `devkit-catalog` `maintenance/bundle/playbooks/*.md` | `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py` | partial, test absent |
| `packages/devkit/tests/integration/features/compact/fixtures/*.txt` | `test_corpus.py` beside them | none (a non-test file selects its directory, which holds no test module) |
| Test modules read as data (`test_bundle_citations.py`, `test_architecture.py`, viewer `test_cli.py`) | `test_affected_tests.py`, `test_test_environment.py` | partial, readers absent |
| `packages/<name>/README.md`, `tools/devkit-dev/README.md` (package-root directory reads) | 21 pairs across 9 packages | none (package-root Markdown selects nothing) |

- No miss under `docs/`, `specs/`, `examples/` or `models/`: the class the draft names is closed by hand-kept rows.
  The open class is cross-package bundle assets, helper reads of `.devkit/architecture.toml`, untested and frontend
  prefixes, recipe scripts and test data.
- A helper's read applies to every test module importing it: all 37 importers of `spec_support/bundle_text.py` are
  already selected through their imports; the two layering helpers have four missed importers.

## Q3: cost

| Measurement | Seconds |
| --- | --- |
| `select` for a document-only change today (no graph), best of 3 | 0.013 |
| `select` for one `devkit_spec` source file today, best of 2 | 4.26 |
| `Workspace(root).groups` (import discovery of every test module), one run | 1.75 (7.9 to 9.4 under the challenger's concurrent load) |
| Parse every test-tree file, best of 3 | 0.63 |
| Probe v2 end to end (parse, environment, evaluation of 441 files), one run | 2.14 |
| Importers of the 4 helpers with reads, by module name, one run | 0.20 |

- A document-only selection grows from about 0.01 s to about 2.5 s with reverse attribution (scan every file once,
  resolve importers only for helpers with reads), or about 4 s if it runs the full `groups` traversal.
- A source selection already parses the test trees and runs `groups`; the scan adds about 1.5 s of evaluation.
- No persistent cache: `ADR-test-selection-and-ci` keeps the selector stateless, and the cost is small next to a
  pytest run.

## Over-selection

- With loop expansion, `test_lockstep.py` reads `packages/*/pyproject.toml` and `tools/*/pyproject.toml` globs and
  package source trees, not the repository root, so `.claude/` and other untested paths still select nothing.
- Literal glob patterns matched against their pattern keep `tools/devkit-dev/tests/integration/test_architecture.py`
  (`root.glob("packages/*/src/**/*.py")`) to package sources.
- Package-root directory reads (14) make a package README select that package's bundle and package tests.
