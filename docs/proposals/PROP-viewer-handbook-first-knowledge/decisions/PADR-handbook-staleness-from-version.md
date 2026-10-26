---
id: PADR-handbook-staleness-from-version
title: Handbook staleness from the VERSION file
summary: For the handbook's staleness note in the viewer, we compare the manifest tag with v<VERSION> read as an ordinary file, to keep ordinary viewer reads free of Git, accepting that a repository without VERSION shows only the tag and date.
proposal: PROP-viewer-handbook-first-knowledge
status: draft
created_at: 2026-10-26
---

# [PADR-handbook-staleness-from-version] Handbook staleness from the VERSION file

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The handbook is intentionally stale between refreshes (`ADR-handbook-on-request-release-snapshot`): every page's
provenance block names the release tag it describes, and `handbook/manifest.json` carries that `tag`, the
`source_commit` and the `generated` date (`CAP-DLV-release-handbook` §4.3). A reader opening it in the viewer needs to
see whether that release is the repository's current one. The viewer's ordinary reads start no Git process
(`CAP-VIEW-repository-viewer` §2, `ADR-viewer-working-tree`), and a refresh writes the tag from `VERSION` before the
release is tagged, so in release preparation the manifest tag is ahead of the latest Git tag (this repository:
manifest `v0.1.4`, `VERSION` `0.1.3`, latest tag `v0.1.3` at Planning time).

Pending the user's answer to question `staleness-reference` of this Planning run.

## 2. Decision Drivers

- No Git process or new endpoint for an ordinary read.
- A note that is right during release preparation as well as between releases.
- Works for library hosts (autohub) through their existing `tree` and `blob`.

## 3. Considered Options

- **`VERSION` file**: read `VERSION` through the existing blob read and compare `v<VERSION>` with the manifest tag;
  no Git, but a repository without `VERSION` gets no comparison.
- **Latest Git tag**: compare with the newest reachable tag; matches "released" exactly but needs a Git read in an
  ordinary request, a new exception to `CAP-VIEW-repository-viewer` §2, and a new data-source method for hosts.
- **Source commit against `HEAD`**: report whether `docs/` changed since `source_commit`; the most precise, but
  needs Git and reports "stale" after almost every commit, which the handbook is by design.
- **No comparison**: show the tag and generation date only; no false notes, but the reader must know the current
  release.

## 4. Decision Outcome

Recommended: the `VERSION` file.

- WHEN the manifest tag equals `v<VERSION>`, the handbook header shows the tag and generation date without a note.
- WHEN they differ, the header shows a non-alert note naming both ("describes `v0.1.3`; this repository is at
  `0.1.4`") and that the Living Spec book shows the current contracts.
- WHEN `VERSION` is absent or unreadable, the header shows the tag and date only.

The reason is the first and third drivers: the comparison is one more ordinary blob read and no Git.

## 5. Consequences

- Positive: no Git in ordinary reads; correct during release preparation, because a refresh writes `v<VERSION>`.
- Negative: a `VERSION` bumped for the next release before its refresh shows the note even though no release has
  happened yet; the note then names a version, not a published tag.
- Follow-up: none.

## 6. Confirmation

- Frontend tests in Development: equal tag, differing tag and absent `VERSION` render the three header states.
- Review only: no Git process is added to `packages/devkit-viewer/src/devkit_viewer/features/browse/`.
