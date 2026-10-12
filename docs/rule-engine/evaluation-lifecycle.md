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
  │   (a Git snapshot gate materializes the staged or CI tree first and uses it as the root)
  ▼
Validate Project Policy: phase overrides, severity overrides, typed settings
  │   (any problem stops the run before a rule executes)
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

# Git snapshot gates: the exact staged tree, or HEAD against its merge base with --base
agent-rules check --staged [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]
agent-rules check --ci [--base REF] [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]

# Fix mode: applies deterministic repairs and verifies convergence
agent-rules fix [-w DIRECTORY] [-p linter|hygiene] [--rules-dir DIRECTORY] [--dry-run] [--format text|json] [FILES]...

# Phase plan: default and effective phase of every rule, plus pending transitions
agent-rules phases [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]

# One rule: phase, severity, effective settings and guide
agent-rules explain RULE-ID [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]
```

Rules come from three sources, in order: the built-in registry, every `kind = "rule"` asset recorded by `devkit sync` in `.devkit/installation.json`, and `--rules-dir`. A later rule with the same ID replaces an earlier one.

- **Phases**:
  - `linter`: Structural specifications, frontmatter invariants, document references, and Markdown relative link validity. This is the gate for pre-commit hooks and CI.
  - `hygiene`: Includes `linter` rules plus file size warnings and formatting guidelines, and every rule parked there by a project phase override.
- **Exit Status**:
  - `0`: All checks passed cleanly, or all fixable findings were successfully repaired.
  - `1`: Unresolved errors, runtime failures, rule loading errors, or invalid project policy.

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

---

## 5. Project Policy: Severity Overrides and Typed Settings

The `[rules]` table of `.devkit/config.toml` is the only place a project changes a distributed rule's behavior; managed rule files are hash-checked by `devkit sync` and are never edited.

### Severity Overrides (`[rules.severity_overrides]`)

```toml
[rules.severity_overrides]
RULE-file-length = "error"
```

The value is `error`, `warning` or `info`. Violations of the rule report the effective severity, and `error` violations fail the command. An entry for an unknown rule, or one equal to the rule's declared severity, is an error.

### Typed Settings (`[rules.settings.<RULE-id>]`)

A rule declares its settings by assigning a frozen dataclass instance to `settings`; the instance carries the defaults and the class carries the field types (`int`, `float`, `str`, `bool`, `list[str]`). A project configures the rule, optionally per path:

```toml
[rules.settings.RULE-file-length]
max_lines = 300
extensions = [".md"]

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

- Every layer is validated before any rule runs: unknown keys, wrong types (`true` is not an integer, `"10"` is not a number), explicit nulls and unsupported patterns fail with the rule ID in the message, and so does a rule's own `validate_settings` rejection. Settings for an unknown rule, or for a rule that declares none, are errors.
- `path` is workspace-relative. A standalone `**` matches zero or more segments; `*`, `?` and character classes match within one segment. Overrides apply in declaration order to every file they match, so later matching overrides win; keys an override omits keep the earlier value. Arrays replace.
- `ctx.settings(rule, path)` returns the effective dataclass for a file; `agent-rules explain <RULE-id>` prints the defaults, the configured values and each override.

---

## 6. Git Snapshot Gates

`check --staged` and `check --ci --base <ref>` evaluate a Git tree instead of the working directory:

| Mode | Tree evaluated | Comparison base | Changed files |
| --- | --- | --- | --- |
| `--staged` | the index (`git write-tree`) | `HEAD` (the empty tree on an unborn branch) | index vs `HEAD` |
| `--ci` | `HEAD` | `git merge-base <base> HEAD` | merge base vs `HEAD` |

The tree's regular files are materialized into a temporary directory (symlinks and submodules are skipped, executable bits kept) which becomes the workspace root for the run. Consequences:

- Unstaged edits, untracked files and ignored local files do not exist for the gate.
- `.devkit/config.toml`, `.devkit/installation.json` and synchronized rules are read from the snapshot, so policy must be committed to take effect in a gate.
- The changed files of the diff are the targets; deleted paths are reported in the `[SNAPSHOT: ...]` line and never evaluated. A snapshot with no changed files passes without loading rules.
- Snapshot gates run the `linter` phase only and refuse file arguments, `--phase hygiene` and `fix`; `--staged` and `--ci` are mutually exclusive.

Two built-in linter rules exist for these gates and inspect explicit targets only: `RULE-secret-leak` (credential files and private key, AWS, GitHub and `sk-` token patterns) and `RULE-clean-artifacts` (compiled binaries, database files, logs above 1 MiB). In a plain `check` they inspect the files named on the command line and report nothing for a whole-workspace run, because a working tree scan would flag ignored local files.
