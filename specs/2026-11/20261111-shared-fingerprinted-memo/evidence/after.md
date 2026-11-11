# Memo harness: after

Source: `memo_harness.py` (unchanged since `before.md`) run on the changed working tree, command
`uv run python specs/2026-11/20261111-shared-fingerprinted-memo/evidence/memo_harness.py tmp/probe/harness-after`.

## Comparison with `before.md`

76 of 84 rows are identical. The 8 differing rows are all converged-rule (decision D1) cases:

| Rows | Before | After | Cause |
| --- | --- | --- | --- |
| docs write/read `symlink-devkit` | used | not used, no log line | a symbolic link at `.devkit/` is refused (agt rule) |
| docs write/read `non-directory-below` | "discarded: cannot be read" (and "not written" on a writing load) | one "not used: a non-directory on the way" line | a non-directory component is refused at open (agt rule) |
| facts write/read `extra-key` | used | not used; the writer rewrites the file | an extra top-level key discards the memo (docs rule) |
| facts write/read `nan-constant` | used | not used; the writer rewrites the file | the fixture appends `NaN` under an extra top-level key `x`, so for the facts memo it is the extra-key case; the facts JSON parse still accepts `NaN` (unchanged, kept local) |

The docs `nan-constant` rows are unchanged: the docs JSON parse refuses `NaN` before the envelope check.

## Table

| memo | mode | fixture | memo used | file | logs (logger/level/message) |
| --- | --- | --- | --- | --- | --- |
| docs | write | valid | used | same | - |
| docs | write | missing-file | not used | created | - |
| docs | write | missing-below-transient | not used | created | - |
| docs | write | no-transient | not used | same | - |
| docs | write | devkit-is-file | not used | same | - |
| docs | write | malformed | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: cannot be read: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) |
| docs | write | nan-constant | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: cannot be read: NaN is not a stored value |
| docs | write | not-object | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | write | foreign-version | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another version |
| docs | write | bool-version | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another version |
| docs | write | foreign-fingerprint | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another parser fingerprint |
| docs | write | entries-not-mapping | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | write | missing-key | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | write | extra-key | not used | rewritten | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | write | non-regular | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json not used: not a regular file |
| docs | write | symlink-file | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | write | symlink-leaf-dir | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | write | symlink-first-below | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | write | symlink-transient | not used | same | - |
| docs | write | symlink-devkit | not used | same | - |
| docs | write | non-directory-below | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json not used: a non-directory on the way |
| docs | read | valid | used | same | - |
| docs | read | missing-file | not used | same | - |
| docs | read | missing-below-transient | not used | same | - |
| docs | read | no-transient | not used | same | - |
| docs | read | devkit-is-file | not used | same | - |
| docs | read | malformed | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: cannot be read: Expecting property name enclosed in double quotes: line 1 column 2 (char 1) |
| docs | read | nan-constant | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: cannot be read: NaN is not a stored value |
| docs | read | not-object | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | read | foreign-version | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another version |
| docs | read | bool-version | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another version |
| docs | read | foreign-fingerprint | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: another parser fingerprint |
| docs | read | entries-not-mapping | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | read | missing-key | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | read | extra-key | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json discarded: not the expected shape |
| docs | read | non-regular | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json not used: not a regular file |
| docs | read | symlink-file | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | read | symlink-leaf-dir | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | read | symlink-first-below | not used | same | memo/INFO/document memo not used: a symbolic link at <root>/.devkit/transient/docs/document-index.json |
| docs | read | symlink-transient | not used | same | - |
| docs | read | symlink-devkit | not used | same | - |
| docs | read | non-directory-below | not used | same | memo/INFO/document memo <root>/.devkit/transient/docs/document-index.json not used: a non-directory on the way |
| facts | write | valid | used | same | - |
| facts | write | missing-file | not used | created | - |
| facts | write | missing-below-transient | not used | created | - |
| facts | write | no-transient | not used | same | - |
| facts | write | devkit-is-file | not used | same | - |
| facts | write | malformed | not used | rewritten | facts/DEBUG/Unable to load facts memo for RULE-harness-facts |
| facts | write | nan-constant | not used | rewritten | - |
| facts | write | not-object | not used | rewritten | - |
| facts | write | foreign-version | not used | rewritten | - |
| facts | write | bool-version | not used | rewritten | - |
| facts | write | foreign-fingerprint | not used | rewritten | - |
| facts | write | entries-not-mapping | not used | rewritten | - |
| facts | write | missing-key | not used | rewritten | - |
| facts | write | extra-key | not used | rewritten | - |
| facts | write | non-regular | not used | same | - |
| facts | write | symlink-file | not used | same | - |
| facts | write | symlink-leaf-dir | not used | same | - |
| facts | write | symlink-first-below | not used | same | - |
| facts | write | symlink-transient | not used | same | - |
| facts | write | symlink-devkit | not used | same | - |
| facts | write | non-directory-below | not used | same | - |
| facts | read | valid | used | same | - |
| facts | read | missing-file | not used | same | - |
| facts | read | missing-below-transient | not used | same | - |
| facts | read | no-transient | not used | same | - |
| facts | read | devkit-is-file | not used | same | - |
| facts | read | malformed | not used | same | facts/DEBUG/Unable to load facts memo for RULE-harness-facts |
| facts | read | nan-constant | not used | same | - |
| facts | read | not-object | not used | same | - |
| facts | read | foreign-version | not used | same | - |
| facts | read | bool-version | not used | same | - |
| facts | read | foreign-fingerprint | not used | same | - |
| facts | read | entries-not-mapping | not used | same | - |
| facts | read | missing-key | not used | same | - |
| facts | read | extra-key | not used | same | - |
| facts | read | non-regular | not used | same | - |
| facts | read | symlink-file | not used | same | - |
| facts | read | symlink-leaf-dir | not used | same | - |
| facts | read | symlink-first-below | not used | same | - |
| facts | read | symlink-transient | not used | same | - |
| facts | read | symlink-devkit | not used | same | - |
| facts | read | non-directory-below | not used | same | - |
