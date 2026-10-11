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
agent-rules check [--phase linter|hygiene] [--format text|json]

# Fix mode: applies deterministic repairs and verifies convergence
agent-rules fix [--dry-run] [--phase linter|hygiene]
```

- **Phases**:
  - `linter`: Structural specifications, frontmatter invariants, document references, and Markdown relative link validity.
  - `hygiene`: Includes `linter` rules plus file size warnings and formatting guidelines.
- **Exit Status**:
  - `0`: All checks passed cleanly, or all fixable findings were successfully repaired.
  - `1`: Unresolved errors, runtime failures, or rule loading errors.
