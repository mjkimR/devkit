# Development selection evidence

Baseline algorithm: `29e7dd36845455d92d42e858e3372e3dd812a22e:scripts/affected_tests.py`. Both algorithms run against the same Development working tree, including the integrated MCP package and new selector tests. Production source is unchanged from that base.

One pytest collection supplied 3,929 parametrized node IDs in 4.05 seconds wall time. `measure.py` reproduces collection, baseline loading from Git, selection and three timings per case. `development-selection.json` records full selected paths, selected collected-file sets, per-file counts and timing samples. No production import is executed by selection; collection separately imports tests.

| Source area | Baseline files / tests | New files / tests | Median selector seconds (baseline / new) |
| --- | ---: | ---: | ---: |
| gate | 56 / 1073 | 16 / 301 | 0.685 / 1.150 |
| workflow | 107 / 2037 | 82 / 1608 | 0.657 / 1.270 |
| worktree | 94 / 1866 | 69 / 1361 | 0.659 / 1.197 |
| rules | 145 / 2779 | 120 / 2205 | 0.663 / 1.660 |
| distribution | 115 / 2177 | 96 / 1836 | 0.707 / 1.250 |
| compact | 151 / 3050 | 126 / 2476 | 0.666 / 1.223 |
| scope | 58 / 1118 | 54 / 1048 | 0.671 / 1.319 |
| documents | 58 / 1118 | 58 / 1118 | 0.667 / 1.243 |
| proposals | 58 / 1118 | 56 / 1065 | 0.688 / 1.228 |

Gate, scope and proposals demonstrate the required independent reductions. Documents retains all spec tests because its transitive consumers and package re-exports are broad; no reduction is claimed there. Static broad CLI/entry-point/source-tree consumers, opaque tests and embedded rules remain selected. Every devkit namespace row retains SOURCE_TREE_TESTS. The MCP fixed mapping remains tested independently.

Selection overhead roughly doubles (about 0.6 seconds extra per call on this machine). Investigation found repeated helper filesystem resolution in the first version (~2 seconds); a per-run helper-path cache reduced that overhead. AST parsing is once per file per run; no persistent cache is used. This cost buys relative imports, helper closures, conftests and module inventory resolution; it is reported rather than hidden by a hardware-independent threshold.

The real testsupport.gate dependency remains: workflow/test_hygiene_authoring.py and rules/engine/test_discovery.py are selected for gate changes. All eight gate test files and the six required structural files are also selected (16 files, 301 tests total). No helper imports were moved or removed to improve this number. Function-local helpers and transitive conftests can make other rows broader than the earlier file-only Planning probe.

Coverage evidence is separate from counts: independently authored temporary workspaces assert both consumer selection and unrelated-sibling exclusion, source/helper cycles, function-local imports, relative imports, package initialization and re-exports, attributes versus modules, wildcard/root/dynamic widening, invalid syntax, missing/renamed modules and ambiguous inventories. Existing runner, Git, data, frontend and full-trigger tests remain. Counts are not safety thresholds.

The final matrix includes the independent-review fixes: relative helper-package initializers and root CLI consumers that also import a fine module. Three additional regression cases verify those conditions.
