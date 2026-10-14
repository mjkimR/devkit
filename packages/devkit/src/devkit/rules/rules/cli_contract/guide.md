# [RULE-cli-contract] CLI Citations Name Existing Commands

## 1. Overview

Documents, skills and instructions cite the `devkit` command line, and agents run what they cite. devkit changes its
commands in place, so a renamed command or a removed option silently leaves wrong citations behind. This rule walks
every citation through the command tree of the running `devkit`, plugin commands (`devkit.commands` entry points)
included, and reports the ones it does not have.

- **Phase and severity**: `linter`, `error`. It runs in `devkit rules check`, the commit gate (`check --staged`) and
  CI (`check --ci`).
- **What is checked**: in the Markdown files the run targets, every inline code span and every line of a fenced code
  block that invokes `devkit`, optionally after `$ ` and a launcher (`uv run [options]`, `uvx`, `python -m`). A fenced
  line ending in `\` continues on the next line. Words of the command path must be subcommands of the group before
  them; options (`--name`, `-x`, also written `--name=value`, `[--a|--b]` or `--name/-n`) must belong to the command
  they follow, the help option included. An option that takes a value consumes the next word.
- **What is not**: prose (`devkit` outside code), names such as `devkit.rules` or `devkit-agt`, anything after `--`,
  a pipe, a list operator, a redirection or a `#` comment, option values, arguments and placeholders. A placeholder
  where a subcommand belongs (`devkit spec <command>`) ends the check of that citation, and a command that passes
  unknown options through (`devkit run`) accepts any option.
- **Outside `devkit`**: the tree is the command line the check runs under. A library caller that evaluates rules
  outside a `devkit` invocation checks nothing.

## 2. Cause of Violation

One violation per citation, at its line and column, for the first problem in it:

- `Unknown command '<word>' of '<command path>' in `<citation>``: the group has no such subcommand. Options after an
  unknown command are not reported separately.
- `Unknown option <option> of '<command path>' in `<citation>``: the command has no such option. Options placed before
  a subcommand belong to the group, as on a real command line: `--version` is an option of the root only.

## 3. Remediation

There is no autofix: which command a stale citation should become is a judgment.

- Cite the command as it is now; `devkit <command> --help` lists subcommands and options.
- A planned, rejected or removed command is not an invocation: describe it in prose (a `bundle init` subcommand)
  rather than as inline code starting with `devkit`.
- A plugin a document describes but the project does not install, or a planned command a document must cite, is a
  configured exception (section 5).

## 4. Configuration

```toml
[rules.settings.RULE-cli-contract]
exclude = ["docs/decisions/**", "docs/proposals/**"]   # Markdown files not checked (default: none)
unchecked_commands = ["spec"]                          # command paths below devkit not checked (default: none)
```

- `exclude` (`list[str]`): workspace-relative patterns of Markdown files the rule skips. Use it for documents that
  record history or plans: decisions that weigh alternative commands, proposals and specs that describe commands
  not built yet.
- `unchecked_commands` (`list[str]`): command paths below `devkit`, words separated by spaces (`"spec"`,
  `"bundle init"`). A citation that reaches one is not checked further, subcommands and options included. Use it
  for a plugin the documents describe but the project environment does not install.
- Both accept per-path overrides (`[[rules.settings.RULE-cli-contract.overrides]]`).

## 5. Exceptions

There is no inline suppression. Record an exception in the settings above with a comment giving the reason, or
exclude the file from every rule with `[rules] exclude`. Lower the rule to a warning with
`[rules.severity_overrides]` while a large set of stale citations is being fixed.

## 6. Examples

```markdown
Run `devkit rules check --staged` before committing.     <!-- checked, passes -->
Run `devkit rules lint`.                                  <!-- Unknown command 'lint' of 'devkit rules' -->
`devkit run -- uv run pytest -x`                          <!-- options after -- are not devkit's -->
A `devkit` installation in prose is not a citation.       <!-- not checked -->
```
