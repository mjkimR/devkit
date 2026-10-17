# Rules library reference

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
raised ([Errors](rules.md#errors)). Rule loading problems, such as a malformed receipt or
a missing or drifted synchronized rule, are returned in `run.load_errors`, and
no rule is evaluated. `run.blocking_violations` (also on `EvaluationResult`)
are the unfixed error-severity violations, `run.ok` is true when there are
neither problems nor blocking violations, and `run.raise_for_problems()` raises
`RulesRunError` when there are problems. `build_project_registry` and
`expand_targets` expose the individual steps; `RuleContext`,
`default_rule_registry` and `evaluate_rules` serve callers that assemble a run
themselves (`CAP-GOV-rule-authoring`);
`validate_policy` checks a `[rules]` policy against loaded rules and returns
`PolicyError` objects that carry the rule ID.
`match_path(pattern, file)` and `validate_pattern(pattern)` are the path
pattern grammar of settings overrides (`path`): `**` is a whole segment matching
zero or more segments, and `*`, `?` and character classes match within one.
A rule whose settings take path patterns checks each in `validate_settings`
with `validate_pattern`, which raises `ValueError` for an empty or absolute
pattern, a backslash or `:`, an empty, `.` or `..` segment, or a partial `**`,
and matches workspace-relative paths with `match_path`.

### Link relocation

`relocate_links(root, files, relocation) -> LinkRelocationReport` rewrites the
relative inline links (`extract_links`) of `files` after paths moved, for any
caller that moves Markdown files. `LinkRelocation` says where things went:
`files` (old path to new path, exactly; a directory linked to as a whole too),
`directories` (old to new directory, for every path strictly beneath it; the
deepest key wins), `removed` (old paths that are gone), `file_origins` (new
file to the old file it was written as) and `directory_origins` (new directory
to the old one its files were written for). Paths are absolute or relative to
`root`; the maps take `str` or `Path` keys (`LinkRelocation[K]`, inferred from the arguments). A link into a moved-away path goes to its new location; a link of a
file written for another location is rewritten to reach the same target from
where the file is now. URLs, root-relative and fragment- or query-only
destinations are left alone, `#fragment` and `?query` are kept, and a
destination that still names its target keeps the author's spelling.
Destinations are read as `markdown_link` reads them (`local_target`: escapes
removed, percent-encoding decoded), and a new destination is written with
`devkit.rules.workspace.markdown.encode_destination(path, suffix='', angle=False)`, which percent-encodes `%`,
`\`, `#`, `?`, `<` and `>` and wraps a path with whitespace or parentheses in
`<...>` (unless the destination already is), so it reads back as the same path;
a trailing `/` (`docs/sub/`) is kept. A file that is a symbolic link is skipped
(`symlink`): it is an alias of its target, which is relocated at its own path
when it is among `files`. A file that resolves outside `root` or under
`.devkit/managed/` or `.devkit/overrides/` is never read or written
(`protected`). Changed files are replaced with `atomic_write_text`; nothing is
raised for a file. The report lists the rewritten `files`, each `RelocatedLink`
(`path`, `line`, `old`, `new` as written; `to_dict` keys `from` and `to`) and
each `UnresolvedLink` (`path`, `line`, `target`, `reason`), whose
`UnresolvedReason` is `unmapped` (a link into a moved-away path no mapping
covers, left as written), or, for a whole file (`line` `0`, empty `target`),
`unreadable`, `unwritable`, `symlink` or `protected`.

### Rule tests

`devkit.rules.testing` is what the tests in a rule's folder use
(`CAP-GOV-rule-authoring`):

- `load_rule(anchor, rule_id=None) -> Rule`: `anchor` is a test file
  (`__file__`) under `<rule folder>/tests/`, or the rule folder itself; the
  folder is loaded as a plugin package, as devkit loads a deployed rule (for a
  managed copy or its project override: with an installation receipt, exactly
  the package `devkit rules check` builds from it, only the files the receipt
  lists for the rule, verified against their hashes; without a receipt, the
  managed modules, each replaced by the override's file when it holds one), and
  the rule with `rule_id` (or the only one) is returned. Raises `RuleLoadError`
  (`RULES_LOAD_FAILED`) when the folder fails to load, is a deployed copy the
  receipt does not list or lists with a missing or drifted file, defines no
  rule, several without `rule_id`, or none with it.
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
`tests/` (an override without `tests/` uses the managed copy's, which `load_rule`
runs against the overridden modules), and `run_rule_tests(root, rules, pytest_args=())` returns one
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
`CAP-GOV-rule-authoring`;
loading order, skipped names and failure handling are in
`CAP-GOV-rule-authoring`,
and the rule contract (settings, `guide`, autofix) in the
`CAP-GOV-rule-authoring`.

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
