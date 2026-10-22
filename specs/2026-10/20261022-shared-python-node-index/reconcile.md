---
reconcile_id: REC-shared-python-node-index
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-rule-authoring.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
---

# Reconcile: `SPEC-shared-python-node-index`

## Living Spec changes

- `CAP-GOV-rule-authoring` §2 lists `ctx.cache.get_python_nodes(path, *types)`: nodes of the requested `ast.AST`
  types from a Python file, in document traversal order, built once per file on first request from `get_python_ast(path)`;
  callers receive a shared immutable tuple of matching nodes and MUST NOT modify them (`ADR-index-python-ast-nodes-by-type-in-workspacecache`);
  raises `ValueError` when no types are passed, and re-raises any syntax error from `get_python_ast`.
- `CAP-GOV-rules-engine`: principle 3 says the session cache also holds indexed AST nodes by type; the layout comment
  for `cache.py` names node indexing.

## No-impact documents

- `CAP-GOV-evaluation-lifecycle`: already specifies cache invalidation dropping parsed Python data and derived indices;
  the node index is cleared under the exact same invalidation calls.
- CLI output and rule contracts: byte-identical findings on this repository (`AC-07`).
- Rule-specific guides: findings and remediation are unchanged.

## Deferred work and source feedback

None: the spec carries no source feedback, and all planned tasks were completed within scope.
