# Evaluation Lifecycle and Autofix Convergence

**Status**: Architecture Specification & Reference Implementation  
**Package**: `agent-rule-engine`  
**Related Documents**:
- [Rule Engine Overview](overview.md)
- [Rule Authoring Guide](rule-authoring.md)

---

## 1. Lifecycle Overview

The evaluation lifecycle executes deterministic checks across the repository in a controlled sequence:

```text
Initialize RuleContext and WorkspaceCache
  │
  ▼
Select Active Rules for Phase (linter or hygiene)
  │
  ▼
Run Specification & Invariant Checks
  │
  ▼
Collect Initial Violations and Execution Errors
  │
  ├─► If fix requested, no fatal errors, and not dry-run:
  │     │
  │     ▼
  │   Run Autofixable.fix() sequentially on modified files
  │     │
  │     ▼
  │   Invalidate modified files and dependent indexes in WorkspaceCache
  │     │
  │     ▼
  │   Recheck all active rules once (Convergence Pass)
  │     │
  │     ▼
  │   Mark resolved fixable findings as fixed if recheck succeeds
  │
  ▼
Return Final Violations and Execution Errors
```

---

## 2. Key Lifecycle Principles

### Single Repair Pass, Not an Unbounded Loop
The engine runs exactly **one repair pass followed by one convergence check**. It deliberately avoids unbounded iteration loops to guarantee termination and predictable runtimes.

### Cache Invalidation on Repair
When an autofix mutates a file on disk:
- The corresponding entries in `WorkspaceCache` (raw bytes, text lines, YAML frontmatter, parsed Markdown links) are immediately invalidated.
- Dependent document catalog indexes are refreshed prior to the convergence recheck.

### Convergence Guarantee
A finding is only marked as `"fixed": true` if the convergence recheck confirms that the violation has actually disappeared. If a fix fails or partially applies, the post-fix recheck reports the remaining violations accurately.

### Fail-Fast Error Reporting
- Invalid YAML frontmatter or unclosed syntax is reported as a violation rather than silently overwritten or corrupted by generated metadata.
- Dynamic rule import or runtime exceptions fail the command and output diagnostic details to `stderr`, keeping standard JSON output parseable on `stdout`.

---

## 3. CLI Execution and Phases

The CLI provides two primary commands:

```bash
# Check mode: strictly read-only, never mutates files
agent-rules check [-w DIRECTORY] [-p linter|hygiene] [--rules-dir DIRECTORY] [--format text|json] [FILES]...

# Fix mode: applies deterministic repairs and verifies convergence
agent-rules fix [-w DIRECTORY] [-p linter|hygiene] [--rules-dir DIRECTORY] [--dry-run] [--format text|json] [FILES]...

# Phase plan: default and effective phase of every rule, plus pending transitions
agent-rules phases [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]
```

- **Phases**:
  - `linter`: Structural specifications, frontmatter invariants, document references, and Markdown relative link validity. This is the gate for pre-commit hooks and CI.
  - `hygiene`: Includes `linter` rules plus file size warnings and formatting guidelines, and every rule parked there by a project phase override.
- **Exit Status**:
  - `0`: All checks passed cleanly, or all fixable findings were successfully repaired.
  - `1`: Unresolved errors, runtime failures, or rule loading errors.

---

## 4. Phase Transitions: Overrides and Promotions

A rule's declared `phase` is its default. Two mechanisms move a rule between phases without editing the rule, so that a gate can stay green while existing debt is cleared:

### Project Phase Overrides (`[rules.phase_overrides]`)

A consumer repository can park a `linter` rule in the `hygiene` phase through its Git-tracked `.devkit/config.toml`:

```toml
# .devkit/config.toml
[rules.phase_overrides]
RULE-markdown-link = "hygiene"
```

- Only `"hygiene"` is accepted as a value. An override for an unknown rule ID, or for a rule that already runs in `hygiene`, is reported as an error and the run fails.
- `linter` runs skip the overridden rule entirely. `hygiene` runs include it and print its remaining violation count:

  ```text
  [PHASE_OVERRIDE: RULE-markdown-link=hygiene default=linter source=.devkit/config.toml remaining=3]
  ```

- `remaining=0` is the signal to delete the entry and return the rule to its default phase.
- Violations report the phase the rule ran in (`phase: "hygiene"`), not the rule's declared default.

### Rule Promotions (`promote_to`)

A new rule introduced into a codebase with many pre-existing violations should be declared as `phase=Phase.HYGIENE` with `promote_to=Phase.LINTER` instead of blocking every session immediately:

```python
super().__init__(id="RULE-no-todo", name="no-todo", description="...", phase=Phase.HYGIENE, promote_to=Phase.LINTER)
```

- `promote_to` is only valid as `linter` on a `hygiene` rule; `BaseRule` rejects any other combination at construction time.
- `hygiene` runs print the remaining count for each such rule:

  ```text
  [PROMOTION: RULE-no-todo=hygiene promote_to=linter remaining=12]
  ```

- When the count reaches zero, flip the rule's declared `phase` to `linter` and drop `promote_to`.

### Inspecting the Plan

`agent-rules phases` lists every rule with its default phase, effective phase, and pending transition. `--format json` emits one object per rule with `rule_id`, `default_phase`, `effective_phase`, `overridden`, and `promote_to`, which is the stable surface for agents deciding whether an override can be retired.

`check --format json` remains a flat array of violations; count entries per `rule_id` to compute the same remaining totals.
