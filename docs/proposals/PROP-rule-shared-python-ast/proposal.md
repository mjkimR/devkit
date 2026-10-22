---
id: PROP-rule-shared-python-ast
title: Parse each Python file once per rules run
summary: "Adds a parsed-AST cache to the rules workspace cache so every rule that inspects Python source shares one parse per file and run, cutting the repeated parsing that dominates devkit rules check."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: governance/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit/src/devkit_agt/features/rules/
    - docs/capabilities/governance/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-rule-shared-python-ast] Parse each Python file once per rules run

## 1. Background & Hypothesis

`devkit rules check` takes about 4.1 s (Measured on main at 4dbf9c4b (macOS, Python 3.12, this repository: about 820 tracked Python files and 850 Markdown files)). A profile shows most of it in Python AST work: about 1,500
`ast.parse` calls and 1.7 million `ast.walk` steps per run, because each Python-source rule parses every file itself.
The heaviest are the devkit-dev `architecture` and `usecase-boundaries` rules, the advisory `unique_code` rule and the
built-in `cli_contract` rule; the catalog `cli_tool` rules (`layers`, `command_boundary`, `library_output`,
`heavy_imports`) do the same where selected. The rules `WorkspaceCache` (`RuleContext.cache`) already shares text,
frontmatter and Markdown links per run, but not parsed Python.

Hypothesis: one parse per file per run, shared through the cache, removes most of the repeated work without
changing any rule's result.

## 2. Technical Spike Questions

- **Q1**: Is a shared `ast.Module` safe to hand to several rules (no rule mutates it), or does the cache need to
  return copies or a read-only view, and what does each option cost?
- **Q2**: How do rules loaded from `.devkit/managed` reach the cache API compatibly (a `WorkspaceCache` method such
  as `get_python_ast(path)`), and how are syntax errors reported once rather than per rule?

## 3. Proposed Design & Impact

- `WorkspaceCache` gains a parsed-AST accessor that caches by path for the run and is invalidated with the existing
  `invalidate` calls after a fix.
- The Python-source rules above use it; their violations stay byte-identical on this repository (a before/after
  comparison of `devkit rules check --format json` is the acceptance evidence), and the run time is measured again.
- The rule authoring guidance (`CAP-GOV-rule-authoring`) names the accessor for new Python-source rules.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr rule-shared-python-ast "<title>" --summary "<Y-statement: For <context>, we <decision>, to <quality>, accepting <downside>.>" records a PADR in decisions/.
- Research: collect benchmarks and references in materials/.
- On acceptance (plan-accept): devkit spec proposal accept rule-shared-python-ast --by user records gate:plan-accept and status:
  accepted, then the Planning branch is merged; an eligible draft may instead be accepted with --direct on the base,
  without Planning. Development starts with devkit spec proposal handoff rule-shared-python-ast.
- On rejection: change only status: rejected, with the user's reason in the commit message; a later hygiene pass
  writes the rejection ADR and deletes the proposal directory.
-->
