# Read-path survey (Q1, Q3)

Measured on the Planning worktree at `35950b46` (content of `eb2d5dba`), Apple M4 Pro, Python 3.12, with a
throwaway static probe under the ignored `tmp/probe/` (`scan_reads.py`, `check_misses.py`, `timing.py`). The probe
never imports test code; it reuses `scripts/affected_tests.py` only to ask what the current selector selects.

## Method

- Files: every `*.py` under a `tests` directory of `packages/*` and `tools/*` (441 files: test modules, embedded rule
  tests, conftests and helpers), the same population the selector's groups and helper traversal draw from.
- A path expression is root-anchored when it evaluates statically from `Path(__file__)` through `.resolve()`,
  `.parent`, `.parents[N]`, `/ "<literal>"`, `.joinpath(...)`, `Path(<anchored>, "<literal>")` and module or
  function-level names bound once to such an expression (including `NAME.parents[N]`).
- A miss: change one representative existing file at the read path, run `select(root, [file], tier="all")`, and the
  reading test (or, for a helper, a test importing it) is absent from a partial or none selection.

## Q1: path forms and static recoverability

| Form | Count | Statically recoverable |
| --- | --- | --- |
| `<anchored> / "a/b/c"` chains (all from `Path(__file__)...parents[N]`, often through a module constant) | 71 | yes, to an exact path |
| `<anchored>.glob/rglob("<literal pattern>")`, `.iterdir()` | 28 | the base directory and the pattern |
| `<anchored> / <name or f-string or attribute>`, `joinpath(*parts)` | 6 | only the anchored base directory |
| `Path("docs/...")` relative to the working directory | 0 repository reads (the matches build `tmp_path` repositories) | n/a |

- 44 of 441 files read any root-anchored path. Of the 71 exact reads, 59 point into `packages/`, 4 into `docs/`, 3
  into `guides/`, 2 into `examples/`, 2 into `scripts/` and 1 into `models/`.
- The draft's "about 30 test files read `docs/capabilities` by literal path" does not hold: 48 files mention
  `capabilities`, but almost every literal builds a fixture repository under `tmp_path`. Repository document reads by
  literal path are four (`docs` as a whole in `test_docs.py` and `test_documented_codes.py`,
  `docs/development/reference/workflow.md` in `test_library.py`, `CAP-DLV-delivery-roles.md` in
  `test_scratch_cleanup_guidance.py`), and the DATA table already lists every one.
- Not recoverable by any literal scan and kept as DATA rows: readers by document ID or index (`test_bundle_citations`,
  `test_documented_codes`, `test_docs`), subprocess runs in the repository root, and source-tree scans whose base is
  a loop variable (`test_agent_output_contract`'s `[FIX]` scan, the `FB-affected-selection-misses-cross-package-fix-scan`
  case, which `ALL_SOURCES_TESTS` now covers).

## Measured misses at this head

| Changed file (representative) | Reading test | Current result |
| --- | --- | --- |
| `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/*.md` | `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py` | partial, test absent |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/SKILL.md.jinja` | `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` | partial, test absent |
| `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `guides/install/bundle-recommendations.md` | `test_deep_research.py` | none (`guides/` selects nothing) |
| `packages/devkit-catalog/README.md` | `test_deep_research.py` | none (package-root Markdown selects nothing) |
| `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja` | `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py` | partial, test absent |
| `packages/devkit/src/devkit_agt/bundles/authoring/bundle/bundle.toml` (read by helper `testsupport/layering.py`) | `packages/devkit/tests/integration/package/test_mounted_commands.py` | partial, test absent |
| `packages/devkit/tests/integration/features/compact/fixtures/mypy-errors.txt` | `packages/devkit/tests/integration/features/compact/test_corpus.py` | none (a non-test file selects its directory, which holds no test module) |

- Zero misses under `docs/`, `specs/`, `examples/`, `models/` and `scripts/`: the class the draft names is closed
  today by hand-kept rows; the open class is cross-package bundle assets, paths the selector treats as untested
  (`guides/`, package-root Markdown) and test data beside its reader.
- A helper's read applies to every test that imports the helper: `spec_support/bundle_text.py` reads the docs bundle,
  and all 37 importing tests are already selected through their imports; `testsupport/layering.py` has one missed
  importer.

## Q3: cost

| Measurement | Seconds (best of 3; the end-to-end probe one run) |
| --- | --- |
| `select` for a document-only change today (no graph) | 0.013 s |
| `select` for one `devkit_spec` source file today (graph and groups) | 4.26 s |
| Parse every test-tree file (`ast.parse`, the selector's `_tree`) | 0.63 s |
| Walk the parsed trees for path joins | 0.19 s |
| Probe end to end (parse, environment, evaluation of 441 files) | 1.50 s |

- A document-only change grows from about 0.01 s to about 1.5 s because it must now parse the test trees; a source
  change adds about 0.2 to 0.9 s to 4.3 s, since groups already parse every test module and its helpers.
- No persistent cache: the cost is small next to any pytest run, and `ADR-test-selection-and-ci` keeps the selector
  stateless. The scan reuses the in-process parsed trees.

## Over-selection

Base-directory matching for dynamic joins makes `test_lockstep.py` (`PACKAGES / directory / "pyproject.toml"`)
a reader of all of `packages/`. Literal glob patterns matched against their pattern, not their base, keep
`tools/devkit-dev/tests/integration/test_architecture.py` (`root.glob("packages/*/src/**/*.py")`) to package sources.
Estimate, not measured: about three added test modules for each package source change (`test_lockstep.py`, `test_architecture.py` and `test_bundle_citations.py` when its base resolves).
