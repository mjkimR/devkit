# Context-link Planning evidence

Inspected source: `7161366d4c1908f13cea6e54c771c42244d9ad0d`; Planning start commit `9efff00a8` changes only status.

## Repository contracts and projection

- `CAP-DLV-uiux-improvement` rules 18–22 retain consumer context ownership, requested setup, route choice and Git
  authority. Rule 19 and `ADR-impeccable-session-authority` currently limit ignore additions to `.impeccable/` paths.
  Requested root links/excludes therefore need a narrowly superseding decision, not an automatic setup inference.
- `services/bundles/manifest.py:source_files` recursively includes regular files, without a Markdown-only filter;
  `_tree` records bytes/mode. `models/content.py:normal_mode` preserves executability as 0755. Existing
  `test_app_uiux_improve.py` projects the skill tree to managed/shared/Claude directories. Development extends that
  test with the actual script rather than changing distribution behavior.

## Primary external sources inspected 2026-11-13

- [Git rev-parse](https://git-scm.com/docs/git-rev-parse) documents root discovery and Git-path resolution.
  Linked-worktree common exclusion was also verified by the local probe below.
- [Upstream Impeccable README](https://raw.githubusercontent.com/pbakaus/impeccable/main/README.md), Project files
  and git: shared files belong in Git while runtime outputs use ignore rules matching nested `.impeccable`
  directories. Linking the full directory therefore still requires the consumer's source-side retention policy.
  The helper will install no source ignore file or upstream content.
- [FreeBSD ls manual](https://man.freebsd.org/cgi/man.cgi?format=html&query=ls&sektion=1) describes literal output
  outside a terminal and long-format link targets. The Open Group POSIX.1-2017/2024 `ls` pages returned HTTP 403;
  exact standards-page verification is unavailable. No claim that `readlink` or `test -ef` is POSIX.1-2017 is made.

## Bounded local probes

Scratch retained at `.devkit/transient/plan-context-links/` (confirmed ignored); no production code was authored.
On macOS, a temporary Git repository named `repo with spaces` and source `docs/source -> context` produced:

```text
macos-sh: TARGET_MATCH=yes
dash: TARGET_MATCH=yes
main-exclude: .git/info/exclude
linked-exclude: <probe-main>/.git/info/exclude
ignore: PRODUCT.md
.impeccable
```

The shell target comparison captured `LC_ALL=C QUOTING_STYLE=literal ls -dn ./PRODUCT.md`, removed the exact fixed
entry prefix and compared the complete expected target. `dash` here still used macOS utilities; GNU/BusyBox utility
behavior is not measured. The link exclusion pattern without a trailing slash matched the directory symlink.
No live Impeccable session, consumer pilot checkout or editor atomic-save behavior was inspected.
