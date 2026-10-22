---
reconcile_id: REC-entrypoints-directory-apply
status: resolved
targets:
  - file: docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md
    resolution: modified
---

# Reconciliation: `SPEC-entrypoints-directory-apply` Apply directory code entrypoints

`CAP-TRACE-code-entrypoints` section 3.5 now explicitly specifies that when `--code` ends with `/`, it requires an existing workspace directory, candidate pairs under that directory are folded into a single directory entrypoint pair, and `--apply` records that directory entrypoint with a trailing `/` in the document's frontmatter.

No other Living Spec contracts change:
- `CAP-GOV-spec-rules`: `RULE-code-entrypoints` already accepts directories with trailing `/` (section 3.1).
- `UC-keep-the-living-spec-consistent`: Steps and contracts are preserved; the entrypoint apply command now correctly produces single directory declarations when requested.
- `FB-entrypoints-directory-code-expands-to-files`: Fully resolved and documented.
