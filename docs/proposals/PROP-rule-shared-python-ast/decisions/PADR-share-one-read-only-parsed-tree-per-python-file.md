---
id: PADR-share-one-read-only-parsed-tree-per-python-file
title: Share one read-only parsed tree per Python file
summary: For Python-source rules that each parse every file, we hand every rule the same cached ast.Module and require it to stay unmodified, to keep the parse saving (copying all trees costs more than parsing them), accepting that a rule that mutates a tree would corrupt later rules' input.
proposal: PROP-rule-shared-python-ast
status: draft
created_at: 2026-10-22
---

# [PADR-share-one-read-only-parsed-tree-per-python-file] Share one read-only parsed tree per Python file

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

Three Python-source rules in this repository's run (`architecture`, `usecase-boundaries`, `unique_code`) and four
catalog `cli_tool` rules each parse every Python file they inspect: 1,526 parses of about 540 files per
`devkit rules check`, 0.82 s of parsing plus the garbage collection those objects cause. A per-run cache can parse each
file once, but only if handing the same `ast.Module` to several rules cannot change any rule's result.

## 2. Decision Drivers

- Rule results stay byte-identical to separate parses.
- The saving survives: whatever the cache returns must cost much less than a parse.
- The contract stays simple enough for a new rule author to follow.

## 3. Considered Options

- **Shared tree, read-only by contract**: every caller receives the same cached object. Costs nothing per call;
  correctness depends on no rule mutating a tree.
- **Deep copy per call**: isolates rules completely. Copying all 490 distinct trees takes 1.00-1.04 s against
  0.38-0.40 s to parse them, so it is slower than today's repeated parsing.
- **Immutable view or frozen node classes**: would enforce read-only access, but `ast` nodes are mutable stdlib
  classes; a proxy layer costs on every attribute access and breaks `isinstance` checks the rules rely on.
- **Keep per-rule parsing**: no risk, no saving.

## 4. Decision Outcome

Chosen: **shared tree, read-only by contract**.

- It is the only option that keeps the saving (drivers 2 and 1): the prototype run shared 490 trees across the
  three rules, produced byte-identical output and left all 490 trees equal to a fresh parse
  (`ast.dump(..., include_attributes=True)`).
- No current rule mutates a node: the source review found no attribute assignment, `setattr`, `NodeTransformer` or
  node-list mutation; per-module state lives on the rules' own dataclasses.
- `CAP-GOV-rule-authoring` states the contract: a tree from the cache is shared for the run and is never modified;
  a rule that needs a changed tree parses its own copy (driver 3).

## 5. Consequences

- Positive: one parse per file and run for every migrated rule; fewer AST allocations also cut cyclic GC time
  (0.49 s to 0.15 s in the prototype).
- Negative: a future rule that mutates a shared tree silently changes the input of every later rule in that run.
- Risk: trees stay alive for the whole run instead of one rule; peak RSS was unchanged in the prototype because the
  devkit-dev rules already hold all their trees at once.
- Follow-up: if a mutating rule is ever needed, it parses its own tree; revisit enforcement only when a mutation
  defect is observed.

## 6. Confirmation

- A test in `packages/devkit/tests/integration/features/rules/workspace/test_cache.py` asserts that repeated
  `get_python_ast` calls return the same object.
- Each migrated rule's tests assert that, after `check`, the trees it read through the cache equal a fresh parse
  (`ast.dump` with attributes).
- Review: `CAP-GOV-rule-authoring` names the read-only contract.
