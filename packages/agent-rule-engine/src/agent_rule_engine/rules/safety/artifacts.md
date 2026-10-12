# [RULE-clean-artifacts] Generated artifacts must not be committed

The rule flags, among the files under check, compiled binaries (ELF, PE and
Mach-O headers), SQLite and other `.db` files, and `.log` files above 1 MiB.

It inspects explicit targets only: files named on the command line or the
changed files of `agent-rules check --staged` / `--ci`. A run without targets
reports nothing.

Remove the artifact from the change, add it to `.gitignore`, and keep build
outputs and local databases out of the repository.
