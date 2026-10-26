---
id: PADR-handbook-staleness-from-version
title: Handbook staleness from the VERSION file
summary: For the handbook's staleness note in the viewer, we compare the manifest tag with v<VERSION> by version order, read as an ordinary file, to keep viewer reads free of Git and right during release preparation, accepting that a repository without VERSION shows only the tag and date.
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
(`CAP-VIEW-repository-viewer` §2, `ADR-viewer-working-tree`).

A refresh runs in release preparation before the `just version-sync` metadata commit and the tag
(`CAP-DLV-release-handbook` §3.3 rule 1), so between the refresh commit and the release both the committed `VERSION`
and the latest Git tag trail the manifest. This repository at Planning time: manifest `v0.1.4`, `VERSION` `0.1.3`,
latest tag `v0.1.3`. An equality test against either one reports a fresh snapshot as stale.

## 2. Decision Drivers

- No Git process or new endpoint for an ordinary read.
- A note that is right during release preparation as well as between releases.
- Works for library hosts (autohub) through their existing `tree` and `blob`.

## 3. Considered Options

- **`VERSION` by version order**: read `VERSION` through the existing blob read and order `v<VERSION>` against the
  manifest tag; no Git and right in both windows, but a repository without `VERSION` gets no comparison.
- **`VERSION` by equality**: the same read; reports every snapshot made for an upcoming release as stale until
  `just version-sync`.
- **Latest Git tag by version order**: the same ordering against the newest tag; matches "released" exactly but
  needs a Git read in an ordinary request, a new exception to `CAP-VIEW-repository-viewer` §2, and a new data-source
  method for hosts.
- **Source commit against `HEAD`**: reports whether `docs/` changed since `source_commit`; needs Git and reports
  "stale" after almost every commit, which the handbook is by design.
- **No comparison**: show the tag and generation date only; no false notes, but the reader must know the current
  release.

## 4. Decision Outcome

Chosen by the user: `VERSION` by version order (numeric `major.minor.patch`; a value that does not parse counts as absent).

- WHEN the manifest tag is ahead of `v<VERSION>`, the header names the snapshot as prepared for the upcoming release
  `<tag>`, without a staleness note.
- WHEN they are equal, the header shows the tag and generation date without a note.
- WHEN the manifest tag is behind, the header shows a non-alert note naming both (for example "describes `v0.1.4`;
  this repository is at `0.1.5`") and that the Living Spec book shows the current contracts.
- WHEN `VERSION` is absent or unparsable, the header shows the tag and date only.

The reason is the first two drivers: one more ordinary blob read, no Git, and no false note in release preparation.

## 5. Consequences

- Positive: no Git in ordinary reads; no false note between a refresh and its release.
- Negative: after `VERSION` is bumped for the next release and before its refresh, the note names a version that is
  not yet a published tag.
- Follow-up: none.

## 6. Confirmation

- Frontend tests in Development: ahead, equal, behind and absent `VERSION` render the four header states.
- Review only: no Git process is added to `packages/devkit-viewer/src/devkit_viewer/features/browse/`.
