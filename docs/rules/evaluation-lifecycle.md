# Evaluation Lifecycle and Autofix Convergence

How a run selects targets and rules, applies project policy, repairs and rechecks, and evaluates Git snapshots.
Related: [Rule Engine Overview](overview.md), [Rule Authoring Guide](rule-authoring.md),
[Rules Reference](reference.md) (commands, output, exit codes, error codes).

## 1. Lifecycle

1. Build the `RuleContext` and `WorkspaceCache`; a Git snapshot gate first materializes the staged or CI tree and uses it as the root (section 6).
2. Load rules ([Rule Authoring Guide, section 5](rule-authoring.md#5-rule-sources-and-registration)) and validate the project policy: phase overrides, severity overrides, typed settings and `exclude` patterns. Any loading or policy problem stops the run before a rule executes.
3. Select the active rules for the phase (`linter` or `hygiene`) and run their checks, collecting violations and execution errors.
4. With `fix` (not `--dry-run`) and no execution error, run each `Autofixable.fix()` once, sequentially, then recheck all active rules once (section 2).
5. Return the final violations and errors.

## 2. Autofix and Convergence

- **One repair pass, one recheck.** There is no repair loop, so a run always terminates with a predictable cost.
- **Cache invalidation.** The paths a fixer returns are invalidated in `WorkspaceCache` (bytes, text, frontmatter, links) and dependent catalog indexes are refreshed before the recheck. A failed fix clears the whole cache and rechecks disk contents; it does not roll back writes.
- **Convergence.** A fixable finding is marked fixed only when the recheck reports fewer findings with the same rule, file and message (lines may move during a fix); whatever a failed or partial fix left is reported as remaining.
- **No unsafe writes.** A file that is not valid UTF-8 is left untouched, writes keep every other byte (line endings included), and nothing under `.devkit/managed/` or `.devkit/overrides/` (copies pinned by the installation receipt) is written.
- **Malformed frontmatter is not a run failure.** The document catalog records it in `frontmatter_errors` and keeps indexing; a bundle rule that requires valid frontmatter reports it as its own violation.
- **Problems go to stderr.** Rule import or runtime exceptions fail the command as advisories on stderr, so stdout stays parseable.

## 3. CLI Execution and Phases

Command synopsis, output and exit codes: [Rules Reference, CLI usage](reference.md#cli-usage).

- **Phases**:
  - `linter`: relative Markdown links, the safety checks on explicit targets, and every rule declared in this phase. The Git snapshot gates evaluate this phase: `check --staged` (also run by the `rules-staged` pre-commit gate of [`devkit gate`](../gate/overview.md#2a-built-in-gates)) and `check --ci`.
  - `hygiene`: the `linter` rules plus file length warnings, every rule declared in this phase, and every rule parked there by a project phase override.
- **Targets**: workspace-relative or absolute paths inside the workspace. A file is checked as is, even when Git ignores it (for example a workflow unit under `.devkit/transient/`). A directory expands recursively to its regular files with the same discovery as a whole-workspace scan: dependency and cache directories (`.git`, `.venv`, `node_modules`, ...), `.devkit/managed/` and `.devkit/overrides/`, and symlinks resolving outside the workspace are skipped, and inside a Git work tree only files Git does not ignore are listed (tracked plus untracked; names are compared in Unicode NFC, so a file whose on-disk name is decomposed, as macOS may store it, still matches Git's precomposed name). No targets means the whole workspace; a directory without files checks nothing. A target that is neither an existing file nor a directory inside the workspace, including a file or directory symlink that resolves outside it, fails with `RULES_TARGET_INVALID` before any rule runs. Link repair still indexes every Markdown file in the workspace when checking selected files.
- **Exclusions**: `exclude` under `[rules]` lists workspace-relative patterns (the `**` grammar of settings overrides, section 5) that no rule targets. Excluded paths are removed from explicit, directory-expanded and snapshot targets, and `ctx.is_file_targeted` is `False` for them; a run whose explicit targets are all excluded checks nothing rather than falling back to the whole workspace. They stay in the document catalog, so link repair can still resolve to them. An invalid pattern is a policy error.

## 4. Phase Transitions: Overrides and Promotions

A rule's declared `phase` is its default. The `linter` phase is the gate for hooks and CI; two mechanisms let a rule sit in `hygiene` while existing debt is cleared, without editing the rule.

### Project Phase Overrides (`[rules.phase_overrides]`)

A project parks any `linter` rule (built-in, synchronized or custom) in `hygiene` through its Git-tracked `.devkit/config.toml`:

```toml
[rules.phase_overrides]
RULE-markdown-link = "hygiene"
```

- Only `"hygiene"` is accepted. An override for an unknown rule, or for a rule that already runs in `hygiene`, is a policy error.
- `linter` runs skip the rule. Whole-workspace `hygiene` runs include it and print its remaining violation count:

  ```text
  [PHASE_OVERRIDE: RULE-markdown-link=hygiene default=linter source=.devkit/config.toml remaining=3]
  ```

- At `remaining=0` the run also reports a `RULES_PROMOTION_READY` notice on stderr whose `fix` is to delete the entry, returning the rule to its default phase.
- A `hygiene` run limited to explicit targets still evaluates the rule but prints no count and no notice: violations in the selected files say nothing about the rest of the workspace.
- Violations report the phase the rule ran in (`phase: "hygiene"`), not its declared default.

### Rule Promotions (`promote_to`)

A new rule meeting many existing violations is declared `phase=Phase.HYGIENE` with `promote_to=Phase.LINTER` ([declaration](rule-authoring.md#optional-promote_to)) instead of blocking every session at once. Whole-workspace `hygiene` runs print its remaining count:

```text
[PROMOTION: RULE-no-todo=hygiene promote_to=linter remaining=12]
```

At zero, the `RULES_PROMOTION_READY` notice says to flip the declared `phase` to `linter` and drop `promote_to`.

`devkit rules phases` lists every rule's default and effective phase and pending transition without evaluating; its JSON form is the stable surface for deciding whether an override can be retired.

## 5. Project Policy: Severity Overrides and Typed Settings

The `[rules]` table of `.devkit/config.toml` is the only place a project changes a distributed rule's behavior: managed rule files are checked against their receipt hash every time they load (a hand-edited copy is a `RULES_LOAD_FAILED` loading error) and are never edited. `phases` and `explain` validate the whole policy as `check` does.

### Severity Overrides (`[rules.severity_overrides]`)

```toml
[rules.severity_overrides]
RULE-file-length = "error"
```

The value is `error`, `warning` or `info`. Violations report the effective severity, and `error` violations fail the command. An entry for an unknown rule, or one equal to the declared severity, is a policy error.

### Typed Settings (`[rules.settings.<RULE-id>]`)

A rule declares typed settings with defaults ([Rule Authoring Guide](rule-authoring.md#optional-settings-and-validate_settings)); a project configures them, optionally per path:

```toml
[rules.settings.RULE-file-length]
max_lines = 300
extensions = [".md"]

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"
max_lines = 800
```

- Every layer is validated before any rule runs: unknown keys, wrong types (`true` is not an integer, `"10"` is not a number), explicit nulls and unsupported patterns fail with the rule ID in the message, and so does a rejection by the rule's `validate_settings`. Settings for an unknown rule, or for a rule that declares none, are errors.
- Each override is validated applied to the base values. Overrides valid alone but invalid together (one sets `lo`, another `hi`) are detected only for a file both match: the run then fails with `RULES_SETTINGS_INVALID` (`RULE-id: <file>: the overrides matching this file (...) combine to invalid settings: ...`), exit code 2.
- `path` is workspace-relative. A standalone `**` matches zero or more segments; `*`, `?` and character classes match within one segment. Overrides apply in declaration order to every file they match, so later matching overrides win; keys an override omits keep the earlier value. Arrays replace.
- `ctx.settings(rule, path)` returns the effective dataclass for a file; `devkit rules explain <RULE-id>` prints the defaults, the configured values and each override.

## 6. Git Snapshot Gates

`check --staged` and `check --ci --base <ref>` evaluate a Git tree instead of the working directory:

| Mode | Tree evaluated | Comparison base | Changed files |
| --- | --- | --- | --- |
| `--staged` | the index (`git write-tree`) | `HEAD` (the empty tree on an unborn branch) | index vs `HEAD` |
| `--ci` | `HEAD` | `git merge-base <base> HEAD` | merge base vs `HEAD` |

The workspace root must be the Git work tree top level; a subdirectory is refused because Git reports tree and diff paths from the top level. The tree is materialized into a temporary directory that becomes the workspace root: regular files keep their executable bit, symlinks whose target stays inside the tree are recreated (others are skipped) and each submodule becomes an empty directory, so links to them resolve as in the working tree. Consequences:

- Unstaged edits, untracked files and ignored local files do not exist for the gate.
- `.devkit/config.toml`, `.devkit/installation.json` and synchronized rules are read from the snapshot, so policy must be committed to take effect in a gate.
- Managed rule copies under `.devkit/managed/` are normally Git-ignored and absent from the tree. A rule file listed in the snapshot's receipt but missing from the snapshot is read from the working tree only when its SHA-256 matches the receipt's `files` entry; a missing or drifted file fails the gate (`RULES_LOAD_FAILED`) with the fix to run `devkit sync` and commit the receipt. A file present in the snapshot is checked against the same entry, as in a plain `check`, so the committed receipt pins exactly which rule code a gate runs.
- The targets are the changed files of the diff, plus every Markdown file in the tree whose relative links point at a deleted path (or into a directory that lost files), so a deletion-only commit still reports the links it breaks. Only regular files are targets. Whole-workspace discovery is not Git-filtered inside a snapshot: the tree holds tracked files only. A snapshot with neither changed nor deleted files passes without loading rules.
- `--rules-dir` must lie inside the repository and is read from the snapshot, so an unstaged edit of a custom rule cannot change the result. A directory outside the repository, or one that is not in the snapshot (untracked or ignored), fails with `RULES_DIR_INVALID`, exit code 2.
- Snapshot gates run the `linter` phase only and refuse file arguments, `--phase hygiene` and `fix`; `--staged` and `--ci` are mutually exclusive and `--base` applies to `--ci` only.

The built-in safety rules `RULE-secret-leak` and `RULE-clean-artifacts` ([catalog](reference.md#built-in-rules)) inspect explicit targets only, so they matter chiefly in these gates: a whole-workspace `check` reports nothing for them, because a working tree scan would flag ignored local files.
