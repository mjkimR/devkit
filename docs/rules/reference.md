# devkit.rules

A sequential Python rule engine for repository governance: deterministic checks
over a workspace, with autofix, project policy and Git snapshot gates. The engine
carries no document model of its own; rules for identifier grammars, frontmatter
schemas or cross-references ship in bundles (`kind = "rule"`) and load through
the installation receipt. Part of the `agt-devkit` distribution (`devkit rules` CLI);
requires Python 3.12 or later.

Semantics: [Rule Engine Overview](overview.md) (architecture, layout),
[Evaluation Lifecycle](evaluation-lifecycle.md) (phases, targets, autofix,
policy, snapshot gates), [Rule Authoring Guide](rule-authoring.md) (rule
protocol, workspace API, rule sources), [Resource Taxonomy](../architecture/resource-taxonomy.md).

## CLI usage

```bash
devkit rules check [-w DIR] [-p linter|hygiene] [--rules-dir DIR] [--format text|json] [--summary-only] [TARGETS]...
devkit rules check --staged [-w DIR] [--rules-dir DIR] [--format text|json] [--summary-only]
devkit rules check --ci [--base REF] [-w DIR] [--rules-dir DIR] [--format text|json] [--summary-only]   # --base defaults to origin/main
devkit rules fix [-w DIR] [-p linter|hygiene] [--rules-dir DIR] [--dry-run] [--format text|json] [--summary-only] [TARGETS]...
devkit rules phases [-w DIR] [--rules-dir DIR] [--format text|json]
devkit rules explain RULE-ID [-w DIR] [--rules-dir DIR] [--format text|json]
devkit rules test [RULE-ID]... [-w DIR] [--rules-dir DIR] [--format text|json] [-- PYTEST-ARGS...]
```

In another project: `uv add "agt-devkit @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit"`,
then `uv run devkit rules check`. In this monorepo, `just rules-check`,
`just rules-fix`, `just rules-phases`, `just rules-explain` and `just rules-test`
pass their arguments through.

Without `-w`/`--workspace-root` the commands use the project root of the current
directory: the nearest directory with a `.devkit/` folder, else the Git work
tree top level, else the current directory.

- `check` never writes files. Targets, exclusions and phases:
  [Evaluation Lifecycle, section 3](evaluation-lifecycle.md#3-cli-execution-and-phases).
- `check --staged` evaluates the Git index (list it in the `verify-commands`
  commit gate to run it before every commit); `check --ci --base <ref>` evaluates `HEAD` against its merge base with
  `<ref>`. Both run the linter phase over the changed files of a materialized
  tree and refuse file arguments, `--phase hygiene` and `fix`
  ([Evaluation Lifecycle, section 6](evaluation-lifecycle.md#6-git-snapshot-gates)).
- `fix --dry-run` reports the initial findings, marking fixable ones
  `status=fixable`, without running any fixer.
- `phases` prints each rule's default and effective phase without evaluating.
- `explain <RULE-id>` prints a rule's phase, severity, effective settings, the
  instructions and playbooks it names as `related` (resolved to the file agents
  read) and its guide document.
- `test [RULE-id]...` runs the tests in each rule's folder (`<rule folder>/tests/`;
  every rule when none is named), with rules resolved as for `explain`
  (built-in, synchronized, `--rules-dir`). The rule folder is the directory of
  the module defining the rule class, or for a plugin package its root in the
  tree that module came from (a project override's copy when the class is
  defined there). Each tests directory runs once as
  `python -m pytest <tests> --import-mode=importlib -p no:cacheprovider -c <null> --rootdir <rule folder> --confcutdir <rule folder> [PYTEST-ARGS]`
  in a subprocess of the interpreter running devkit, from the workspace root but
  isolated from the project: no pytest configuration file is read and no
  `conftest.py` above the rule folder applies, so a rule's tests depend on its
  folder alone (a project's `addopts` or `filterwarnings = error` cannot break
  them), with
  `PYTHONDONTWRITEBYTECODE=1`: nothing is written next to the tests, so a run
  leaves `.devkit/managed/` untouched. The full output goes to a log file, as
  with `devkit run` ([Compact Reference](../compact/reference.md)). Arguments
  after `--` are passed to pytest. Loading and policy problems are reported as
  warnings; a rule that fails to load is not available to test. Writing the
  tests: [Rule Authoring Guide, section 6](rule-authoring.md#6-testing-a-rule).

### Exit codes

The devkit convention ([Errors, Exit Codes and Platforms](../architecture/overview.md#4-errors-exit-codes-and-platforms)):

| Command | `0` | `1` | `2` |
| --- | --- | --- | --- |
| `check`, `fix` | no unresolved error-severity violation (warnings and infos alone do not fail; `fix` repaired every fixable finding) | unresolved error violations remain | the run could not evaluate: usage or argument error, unreadable `.devkit/config.toml` (`CONFIG_INVALID`), invalid `[rules]` table, rule loading, policy or execution problem, invalid target, Git snapshot failure; takes precedence over violations found in the same run |
| `phases` | plan printed | - | usage or argument error, unreadable config or invalid `[rules]` table, any loading or policy problem (printed after the plan) |
| `explain` | rule described (loading and policy problems of other rules are reported as warnings) | - | usage or argument error (an unknown rule ID is `ARGUMENT_INVALID`), unreadable config or invalid `[rules]` table, a policy problem of the described rule |
| `test` | no selected rule's tests failed (`no-tests` is not a failure; loading and policy problems are warnings) | a selected rule's tests failed (any pytest exit code other than `0` and `5`) | usage or argument error (an unknown rule ID is `ARGUMENT_INVALID`), unreadable config or invalid `[rules]` table, pytest not importable (`RULES_TEST_UNAVAILABLE`); a run interrupted by signal `N` exits `128 + N` |

A command that collects loading, policy or execution problems exits with the
highest `exit_code` among them (`2` for every such problem today). Argument
checks beyond click's syntax (`--staged` with `--ci`, `--base` without `--ci`,
file arguments or `--phase hygiene` with a snapshot, a `--rules-dir` or
`--workspace-root` that is not an existing directory, an unknown rule ID) are
`ARGUMENT_INVALID` (`INPUT_ERROR`); only click's own syntax errors print a
`Usage:` block.

### Output

In text mode every problem is printed on stderr as an Agent Advisory Protocol
block with its code ([Errors](#errors)); problems that do not fail a command are
`[WARN]` blocks after the result. Under `--format json` the JSON object carries
them and nothing is printed on stderr
([Agent-First Output](../architecture/agent-output.md)).

Text output is one `[KIND: ...]` sentinel line per fact; free text (messages,
remediations, descriptions) is written as a JSON string so every line stays
parseable:

```text
[SNAPSHOT: mode=staged tree=3f2a9c1d0b7e base=9e8d7c6b5a4f changed=2 deleted=0]
[VIOLATION: RULE-markdown-link severity=error file=docs/a.md line=3 status=fixable message="Broken relative link: wrong/setup.md" remediation="..." guide=...]
[SUMMARY: errors=1 warnings=0 infos=0 fixed=0]
```

- `check` and `fix`: a `[SNAPSHOT: ...]` line first in a snapshot gate; one
  `[VIOLATION: ...]` per finding (`status` is `open`, `fixable` or `fixed`;
  `remediation` and `guide` appear when the rule gives them); a hygiene run's
  `[PHASE_OVERRIDE: ...]`/`[PROMOTION: ...]` lines (whole-workspace runs only)
  ([Evaluation Lifecycle, section 4](evaluation-lifecycle.md#4-phase-transitions-overrides-and-promotions))
  and a `RULES_PROMOTION_READY` notice on stderr when one has `remaining=0`;
  then `[SUMMARY: errors=N warnings=N infos=N fixed=N]` counting unfixed
  findings per severity and the fixed ones; then `[OK: ...]` when the command
  exits `0`. A run that could not evaluate and found nothing prints no summary.
- `--summary-only` replaces the `[VIOLATION: ...]` lines with one
  `[RULE_COUNTS: RULE-id errors=N warnings=N infos=N fixed=N]` line per rule
  and keeps the other lines. Exit codes are unchanged; `--format json` ignores
  the flag.
- `phases`: one `[PHASE: RULE-id default=... effective=... overridden=yes|no promote_to=...]` line per rule.
- `explain`: `[RULE: ...]`, `[DESCRIPTION: ...]`, one
  `[RELATED: <bundle>:<asset-id> kind=instruction|playbook path=<file>]` per related
  asset (`kind=- path=-` when it is not deployed), one
  `[SETTING: key=value default=value]` per setting and one
  `[SETTING_OVERRIDE: path=... key=value ...]` per override (or
  `[SETTINGS: none]`), then the guide document as written.
- `test`: one `[RULE_TEST: RULE-id tests=<dir> result=passed|failed|no-tests|interrupted exit=<n> log=<path>]`
  per rule, in the order named (sorted by ID when none is named); `tests` is
  workspace-relative when inside the workspace, else absolute, and `exit` and
  `log` are `-` when there is no tests directory (`exit=5`, pytest's "no tests
  collected", is also `no-tests`). After a failed run comes compact's failure
  view: `[RULE_TEST_SUMMARY: RULE-id "<pytest summary>"]` lines,
  `[RULE_TEST_FAILURE: RULE-id "<test id>" kind=failed|error message=...]` for
  the failed tests the excerpt cuts out, and
  `[RULE_TEST_OUTPUT: RULE-id shown=N omitted=N filtered=N]` followed by the
  head-and-tail excerpt (pytest's short test summary names every failed test).
  Rules defined in one package share one run, shown once. Last,
  `[SUMMARY: rules=N passed=N failed=N no_tests=N interrupted=N]`. An interrupted run (Ctrl-C, `SIGTERM`,
  `SIGHUP`) ends the command: the rules run so far are printed, the interrupted one `result=interrupted` with the
  log up to the interruption, and the command exits `128 + N`. The advisories of the pytest runs (compact's) are
  reported with the warnings.

```text
[RULE_TEST: RULE-markdown-link tests=packages/devkit/src/devkit/rules/rules/markdown_link/tests result=passed exit=0 log=/tmp/devkit-run-501/a8ae3cd8d8a1/20261013-135346-python3-m-uysb0n32.log]
[RULE_TEST: RULE-doc-heading tests=rules/doc_heading/tests result=failed exit=1 log=/tmp/devkit-run-501/a8ae3cd8d8a1/20261013-135346-python3-m-8k9ofwgf.log]
[RULE_TEST_SUMMARY: RULE-doc-heading "1 failed, 1 passed in 0.04s"]
[RULE_TEST_OUTPUT: RULE-doc-heading shown=1188 omitted=0 filtered=4]
...
FAILED rules/doc_heading/tests/test_rule.py::test_fails - AssertionError: expected a ...
========================= 1 failed, 1 passed in 0.04s ==========================
[SUMMARY: rules=2 passed=1 failed=1 no_tests=0 interrupted=0]
```

`--format json` prints exactly one object on stdout:
`{"violations": [...], "errors": [...], "notices": [...]}` (`check`, `fix`; each violation carries `rule_id`,
`file`, `line`, `column`, `message`, `fixable`, `fixed`, `severity`, `phase`, and `remediation` and `guide` when
the rule gives them, as the `[VIOLATION: ...]` line does),
`{"rules": [...], "errors": [...]}` with one object per rule carrying
`rule_id`, `default_phase`, `effective_phase`, `overridden` and `promote_to`
(`phases`), `{"rule": {...}, "notices": [...], "errors": [...]}`
(`explain`), or `{"results": [...], "summary": {...}, "notices": [...]}`
(`test`: one result per rule with `rule_id`, `tests`, `result`, `exit_code`
and `log`, `null` without a run, and for a failed run `summaries`, `failures`
(`test`, `kind`, `message`), `output` (the excerpt) and `omitted`
(`failures`, `output`), otherwise empty or `null`; `summary` has `rules`,
`passed`, `failed`, `no_tests` and `interrupted`). `errors` holds the collected problems and `notices` the warnings
and notices, as `to_dict()` objects (each with its `code`, `level`,
`exit_code`, `rule_id` and advisory). A command that fails before it has a
result prints `{"error": {...}}` instead.

## Project configuration

Everything lives in the Git-tracked `.devkit/config.toml` under `[rules]`, the
only place a project changes a distributed rule's behavior. Semantics and
validation: [Evaluation Lifecycle](evaluation-lifecycle.md), sections 3
(`exclude`), 4 (phase overrides) and 5 (severity overrides, settings).

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
types and invalid patterns fail the run (exit code `2`) before any rule
executes, with the rule ID in the message.

## Built-in rules

| Rule | Module | Phase, severity | Checks | Guide |
| --- | --- | --- | --- | --- |
| `RULE-markdown-link` | `rules.markdown_link` | linter, error | relative Markdown links point at existing files; autofix rewrites a broken link when exactly one Markdown file has its basename | [guide.md](../../packages/devkit/src/devkit/rules/rules/markdown_link/guide.md) |
| `RULE-file-length` | `rules.file_length` | hygiene, warning | files above `max_lines` (settings `max_lines`, `extensions`) | [guide.md](../../packages/devkit/src/devkit/rules/rules/file_length/guide.md) |
| `RULE-secret-leak` | `rules.secret_leak` | linter, error | credential file names and private key or token patterns in explicit targets | [guide.md](../../packages/devkit/src/devkit/rules/rules/secret_leak/guide.md) |
| `RULE-clean-artifacts` | `rules.clean_artifacts` | linter, error | compiled binaries, database files and logs above 1 MiB in explicit targets | [guide.md](../../packages/devkit/src/devkit/rules/rules/clean_artifacts/guide.md) |

The guide of each rule is canonical for its behavior; `devkit rules explain
<RULE-id>` prints it. The safety rules report nothing for a run without
explicit targets.

### Built-in authoring bundle

The opt-in bundle `authoring` (sources in `src/devkit/rules/authoring/bundle/`)
is deployed only when a project selects it. Both rules run in the `hygiene`
phase only, so they never block a commit or a CI linter run:

```bash
uv run devkit add authoring                          # both presets (default preset `all`)
uv run devkit add authoring:agent-guide-authoring    # one of them
uv run devkit rules check --phase hygiene
```

| Preset | Rule (warning, hygiene) | Playbook |
| --- | --- | --- |
| `skill-authoring` | `RULE-skill-document-size`: a skill or playbook Markdown file above `max_bytes` (8192 UTF-8 bytes) ([guide](../../packages/devkit/src/devkit/rules/authoring/bundle/rules/skill_document_size/guide.md)) | `skill-authoring`: router structure for new skills, the four restructuring steps, helper-script rules |
| `agent-guide-authoring` | `RULE-agent-guide-size`: an `AGENTS.md` or `CLAUDE.md` above `max_bytes` (8192 UTF-8 bytes), reporting the devkit guidance block's share ([guide](../../packages/devkit/src/devkit/rules/authoring/bundle/rules/agent_guide_size/guide.md)) | `agent-guide-authoring`: what stays in an always-loaded guide (no structure trees; module specifics only as links), where the rest moves, per-host loading |

Both remediations name the playbook and its `uv run devkit playbook search`
query. The rules are bundle assets (one plugin package directory each) loaded
from the receipt, never imported from the package; their guides define the
checked paths and settings.

## Library

`run_project_rules` evaluates a project exactly as `devkit rules check` does: it
reads the `[rules]` policy, registers the built-in rules, the receipt's rules and
the plugin packages under `rules_dir`, builds the full `RuleContext` and evaluates.
`load_project_rules(root, rules_dir)` is the loading half on its own: it returns
a `ProjectRules` with the `config`, the `registry`, the settings `resolvers`,
`load_errors` and `policy_errors`, without evaluating (`phases` and `explain`
use it).

```python
from pathlib import Path
from devkit.rules import RulesRunError, git_snapshot, run_project_rules

run = run_project_rules(Path("."))  # whole workspace, linter phase
run = run_project_rules(Path("."), targets=["docs"])  # files or directories; [] checks nothing
staged = git_snapshot(Path("."), staged=True)
run = run_project_rules(staged.root, snapshot=staged)  # the exact index, as `check --staged`
for violation in run.result.violations:
    print(violation.rule_id, violation.file, violation.line)
for problem in run.errors:  # load_errors, then policy/execution errors
    print(problem.code, problem.rule_id, problem)
run.raise_for_problems()  # RulesRunError (RULES_RUN_FAILED), one detail per problem
for violation in run.blocking_violations:  # unfixed error-severity findings
    print(violation.file, violation.message)
```

Keyword arguments are `targets`, `snapshot`, `phase`, `fix`, `dry_run` and
`rules_dir`. Configuration, target, rules-directory and snapshot failures are
raised ([Errors](#errors)). Rule loading problems, such as a malformed receipt or
a missing or drifted synchronized rule, are returned in `run.load_errors`, and
no rule is evaluated. `run.blocking_violations` (also on `EvaluationResult`)
are the unfixed error-severity violations, `run.ok` is true when there are
neither problems nor blocking violations, and `run.raise_for_problems()` raises
`RulesRunError` when there are problems. `build_project_registry` and
`expand_targets` expose the individual steps; `RuleContext`,
`default_rule_registry` and `evaluate_rules` serve callers that assemble a run
themselves ([Rule Authoring Guide, section 5](rule-authoring.md#5-rule-sources-and-registration));
`validate_policy` checks a `[rules]` policy against loaded rules and returns
`PolicyError` objects that carry the rule ID.

### Rule tests

`devkit.rules.testing` is what the tests in a rule's folder use
([Rule Authoring Guide, section 6](rule-authoring.md#6-testing-a-rule)):

- `load_rule(anchor, rule_id=None) -> Rule`: `anchor` is a test file
  (`__file__`) under `<rule folder>/tests/`, or the rule folder itself; the
  folder is loaded as a plugin package, as devkit loads a deployed rule, and
  the rule with `rule_id` (or the only one) is returned. Raises `RuleLoadError`
  (`RULES_LOAD_FAILED`) when the folder fails to load, defines no rule, several
  without `rule_id`, or none with it.
- `check(rule, root, files=None, *, targets=(), fix=False, dry_run=False, settings=None, phase=None) -> list[Violation]`:
  writes `files` (workspace-relative path to `str` or `bytes`) under `root`,
  evaluates the one rule with `evaluate_rules` (phase defaults to the rule's
  declared phase; `targets` are files or directories, none means the whole
  workspace) and returns its violations with their effective phase and
  severity; raises `RulesRunError` (`RULES_RUN_FAILED`) carrying the problems
  when the evaluation reports any. `settings` is the
  `[rules.settings.<RULE-id>]` table as values, path overrides under
  `"overrides"`; it goes through the configuration parser (`RulesConfigError`
  for a malformed shape) and the `SettingsResolver` of a project run.
- `evaluate(...)`: the same arguments, returning the whole `EvaluationResult`
  without raising for its problems; `write_files(root, files)` and
  `rule_directory(anchor)` are the steps on their own.

`devkit.rules.engine.rule_tests` is the command's library half:
`rule_folder(rule)` and `tests_directory(rule)` locate a rule's folder and
`tests/`, and `run_rule_tests(root, rules, pytest_args=())` returns one
`RuleTestRun` per rule (`rule_id`, `tests`, `result` as `RuleTestResult`,
`run` as the `devkit.compact.CommandRun`, `exit_code`), raising
`RulesTestUnavailableError` when pytest is not importable; it never prints.
`devkit.compact` is imported only when tests run.

### Custom rules

`--rules-dir path/to/rules` (`rules_dir`) loads each immediate subdirectory
as one plugin package: a directory holding the rule module, optional
`__init__.py`, helper modules imported relatively, the guide, resources and
tests, for example `rules/banned_words/rule.py` with `rules/banned_words/guide.md`
and `rules/banned_words/tests/` beside it. A `.py` file directly in the
directory is a `RULES_LOAD_FAILED` loading error whose fix moves it into
`<rules-dir>/<name>/`. The package layout is in
[Implementing a Custom Rule](rule-authoring.md#3-implementing-a-custom-rule-example);
loading order, skipped names and failure handling are in
[Rule sources](rule-authoring.md#5-rule-sources-and-registration),
and the rule contract (settings, `guide`, autofix) in the
[Rule Authoring Guide](rule-authoring.md#1-rule-protocols-and-contracts).

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
            guide="guide.md",
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

## Errors

Every error the library raises or collects is an `AdvisoryError`
(`devkit.advisory`) and a `RulesError`; branch on `error.code`, never on the
message. Raised errors stop a run before any rule is evaluated; collected
problems (`RuleProblem`, with `rule_id` naming the rule they concern or `None`)
are returned in `RuleRegistry.errors`, `ProjectRun.load_errors` and
`EvaluationResult.errors`, and `str(problem)` is the message.

| Class | Code | Mode | When |
| --- | --- | --- | --- |
| `RulesConfigError` | `RULES_CONFIG_INVALID` | `INPUT_ERROR` | `[rules]` in `.devkit/config.toml` is malformed (raised; a subclass of the core `ConfigError`, which is raised unchanged as `CONFIG_INVALID` when the file itself cannot be read or parsed) |
| `TargetError` | `RULES_TARGET_INVALID` | `INPUT_ERROR` | an explicit target is outside the workspace (directly or through a symlink) or does not exist (raised) |
| `RulesDirError` | `RULES_DIR_INVALID` | `INPUT_ERROR` | a snapshot run cannot read `--rules-dir` from the snapshot: outside the repository or not in the snapshot (raised) |
| `SnapshotError` | `RULES_SNAPSHOT_FAILED` | `INPUT_ERROR` (not a work tree top level, unknown `--base`) or `MAINTENANCE` (Git failure) | a Git snapshot cannot be taken or materialized (raised) |
| `PinnedWriteError` | `RULES_PINNED_WRITE_REFUSED` | `BLOCKED` | a fixer tried to write a receipt-pinned copy under `.devkit/managed/` or `.devkit/overrides/` |
| `RuleDefinitionError` | `RULES_DEFINITION_INVALID` | `MAINTENANCE` | a rule class declares an invalid `promote_to` (raised at construction) |
| `PolicyError` | `RULES_POLICY_INVALID` | `INPUT_ERROR` | a phase or severity override or settings entry names an unknown rule or changes nothing (collected) |
| `SettingsError` | `RULES_SETTINGS_INVALID` | `INPUT_ERROR`, or `MAINTENANCE` for a defect in the rule's settings declaration | settings do not type-check or `validate_settings` rejects them (collected; a `PolicyError`) |
| `RuleLoadError` | `RULES_LOAD_FAILED` | `MAINTENANCE`; `AUTO` when missing | a rule package fails to load (or a `.py` file sits directly in `--rules-dir`), or the receipt is malformed or lists a missing or drifted rule (collected; `fix` names `devkit sync`); a missing rule file (a fresh clone or worktree lacks the ignored managed copies) is `AUTO` with the fix `devkit sync` |
| `RuleExecutionError` | `RULES_EXECUTION_FAILED` | `MAINTENANCE` | a rule raised while checking or fixing; `[TARGET]` is the file defining it (collected) |
| `RulesTestUnavailableError` | `RULES_TEST_UNAVAILABLE` | `MAINTENANCE` | `devkit rules test` (or `run_rule_tests`) cannot import pytest in the interpreter running devkit; `fix`: `uv add --dev pytest` (raised before any test runs) |
| `RulesRunError` | `RULES_RUN_FAILED` | `MAINTENANCE` | raised by `ProjectRun.raise_for_problems()` for callers that need one error for a failed run, such as the workflow engine's `lint-clean`; `problems` keeps the collected problems |

`expand_targets`, `RuleContext` (targets outside the workspace) and
`ctx.settings(rule, path)` raise `TargetError` too. Passing `targets` or
`fix=True` together with a snapshot, or a snapshot taken from another root, is
a programming error and raises `ValueError`. A rule's `validate_settings`
raises `ValueError`, which the engine reports as `SettingsError`.

Warnings and notices are returned, never raised, at level `WARNING` or
`NOTICE` ([Agent Advisory Protocol](../advisory/protocol.md#2-levels)):

| Code | Level | When |
| --- | --- | --- |
| `RULES_PROMOTION_READY` | `NOTICE` | a whole-workspace `hygiene` run finds a phase override or promotion with `remaining=0`; `target_files` names the files to edit (`.devkit/config.toml` for an override, the file declaring the rule for a promotion), `fix` the edit (drop the `[rules.phase_overrides]` entry, or switch the declared phase to its `promote_to`) |
| `RULES_RELATED_UNRESOLVED` | `NOTICE` | `explain` of a rule whose `related` entry names an asset that is not deployed (`fix`: `devkit add <bundle>`) or is neither an instruction nor a playbook; the entry is printed with `kind=- path=-` |
| any collected problem's code | `WARNING` | `explain` reports a loading or policy problem that does not concern the described rule, `test` any loading or policy problem (`with_level`; the code is unchanged) |

Rule violations of severity `warning` or `info` are findings, not advisories:
they are results on stdout and never affect `--strict`.

## Current limits

- Caches live for one evaluation session; parallel workers are future work.
- Markdown links come from a CommonMark inline-link scanner (angle-bracket
  destinations, titles, balanced parentheses, escapes, code spans and fences);
  reference-style links and autolinks are not checked, and links spanning
  several lines are not recognized. A destination is decoded (percent-encoding,
  escapes) and its `?query` and `#fragment` are ignored when resolving the file;
  a repaired destination percent-encodes `%`, `\`, `#`, `?`, `<` and `>` so it
  decodes back to the candidate's path.
- Settings fields are scalars and string lists; nested tables are not supported.
- Snapshot gates materialize the whole tree, so time and disk use grow with
  repository size; blobs are streamed from one `git cat-file --batch` process
  and written as they arrive.
- Phase overrides can only move a rule to `hygiene`; promoting a rule to
  `linter` is done by editing its declared phase.
