# Tracked Impeccable context links

Read for requested context-link setup or read-only link inspection. Run this skill's
`scripts/link-impeccable-context.sh`; do not load the shell source as instructions.

- During context gathering, `--check` is read-only inspection and needs no setup request.
- Mutating link setup runs only on the user's request, through the selected task route and host permissions.
- Before requested setup, show these exact Git local exclude lines:

```text
/PRODUCT.md
/DESIGN.md
/.impeccable
```

1. Use an existing tracked source. Default source is `docs/materials/impeccable`; pass another in-worktree directory
   explicitly. Source context remains consumer-owned; the helper neither creates content nor installs source-side
   ignores or stages files. Linking `.impeccable` does not ignore runtime output through its tracked source path;
   leave retention policy with the consumer.
2. Before link mode, stop other writers of managed root entries and source for the command duration.
   Noncooperating concurrent writers are unsupported.
3. Run `sh <installed-skill>/scripts/link-impeccable-context.sh [<source-dir>]` once per worktree or clone needing
   links. Relative arguments resolve from that worktree's root. Linked worktrees share the Git exclude file and
   still need their own relative links. Existing root files, directories and links are preserved.
4. Check with `sh <installed-skill>/scripts/link-impeccable-context.sh --check [<source-dir>]`.
   Read stable codes/actions and terminal exit: 0 clean, 1 unresolved states, 2 unable to run.
   Check mode changes no files, locks or temporary files. Report partial setup effects on I/O failure.
5. If `LINK_REPLACED` reports replacement, preserve both versions and request direction to reconcile into the
   tracked source before restoring the root link. Never overwrite or repair automatically. Check again afterward.
   Use the existing absolute read-only context path fallback when links are not used.

Completion: each managed entry is linked to the current worktree source or reported unresolved with its stable
code/action; source content, source-side ignores and exact Git authority stay with the consumer.
