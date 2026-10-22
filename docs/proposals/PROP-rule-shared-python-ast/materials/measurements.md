# Planning measurements for PROP-rule-shared-python-ast

Measured on the `plan-rule-shared-python-ast` worktree at base `9c4fdb29` (macOS, CPython 3.12.8, 822 tracked Python
files). Every run is a whole-workspace `devkit rules check --format json` with the repository's installed bundles
(`cli-tool` is not selected, so the catalog rules do not run here). The probe scripts lived in the ignored
`probe/` directory, which is removed before the Planning branch's last commit; their method is described below so a later run can repeat them.

## 1. Baseline

| Measure | Value |
| --- | --- |
| Wall time, `.venv/bin/devkit rules check --format json` | 4.00-4.44 s (median of 7 interleaved runs 4.29 s) |
| Peak RSS | about 178-181 MB |
| Result | `{"violations": [], "errors": [], "notices": []}`, exit 0 |
| `ast.parse` calls (exec mode) | 1,526: `unique_code` 538, `architecture` 494, `usecase-boundaries` 494 |
| Files behind those calls | about 540 (494 parsed by all three rules, the rest by `unique_code` only) |
| Parse time, unprofiled | 0.82 s in total (`usecase-boundaries` 0.36 s, `unique_code` 0.25 s, `architecture` 0.22 s) |
| Cyclic GC time | 0.49-0.52 s (797/73/6 collections in generations 0/1/2) |

Per-rule wall time (unprofiled, one run): `RULE-advisory-unique-code` 0.90 s, `RULE-architecture` 0.80 s,
`RULE-usecase-boundaries` 0.69 s, `RULE-markdown-link` 0.51 s, `RULE-document-reference` 0.42 s,
`RULE-cli-contract` 0.35 s, `RULE-id-convention` 0.26 s, every other rule below 0.1 s.

`RULE-cli-contract` parses no Python: it checks CLI citations in Markdown (`cli_contract/citations.py`). The draft
listed it among the Python-source rules; it is out of this proposal's scope.

## 2. Profile (cProfile, 11.6 s under the profiler)

- `ast.walk` 1.72 million steps; `ast.iter_child_nodes` 5.37 million calls. One walk over all 822 trees costs about
  0.21 s unprofiled, so the repeated walks cost about 0.5 s; they are rule-internal and not shared by this proposal.
- `pathlib` resolution: 22,962 `Path.resolve` calls. `WorkspaceCache._key` resolves the path on every cache access
  (14,727 calls); `RuleContext._relative` evaluates `absolute.resolve()` on every call even when the lexical form
  already succeeds (7,828 calls through `is_file_targeted` and `settings`). 14,727 resolutions alone take 0.35 s
  unprofiled.

## 3. Shared-parse prototype

Method: `ast.parse` replaced by a memo keyed by the source (`str` or `bytes`), so every rule that parses the same
content receives the same tree object. `MODE=paths` instead made `RuleContext._relative` resolve only when the lexical
form fails and memoized `WorkspaceCache._key` per input path; `MODE=all` combined both. The retained trees were
released before interpreter exit, as a per-run `WorkspaceCache` is.

| Variant | Median wall time (7 interleaved runs) | Minimum | JSON output vs baseline |
| --- | --- | --- | --- |
| baseline | 4.29 s | 4.14 s | - |
| shared parse | 3.68 s (-0.61 s, -14 %) | 3.63 s | byte-identical |
| path resolution only | 3.87 s (-0.42 s, -10 %) | 3.71 s | byte-identical |
| both | 3.23 s (-1.06 s, -25 %) | 3.18 s | byte-identical |

- Shared parse: 490 distinct trees instead of 1,526 parses; GC time 0.15 s instead of 0.49 s (375/34/3
  collections), because far fewer AST objects are allocated.
- Time the real CLI process, not an in-process timer: when the probe kept its memo in a module global until
  interpreter shutdown, the shared-parse variant's wall time was 4.19 s (about 0.65 s at shutdown). That cost belongs
  to the probe's module global, not to a per-run cache: the challenger stored the shared trees on the run's own
  `WorkspaceCache`, which a reference cycle with its `DocumentCatalog` keeps alive until exit, and measured base
  4.25 s, trees left until exit 3.69 s, trees collected explicitly 3.71 s (5 interleaved real-CLI runs).
- Memory: holding all 822 trees of this repository adds about 221 MB RSS for 5.1 MB of source (challenger probe).
- Peak RSS with shared trees: 178-185 MB, unchanged from baseline (the two devkit-dev rules already hold all their
  trees at once).

## 4. Read-only safety (spike Q1)

- After a full run with shared trees, every one of the 490 cached trees was compared with a fresh parse of the same
  source using `ast.dump(..., include_attributes=True)`: 0 differed.
- Source review of `architecture`, `usecase-boundaries`, `unique_code` (`rule.py`, `index.py`) and the catalog
  `layers`, `heavy_imports`, `command_boundary` and `library_output` rules: no node attribute assignment,
  `setattr`, `NodeTransformer`, `fix_missing_locations` or list mutation of a node field. Per-module state
  (`usecase-boundaries` `Module.bindings`, `unique_code` `Module.classes`/`constants`/`imports`) lives on the rules'
  own dataclasses, which reference nodes but do not change them.
- Copy cost: `copy.deepcopy` of all 490 trees took 1.00-1.04 s, against 0.38-0.40 s to parse them all once, so a
  copy-per-caller design would be slower than today's repeated parsing.

## 5. Encoding and error behavior (spike Q2)

| Input | `ast.parse(text)` (cache `read_text`, UTF-8 with replacement) | `ast.parse(bytes)` |
| --- | --- | --- |
| UTF-8 with BOM | `SyntaxError: invalid non-printable character U+FEFF` | parses |
| Invalid UTF-8 byte | parses with U+FFFD | `SyntaxError: (unicode error) 'utf-8' codec can't decode ...` |
| NUL byte | `SyntaxError` (3.12) | `SyntaxError` |

The repository has 0 BOM and 0 non-UTF-8 Python files among 822. Today the parse sites read in three ways:
`architecture` and `usecase-boundaries` use `Path.read_text()` (strict, locale encoding) outside the cache;
`unique_code` and the four catalog rules use `ctx.cache.read_text` (replacement). Their syntax-error handling also
differs and is part of each rule's contract:

| Rule | On `SyntaxError` |
| --- | --- |
| `architecture` | reports `cannot parse source: <error>` at the file (also on `UnicodeError`) |
| `usecase-boundaries` | aborts with one `cannot inspect usecase boundaries: <error>` finding; parses without a file name, so the error reads `<unknown>` |
| `unique_code` | skips the file (also on `ValueError`) |
| catalog `layers`, `heavy_imports`, `command_boundary`, `library_output` | skip the file ("the linter of the language reports it") |

## 6. Loading and compatibility (spike Q2)

- Rules run from `.devkit/managed/` (ignored by Git; synchronized from the bundle sources) inside the installed
  `devkit-agt`, and `RuleContext.cache` is always a `WorkspaceCache`. `devkit-dist` and `devkit-agt` are pinned in
  lockstep (`==0.1.1`); `devkit-dev` and `devkit-catalog` are workspace packages. A rule calling a cache method the
  installed engine lacks fails as the evaluator's rule execution error, not silently.
- `inspect_architecture(root, config_path)` and `inspect_usecases(root, config_path)` are also called without a
  `RuleContext` by their bundled tests and by `tools/devkit-dev/tests/integration/test_architecture.py`.
- `devkit sync` after changing bundle rule sources rewrites the tracked `.devkit/installation.json` hashes.

## 7. Path-resolution edge inputs (second challenger round)

A probe compared today's eager `RuleContext._relative` (both candidates built in a tuple) with the lazy form over 23
inputs on CPython 3.12.8: relative and absolute paths, `..` segments, a workspace root reached through a symlinked
prefix, an in-workspace symlink pointing outside, `.`, the empty string and the root itself gave identical results.
The 2 differences were symlink loops (`loop1`, `loop1/x`): the eager form raises `RuntimeError` from `resolve()`,
the lazy form returns the lexical name. CLI targets are unaffected, because target expansion
(`services/targets.py`) resolves them first. In-run writers: every cache-aware fixer writes through `write_text`,
and the evaluator invalidates the returned paths after each fixer (or everything when a fixer raises); no fixer
creates, removes or retargets symlinks.
