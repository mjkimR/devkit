# [RULE-clean-artifacts] Generated Artifacts Never Enter a Commit

## 1. Overview

Build outputs, local databases and logs bloat the repository, change on every run and may carry local data. The
rule stops them at the commit gate and in CI.

- **Phase and severity**: `linter`, `error`.
- **What is checked**: explicit targets only, the files named on the command line or the changed files of
  `devkit rules check --staged` / `--ci`. A run without targets reports nothing.

## 2. Cause of Violation

The message is `<kind> should not be committed`:

- **Compiled binary**: the file starts with an ELF, PE/DOS or Mach-O header.
- **Database file**: the name ends in `.db`, `.sqlite` or `.sqlite3`.
- **Log file**: the name ends in `.log` and the file is larger than 1 MiB.

## 3. Remediation

Remove the artifact from the change (`git restore --staged <file>`, or `git rm --cached <file>` for one already
tracked) and add an ignore rule (`.gitignore`) so it does not come back. Produce build outputs in CI or a release
job, and keep local databases and logs outside the repository.

## 4. Configuration

The rule has no settings.

## 5. Exceptions

There is no inline suppression. A deliberate binary fixture (a small test database, a sample executable) belongs
under a path excluded from every rule (`[rules] exclude`), with the reason in a comment.
