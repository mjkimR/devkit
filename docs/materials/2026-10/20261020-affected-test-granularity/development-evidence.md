# Development selection evidence

Baseline algorithm: `29e7dd36845455d92d42e858e3372e3dd812a22e:scripts/affected_tests.py`. Both algorithms run against the same Development working tree, including the integrated MCP package and new selector tests. Production source is unchanged from that base.

One pytest collection supplied 3,926 parametrized node IDs in 4.28 seconds wall time. `measure.py` reproduces collection, baseline loading from Git, selection and three timings per case. `development-selection.json` records full selected paths, selected collected-file sets, per-file counts and timing samples. No production import is executed by selection; collection separately imports tests.

| Source area | Baseline files / tests | New files / tests | Median selector seconds (baseline / new) |
| --- | ---: | ---: | ---: |
| gate | 56 / 1073 | 16 / 301 | 0.657 / 1.134 |
| workflow | 107 / 2037 | 81 / 1606 | 0.638 / 1.330 |
| worktree | 94 / 1866 | 61 / 1288 | 0.639 / 1.209 |
| rules | 145 / 2779 | 119 / 2203 | 0.679 / 1.285 |
| distribution | 115 / 2177 | 88 / 1763 | 0.675 / 1.351 |
| compact | 151 / 3050 | 125 / 2474 | 0.668 / 1.280 |
| scope | 58 / 1118 | 51 / 1016 | 0.674 / 1.367 |
| documents | 58 / 1118 | 58 / 1118 | 0.700 / 1.268 |
| proposals | 58 / 1118 | 55 / 1063 | 0.643 / 1.289 |

Gate, scope and proposals demonstrate the required independent reductions. Documents retains all spec tests because its transitive consumers and package re-exports are broad; no reduction is claimed there. Static broad CLI/entry-point/source-tree consumers, opaque tests and embedded rules remain selected. Every devkit namespace row retains SOURCE_TREE_TESTS. The MCP fixed mapping remains tested independently.

Selection overhead roughly doubles (about 0.6 seconds extra per call on this machine). Investigation found repeated helper filesystem resolution in the first version (~2 seconds); a per-run helper-path cache reduced that overhead. AST parsing is once per file per run; no persistent cache is used. This cost buys relative imports, helper closures, conftests and module inventory resolution; it is reported rather than hidden by a hardware-independent threshold.

The real testsupport.gate dependency remains: workflow/test_hygiene_authoring.py and rules/engine/test_discovery.py are selected for gate changes. All eight gate test files and the six required structural files are also selected (16 files, 301 tests total). No helper imports were moved or removed to improve this number. Function-local helpers and transitive conftests can make other rows broader than the earlier file-only Planning probe.

Coverage evidence is separate from counts: independently authored temporary workspaces assert both consumer selection and unrelated-sibling exclusion, source/helper cycles, function-local imports, relative imports, package initialization and re-exports, attributes versus modules, wildcard/root/dynamic widening, invalid syntax, missing/renamed modules and ambiguous inventories. Existing runner, Git, data, frontend and full-trigger tests remain. Counts are not safety thresholds.
