---
reconcile_id: REC-snapshot-scoped-rules
status: resolved
targets:
  - file: docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-rules-engine.md
    resolution: modified
  - file: docs/development/reference/rules.md
    resolution: modified
---

# Reconcile: `SPEC-snapshot-scoped-rules`

## Living Spec changes

- `CAP-GOV-evaluation-lifecycle`:
  - §3 Target scoping updated: applies to explicit working-tree runs and Git snapshot runs (`check --staged`, `check --ci`). Scoping candidate paths in snapshot runs include targets plus `snapshot.deleted` (including typechanges and old paths of renames), while `RuleContext.targets` holds only existing files. Modifying `.devkit/config.toml` or `.devkit/installation.json` disables rule skipping. Whole-workspace CI runs (`just rules-check` in `.github/workflows/ci.yml`) remain the complete safety net.
  - §6 Git Snapshot Gates updated: target scoping applies to snapshot runs, skipping declared rules whose inputs match no changed or deleted paths.
- `CAP-GOV-rules-engine`:
  - Principle 5 updated: target scoping in `evaluate_rules` ensures explicit targets and snapshot diffs agree on which rules can be affected.
- Rules Reference (`docs/development/reference/rules.md`):
  - Updated target scoping description to cover snapshot evaluation.
