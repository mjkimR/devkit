# devkit.rules

A sequential Python rule engine for repository governance: deterministic checks
over a workspace, with autofix, project policy and Git snapshot gates. The engine
carries no document model of its own; rules that define identifier grammars,
frontmatter schemas or cross-reference semantics ship in bundles (`kind = "rule"`)
and load through the installation receipt.
Part of the `devkit` distribution (`devkit rules` CLI); requires Python 3.12 or later.

## Structure

```text
src/devkit/rules/
├── engine/                  # Rule contracts, registry, config, settings, phases, evaluation and autofix recheck
│   ├── discovery.py         # Rule assets recorded by devkit sync in .devkit/installation.json
│   ├── policy.py            # One validation of [rules] policy (phases, severities, settings)
│   ├── project.py           # run_project_rules: the one assembly of config, registry, context and evaluation
│   └── settings.py          # Typed per-rule settings with path-scoped overrides
├── workspace/               # File cache, Markdown links and fences, file catalog, task counter and Git snapshots
├── cli/                     # Click commands (commands.py) and rendering (output.py)
└── rules/
    ├── base.py              # Common rule implementation (settings, guide, promote_to)
    ├── markdown/            # Relative link validation and repair
    ├── hygiene/             # File length checks
    └── safety/              # Secrets and generated artifacts in the files under check
```

Tests live in `tests/` with the same feature groups. Library callers import the
public API from `devkit.rules`; built-in rule classes are exported by
`devkit.rules.rules`. Implementation modules live under the folders above.

## CLI usage

From this monorepo, run `just init`, then:

```bash
just rules-check
just rules-check --format json
just rules-check docs/rules/overview.md
just rules-check --staged                      # the exact staged tree (what the `rules-staged` commit gate runs)
just rules-check --ci --base origin/main       # HEAD against its merge base (CI gate)
just rules-fix --dry-run
just rules-fix
just rules-check --phase hygiene
just rules-phases
just rules-explain RULE-file-length
```

To install directly in another project:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"
uv run devkit rules check --workspace-root .
```

Without `--workspace-root` the commands use the project root of the current
directory: the nearest directory with a `.devkit/` folder, else the Git work
tree top level, else the current directory.

`check` never writes files. `fix --dry-run` reports the initial findings,
marking fixable ones `[FIXABLE]`, without running any fixer. `hygiene` includes linter rules as well as hygiene checks.
`phases` prints each rule's default and effective phase without evaluating.
`explain <RULE-id>` prints a rule's phase, severity, effective settings and its
guide document. Exit codes: `0` clean (or every fixable finding repaired), `1`
unresolved error violations, `2` the run could not evaluate: a rule loading or
execution failure, invalid project policy, an invalid target, or a Git snapshot
failure (`click` usage errors also exit `2`). Warnings alone do not fail the
command. `--format json` emits an array of violations to stdout; execution and
loading errors are reported separately to stderr.

Targets are workspace-relative or absolute paths inside the workspace. A file
is checked as is; a directory expands to every regular file under it, with the
same discovery as whole-workspace scans: dependency and cache directories
(`.git`, `.venv`, `node_modules`, ...) and the receipt-pinned copies under
`.devkit/managed/` and `.devkit/overrides/` are skipped, symlinks that resolve
outside the workspace are skipped, and inside a Git work tree only files Git
does not ignore are listed (tracked plus untracked, not ignored). A file named
explicitly is checked even when Git ignores it (for example a workflow unit
under `.devkit/transient/`). No file arguments checks the whole workspace; a directory with no
files checks nothing. A target that is neither an existing
file nor a directory inside the workspace fails with `INVALID_LINT_TARGET`
before any rule runs. Link repair still indexes every Markdown file in the
workspace, even when checking selected files.

`--summary-only` (text output) replaces the per-finding listing with one line
per rule (`RULE-id: N error(s), M warning(s)[, I info(s)][, K fixed]`), keeping the status
lines (`[SNAPSHOT]`, `[PHASE_OVERRIDE]`, `[PROMOTION]`) and the final summary.
Exit codes are unchanged; `--format json` ignores the flag.

## Git snapshot gates

`check --staged` evaluates the Git index (what a commit would contain) and
`check --ci --base <ref>` evaluates `HEAD` against its merge base with `<ref>`.
Both read the tree from Git, materialize it into a temporary directory and run
the linter phase there, with the changed files of the diff as targets, plus
every Markdown file whose relative links point at a path the snapshot deletes
(so a deletion-only commit still catches the links it breaks). Unstaged
edits, untracked files and local-only configuration cannot change the result:
`.devkit/config.toml`, the installation receipt and synchronized rules are all
taken from the snapshot. Managed rule copies under `.devkit/managed/` are
usually Git-ignored and therefore absent from the tree; the gate reads such a
file from the working tree only when its SHA-256 matches the hash recorded in
the snapshot's receipt. A rule file that is missing or differs from the receipt
fails the gate with a message to run `devkit sync` and commit the receipt.
Snapshot gates refuse file arguments, `--phase hygiene` and `fix`; `--base`
applies to `--ci` only. The workspace root must be the Git work tree top level
(a subdirectory is refused, because Git reports tree paths from the top level).
`--rules-dir` must lie inside the repository and is read from the snapshot, so
an unstaged edit of a custom rule cannot change the result; a directory outside
the repository or missing from the snapshot fails with exit code 2. Tracked
symlinks whose target stays inside the tree are recreated and submodules become
empty directories, so links to them resolve as in the working tree; only
regular files are targets. A snapshot with no changed or deleted files passes without
evaluating. The text output starts with a
`[SNAPSHOT: mode=... changed=N deleted=M]` line.

Two built-in linter rules exist for these gates and inspect explicit targets
only: `RULE-secret-leak` (credential file names, and PEM/PGP private keys, AWS,
GitHub, `sk-`, Stripe, Slack and Google key patterns, reported per line) and
`RULE-clean-artifacts` (compiled binaries, database files, logs above 1 MiB). A
run without targets reports nothing for them.

## Project configuration

Everything lives in the Git-tracked `.devkit/config.toml` under `[rules]`:

```toml
[rules]
exclude = ["docs/research/**", "CHANGELOG.md"]   # never targeted by any rule

[rules.phase_overrides]
RULE-markdown-link = "hygiene"          # only "hygiene": park a linter rule while debt is cleared

[rules.severity_overrides]
RULE-file-length = "error"              # error | warning | info

[rules.settings.RULE-file-length]       # typed settings declared by the rule
max_lines = 300
extensions = [".md"]

[[rules.settings.RULE-file-length.overrides]]
path = "docs/research/**"               # workspace-relative; ** matches zero or more segments
max_lines = 800
```

Entries for unknown rules, redundant overrides, unknown settings keys, wrong
types and invalid patterns fail the run before any rule executes, with the rule
ID in the message. Later matching overrides win and omitted keys inherit the
earlier value. Each override is validated against the base values; two
overrides that are only invalid together (for example one sets `lo`, another
`hi`) are reported for the first file both match, as an `Invalid settings`
error (exit code 2). Because managed files are hash-checked by `devkit sync`, this
table is the only place a project changes a distributed rule's behavior.

`exclude` lists workspace-relative patterns with the same `**` grammar as
settings overrides. An excluded path is never a target: it is dropped from
explicit, directory-expanded and snapshot targets, `ctx.is_file_targeted`
returns `False` for it, and naming only excluded files checks nothing. Excluded
files stay in the document catalog, so link repair can still point at them.

### Phase overrides and promotions

The `linter` phase is the gate for hooks and CI. To adopt a rule against a
codebase that already violates it, park it in `hygiene` while the debt is
cleared, then return it once `check --phase hygiene` reports `remaining=0`:

- A project moves a built-in or custom `linter` rule to `hygiene` through
  `[rules.phase_overrides]`. Only `"hygiene"` is accepted.
- A rule author declares a new `hygiene` rule with `promote_to=Phase.LINTER`
  to record that it becomes a linter rule once clean.

`check --phase hygiene` prints a `[PHASE_OVERRIDE: ...]` or `[PROMOTION: ...]`
line per pending transition with its remaining count. `devkit rules phases`
lists the full plan, and `--format json` emits one object per rule. Details are
in [Evaluation Lifecycle](evaluation-lifecycle.md).

## Synchronized rules

Rules shipped by a bundle (`kind = "rule"`) are recorded by `devkit sync` in
`.devkit/installation.json`. `devkit rules` loads every `.py` file listed under
such an asset (an override under `.devkit/overrides/` replaces the managed
copy) after the built-in rules and before `--rules-dir`, so no flag is needed.
A rule with the same ID as an earlier one replaces it. A listed file that does
not exist on disk is a loading error (exit code 2), not a silent skip: run
`devkit sync` to restore the managed copies.

This is also where document-model rules live. The built-in rules are limited to
what holds for any repository (relative links, file length, secrets and build
artifacts). A bundle that defines a documentation layout, an identifier grammar
or document relationships ships the rules that enforce them, together with the
guides and templates those rules cite. The engine's `DocumentCatalog` only
indexes Markdown paths, basenames and the frontmatter `id`, `title` and
`status` fields verbatim; it does not validate identifiers or extract references.

## Library and custom rules

`run_project_rules` evaluates a project exactly as `devkit rules check` does. It
reads the `[rules]` policy (including `exclude`) and registers the built-in
rules, the rules recorded in the installation receipt and the files under
`rules_dir`. It then builds the full `RuleContext` and evaluates. The CLI, the
`rules-staged` commit gate and the workflow engine's `lint-clean` check all
call it, so they cannot disagree on policy.

```python
from pathlib import Path
from devkit.rules import git_snapshot, run_project_rules

run = run_project_rules(Path("."))  # whole workspace, linter phase
run = run_project_rules(Path("."), targets=["docs"])  # files or directories; [] checks nothing
staged = git_snapshot(Path("."), staged=True)
run = run_project_rules(staged.root, snapshot=staged)  # the exact index, as `check --staged`
for violation in run.result.violations:
    print(violation.rule_id, violation.file, violation.line)
if run.errors:  # load_errors, then policy/execution errors
    raise SystemExit("; ".join(run.errors))
```

Keyword arguments are `targets`, `snapshot`, `phase`, `fix`, `dry_run` and
`rules_dir`. An invalid `[rules]` table raises `ConfigError`. An invalid
explicit target raises `TargetError`, and a `rules_dir` that a snapshot run
cannot read from the snapshot raises `RulesDirError`. Rule loading problems, such as a
malformed receipt or a missing or drifted synchronized rule, are returned in
`run.load_errors`, and no rule is evaluated. `run.failed` is true when there
are errors or unfixed error-severity violations. `build_project_registry` and
`expand_targets` expose the individual steps; `RuleContext`, `default_registry`
and `evaluate` remain available for callers that assemble a run themselves;
`validate_policy` checks a `[rules]` policy against loaded rules and returns
`PolicyError` messages that carry the rule ID.

Use `--rules-dir path/to/rules` to load Python files defining `BaseRule`
subclasses. Files load in sorted path order and classes in definition order;
imported classes and files or directories whose name starts with `_` or `.` are
ignored. A file that fails to import, or whose rule classes cannot be
instantiated without arguments, contributes no rule and is a loading error.
Custom rules are executable Python and should come from a trusted source.

```python
from dataclasses import dataclass, field

from devkit.rules import RuleContext, Violation
from devkit.rules.rules import BaseRule


@dataclass(frozen=True)
class BannedWordsSettings:
    banned: list[str] = field(default_factory=lambda: ["TODO"])


class BannedWordsRule(BaseRule):
    def __init__(self) -> None:
        super().__init__(
            id="RULE-banned-words",
            name="banned-words",
            description="Banned markers in documentation",
            settings=BannedWordsSettings(),
            guide="banned_words.md",
        )

    def validate_settings(self, settings: BannedWordsSettings) -> None:
        if not settings.banned:
            raise ValueError("banned must list at least one word")

    def check(self, ctx: RuleContext) -> list[Violation]:
        out = []
        for path in ctx.cache.find_files(ctx.workspace_root, extensions=(".md",)):
            rel = path.relative_to(ctx.workspace_root).as_posix()
            if not ctx.is_file_targeted(rel):
                continue
            settings: BannedWordsSettings = ctx.settings(self, rel)
            if any(word in ctx.cache.read_text(path) for word in settings.banned):
                out.append(Violation(self.id, rel, 1, "banned marker"))
        return out
```

`settings` is a frozen dataclass instance carrying the defaults; its fields may
be `int`, `float`, `str`, `bool` or `list[str]`. `ctx.settings(rule, path)`
returns the effective instance for a file after project overrides.
`validate_settings` rejects values the types alone cannot express. `guide` names
a Markdown file next to the rule module that `explain` prints and violations
cite.

Autofix rules also implement `fix(ctx) -> list[str]`, returning every modified
workspace-relative file path. Use `ctx.cache` for shared reads and writes:
`ctx.cache.write_text` writes exact UTF-8 bytes and refuses paths under
`.devkit/managed/` and `.devkit/overrides/`, and `ctx.cache.read_text_strict` returns `None` for a file that is
not valid UTF-8 and must not be rewritten. The evaluator invalidates returned
paths after each fix and rechecks all active rules once; a fixable finding is
marked fixed when the recheck reports fewer findings with the same rule, file
and message. A failed fix clears the cache and rechecks disk contents; it does
not roll back writes. A rule execution error prevents the autofix pass from
starting. Malformed frontmatter is not an error for the built-in rules: the
catalog records it in `frontmatter_errors` and keeps indexing.

## Current limits

Caches live for one evaluation session. Markdown links come from a CommonMark
inline-link scanner (angle-bracket destinations, titles, balanced parentheses,
escapes, code spans and fences); reference-style links and autolinks are not
checked, and links spanning several lines are not recognized. A link
destination is decoded (percent-encoding, escapes) and its `?query` and
`#fragment` are ignored when resolving the file. Settings fields are scalars
and string lists; nested tables are not supported. Snapshot gates materialize
the whole tree and read all blobs in one batch, so time and memory are
proportional to repository size. Phase overrides can only move a rule to `hygiene`; promoting a rule to
`linter` is done by editing its declared phase. Parallel workers are future work.

## Architectural Specifications & Deep-Dives

Detailed technical designs and protocols are documented in `docs/rules/`:

- [Rule Engine Architecture Overview](overview.md): Core subsystems, workspace cache, and Markdown file catalog.
- [Evaluation Lifecycle & Convergence](evaluation-lifecycle.md): Phased checks, project policy, snapshot gates, single-pass autofix, and convergence verification.
- [Rule Authoring Guide](rule-authoring.md): Protocols, settings, guides, finding models, cache APIs, and custom rule implementation.
- [Resource Taxonomy](../architecture/resource-taxonomy.md): Governance rules within the multi-tier agent asset taxonomy.
