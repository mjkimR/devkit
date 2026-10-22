---
id: PROP-shared-python-node-index
title: Walk each Python tree once per rules run
summary: "Adds a per-run node index to the rules workspace cache so Python-source rules read the nodes they need from one shared traversal instead of each walking every tree."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: low                  # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - tools/devkit-dev/
    - packages/devkit-dist/src/devkit_dist/bundles/advisory/
    - packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-shared-python-node-index] Walk each Python tree once per rules run

## 1. Background & Hypothesis

After `SPEC-rule-shared-python-ast` each Python file is parsed once per rules run, but the Python-source rules still
walk every shared tree themselves: a profile of `devkit rules check` (Measured on main at df307e99 (macOS, Python 3.12, about 820 tracked Python files), about 2.9 s) shows about 1.75 million
`ast.walk` steps and 5.4 million `iter_child_nodes` calls, mostly from `RULE-architecture` (`_imports`),
`RULE-advisory-unique-code` and `RULE-usecase-boundaries`, which each traverse the whole tree to find a few node kinds.

Hypothesis: one traversal per file that indexes nodes by type, cached beside the parsed tree, serves every rule and
removes most of the remaining Python-analysis time.

## 2. Technical Spike Questions

- **Q1**: Which node kinds do the rules read (imports, function and class definitions, calls, string constants), and
  does any rule need traversal order or parent links that a by-type index loses?
- **Q2**: What is the accessor shape (`get_python_nodes(path, *types)` returning a read-only sequence) and its memory
  cost next to the shared tree?

## 3. Proposed Design & Impact

- `WorkspaceCache` builds the node index lazily on first request and keeps it for the run under the same
  invalidation as the parsed tree; the shared-tree read-only contract extends to the index.
- The three rules (and the catalog `cli_tool` rules where they walk trees) read from the index; outputs stay
  byte-identical on this repository.
- Acceptance: `devkit rules check` median measured on main before and after, interleaved; walk-step count recorded.
- A smaller, safer step than `PROP-persistent-python-facts-cache`; its result decides whether that one is worth it.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr shared-python-node-index "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept shared-python-node-index --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff shared-python-node-index.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
