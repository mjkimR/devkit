# Evaluation Lifecycle and Autofix Convergence

**Status**: Architecture Specification & Reference Implementation  
**Package**: `devkit.rules`  
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
Run Rule Checks
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
  │   Mark fixable findings as fixed when the recheck reports fewer findings
  │   with the same rule, file and message (lines may move during a fix)
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
- Fixes never rewrite what they cannot reproduce: a file that is not valid UTF-8 is left untouched, writes keep every other byte (line endings included), and nothing under `.devkit/managed/` or `.devkit/overrides/` (copies pinned by the installation receipt) is written.
- Malformed frontmatter in one document does not stop the run: the document catalog records it in `frontmatter_errors` and keeps indexing paths. A bundle rule that requires valid frontmatter reports it as its own violation.
- Dynamic rule import or runtime exceptions fail the command and output diagnostic details to `stderr`, keeping standard JSON output parseable on `stdout`.

---

## 3. CLI Execution and Phases

The CLI provides two primary commands:

```bash
# Check mode: strictly read-only, never mutates files
devkit rules check [-w DIRECTORY] [-p linter|hygiene] [--rules-dir DIRECTORY] [--format text|json] [--summary-only] [TARGETS]...

# Git snapshot gates: the exact staged tree, or HEAD against its merge base with --base
devkit rules check --staged [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json] [--summary-only]
devkit rules check --ci [--base REF] [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json] [--summary-only]

# Fix mode: applies deterministic repairs and verifies convergence
devkit rules fix [-w DIRECTORY] [-p linter|hygiene] [--rules-dir DIRECTORY] [--dry-run] [--format text|json] [--summary-only] [TARGETS]...

# Phase plan: default and effective phase of every rule, plus pending transitions
devkit rules phases [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]

# One rule: phase, severity, effective settings and guide
devkit rules explain RULE-ID [-w DIRECTORY] [--rules-dir DIRECTORY] [--format text|json]
```

Without `-w` every command uses the project root of the current directory: the nearest directory containing `.devkit/`, else the Git work tree top level, else the current directory.

Rules come from three sources, in order: the built-in registry, every `kind = "rule"` asset recorded by `devkit sync` in `.devkit/installation.json`, and `--rules-dir`. A later rule with the same ID replaces an earlier one.

- **Phases**:
  - `linter`: Markdown relative link validity, safety checks on explicit targets, and every bundle-distributed rule declared in this phase. This is the phase evaluated by `check --staged` (and by the `rules-staged` pre-commit gate of [`devkit gate`](../gate/overview.md#2a-built-in-gates)) and by `check --ci`.
  - `hygiene`: Includes `linter` rules plus file size warnings, every bundle rule declared in this phase, and every rule parked there by a project phase override.
- **Targets**: `TARGETS` are workspace-relative or absolute paths inside the workspace. A file is checked as is; a directory expands recursively to the regular files under it with the same discovery as workspace scans: dependency and cache directories (`.git`, `.venv`, `node_modules`, caches) and `.devkit/managed/` and `.devkit/overrides/` are skipped, symlinks resolving outside the workspace are skipped, and inside a Git work tree Git-ignored files are skipped unless named explicitly. No targets means the whole workspace; a directory without files checks nothing. A target that is neither an existing file nor a directory inside the workspace is a `RULES_TARGET_INVALID` failure before any rule runs. Snapshot gates refuse targets.
- **Exclusions**: `exclude` under `[rules]` lists workspace-relative patterns (`**` grammar of settings overrides) that no rule targets. Excluded paths are removed from explicit, directory-expanded and snapshot targets and `ctx.is_file_targeted` is `False` for them; a run whose explicit targets are all excluded checks nothing rather than falling back to the whole workspace. They remain in the document catalog so link repair can still resolve to them. An invalid pattern is a policy error that fails the run before evaluation.
- **`--summary-only`**: text output prints one `[RULE_COUNTS: RULE-id errors=N warnings=N infos=N fixed=N]` line per rule instead of the `[VIOLATION: ...]` lines, keeping the `[SNAPSHOT]`, `[PHASE_OVERRIDE]`, `[PROMOTION]`, `[SUMMARY]` and `[OK]` lines. JSON output ignores the flag. The sentinel lines are listed in the [Rules Reference, CLI usage](reference.md#cli-usage).
- **Exit Status** (the devkit convention of [Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)):
  - `0`: All checks passed cleanly, or all fixable findings were successfully repaired.
  - `1`: Unresolved error violations. The run evaluated and found errors.
  - `2`: The run could not evaluate: rule loading failures, rule execution errors, invalid project policy, an invalid target, or a Git snapshot failure, each reported on stderr as an advisory with its code (see the [Rules Reference, Errors](reference.md#errors)). Execution errors take precedence over violations found in the same run. (Argument errors such as `--staged` with file arguments also exit `2`, as `ARGUMENT_INVALID` advisories; only click's syntax errors print a `Usage:` block.)

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

- `remaining=0` is the signal to delete the entry and return the rule to its default phase; the run then also reports a `RULES_PROMOTION_READY` notice on stderr whose `fix` names that edit.
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

- When the count reaches zero, flip the rule's declared `phase` to `linter` and drop `promote_to`; the `RULES_PROMOTION_READY` notice says so.

### Inspecting the Plan

`devkit rules phases` lists every rule with its default phase, effective phase, and pending transition. `--format json` emits `{"rules": [...], "errors": [...]}`, one object per rule with `rule_id`, `default_phase`, `effective_phase`, `overridden`, and `promote_to`, which is the stable surface for agents deciding whether an override can be retired.

`check --format json` prints `{"violations": [...], "errors": [...]}`; count the `violations` entries per `rule_id` to compute the same remaining totals.

`phases` and `explain` validate the whole `[rules]` policy (phase overrides, severity overrides and settings) as `check` does. `phases` prints the plan and exits `2` on any problem; `explain` exits `2` only for problems of the rule it describes (or an unknown rule ID, `ARGUMENT_INVALID`) and prints the problems of other rules as warnings.

---

## 5. Project Policy: Severity Overrides and Typed Settings

The `[rules]` table of `.devkit/config.toml` is the only place a project changes a distributed rule's behavior; managed rule files are checked against their receipt hash every time they load (a hand-edited copy is a `RULES_LOAD_FAILED` loading error) and are never edited.

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
- Each override is validated applied to the base values. Overrides that are valid alone but invalid together (one sets `lo`, another `hi`) can only be detected for a file both match: the run then fails with `RULES_SETTINGS_INVALID` (`RULE-id: <file>: the overrides matching this file (...) combine to invalid settings: ...`), exit code 2.
- `path` is workspace-relative. A standalone `**` matches zero or more segments; `*`, `?` and character classes match within one segment. Overrides apply in declaration order to every file they match, so later matching overrides win; keys an override omits keep the earlier value. Arrays replace.
- `ctx.settings(rule, path)` returns the effective dataclass for a file; `devkit rules explain <RULE-id>` prints the defaults, the configured values and each override.

---

## 6. Git Snapshot Gates

`check --staged` and `check --ci --base <ref>` evaluate a Git tree instead of the working directory:

| Mode | Tree evaluated | Comparison base | Changed files |
| --- | --- | --- | --- |
| `--staged` | the index (`git write-tree`) | `HEAD` (the empty tree on an unborn branch) | index vs `HEAD` |
| `--ci` | `HEAD` | `git merge-base <base> HEAD` | merge base vs `HEAD` |

The workspace root must be the Git work tree top level; a subdirectory is refused because Git reports tree and diff paths from the top level. The tree is materialized into a temporary directory which becomes the workspace root for the run: regular files keep their executable bit, symlinks whose target stays inside the tree are recreated (others are skipped) and each submodule becomes an empty directory, so links to them resolve as in the working tree. Consequences:

- Unstaged edits, untracked files and ignored local files do not exist for the gate.
- `.devkit/config.toml`, `.devkit/installation.json` and synchronized rules are read from the snapshot, so policy must be committed to take effect in a gate.
- Managed rule copies under `.devkit/managed/` are normally Git-ignored and absent from the tree. A rule file listed in the snapshot's receipt but missing from the snapshot is read from the working tree only when its SHA-256 matches the receipt's `files` entry; a missing or drifted file fails the gate with a `devkit sync` hint. A file present in the snapshot is checked against the same `files` entry, exactly as in a plain `check`. The committed receipt therefore still pins exactly which rule code a gate runs.
- The changed files of the diff are the targets, plus every Markdown file in the tree whose relative links point at a deleted path (or into a directory that lost files), so a deletion-only commit still reports the links it breaks. Deleted paths are reported in the `[SNAPSHOT: ...]` line. A snapshot with neither changed nor deleted files passes without loading rules.
- `--rules-dir` must lie inside the repository; it is read from the snapshot, so an unstaged edit of a custom rule does not change the result. A directory outside the repository, or one that is not in the snapshot (untracked or ignored), fails the run with exit code 2.
- Only regular files are targets. The rule engine's whole-workspace discovery is not Git-filtered inside a snapshot: the tree already holds tracked files only.
- Snapshot gates run the `linter` phase only and refuse file arguments, `--phase hygiene` and `fix`; `--staged` and `--ci` are mutually exclusive and `--base` applies to `--ci` only.

Two built-in linter rules exist for these gates and inspect explicit targets only: `RULE-secret-leak` (credential file names such as `.env`, `prod.env`, `id_rsa` and `*.key`; PEM and PGP private keys, AWS, GitHub, `sk-`, Stripe, Slack and Google key patterns, one finding per matching line) and `RULE-clean-artifacts` (compiled binaries, database files, logs above 1 MiB). In a plain `check` they inspect the files named on the command line and report nothing for a whole-workspace run, because a working tree scan would flag ignored local files.
