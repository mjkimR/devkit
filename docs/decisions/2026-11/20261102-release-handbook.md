---
id: ADR-release-handbook
title: Release handbook as an on-request snapshot, shown first in the viewer
summary: "For a human entry point to devkit, we keep a tracked handbook/ refreshed only on request at release, localized only under handbook/<lang>/, shown first in the viewer with staleness from VERSION and the Living Spec book on request, to add no reconcile duty, accepting a handbook that may lag."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-handbook-first-book-on-request
  - ADR-handbook-on-request-release-snapshot
  - ADR-handbook-staleness-from-version
  - ADR-localized-handbook-language-exception
---

# [ADR-release-handbook] Release handbook as an on-request snapshot, shown first in the viewer

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `CAP-DLV-release-handbook`, `CAP-VIEW-repository-viewer`, `handbook/`,
  `scripts/release.sh`, `packages/devkit-viewer/`, `AGENTS.md`

---

## 1. Context & Problem Statement

`docs/` is written for agents and split by contract and ID; a person has no single entry point to what devkit is and
how to use it. A derived handbook gives one, but any derived copy that must stay current becomes a second reconcile
target. Releases are frequent (v0.1.0 to v0.1.3 within 11 days, 239 `docs/` files changed between two of them), so
a refresh bound to every tag means a near-full rewrite, translation and human review every few days.

`AGENTS.md` requires all documentation, architecture specifications and guide materials in English. No rule enforces
it and no ADR recorded it. The handbook exists for people, and its first readers include Korean speakers, so it needs
translated pages; without a recorded, bounded exception, non-English text has no defined place in the repository.

The viewer's Book rail tab (`view` id `book`, the Living Spec reading tab of `CAP-VIEW-repository-viewer` §4, whose
label there differs from the code's) indexed every Markdown file under `docs/` and `specs/` and rendered every Living
Spec chapter as soon as it opened. On this repository that is about 1.1 s, 922 blob reads and 124k DOM nodes before
anything is readable, of which about 0.47 s is rendering (`MAT-viewer-handbook-cold-load`). The release handbook
(`CAP-DLV-release-handbook`) is the entry point written for people, but the viewer did not show it, and
`CAP-DLV-release-handbook` §2 listed that as out of scope with a reason that no longer holds: the viewer reads the
working tree (`ADR-repository-viewer`), where `handbook/` is an ordinary directory. Only this repository has a
handbook (the playbook is in the repository-only `devkit-dev` bundle), the viewer serves several repositories, and the
handbook trails the current `docs/` between refreshes, so the book must stay reachable.

The handbook is intentionally stale between refreshes: every page's provenance block names the release tag it
describes, and `handbook/manifest.json` carries that `tag`, the `source_commit` and the `generated` date
(`CAP-DLV-release-handbook` §4.3). A reader opening it in the viewer needs to see whether that release is the
repository's current one. The viewer's ordinary reads start no Git process (`CAP-VIEW-repository-viewer` §2,
`ADR-repository-viewer`). A refresh runs in release preparation before the `just version-sync` metadata commit and
the tag (`CAP-DLV-release-handbook` §3.3 rule 1), so between the refresh commit and the release both the committed
`VERSION` and the latest Git tag trail the manifest. This repository at Planning time: manifest `v0.1.4`, `VERSION`
`0.1.3`, latest tag `v0.1.3`. An equality test against either one reports a fresh snapshot as stale.

---

## 2. Decision Drivers

- No new obligation for `spec-sync` or Living Spec reconcile.
- A handbook a reader can trust: it states which release it describes and matches that release's `docs/`.
- Refresh cost under the user's control, not the release cadence's.
- Releases that do not refresh stay independent of the handbook.
- Every agent-facing and Living Spec document stays English.
- People can read the handbook in their language.
- The language exception is bounded by path, so a reviewer can tell at a glance whether non-English text is allowed.
- The first read of the viewer tab is the person-oriented one where it exists.
- No index or book rendering before a person asks for the current contracts.
- Unchanged book content and order once computed.
- No new write path; no new endpoint or Git process for an ordinary read; library hosts (autohub) keep their
  `RepositoryDataSource` and its existing `tree` and `blob`.
- Hosts keep the `book` view id, `initialView` and the `sdd:path-change` event.
- A staleness note that is right during release preparation as well as between releases.

---

## 3. Considered Options

### Handbook delivery, cadence and gating (ADR-handbook-on-request-release-snapshot)

- **Delivery form**: a tracked `handbook/` on `main` (chosen; browsable in the tag, linkable from `README.md`); a
  GitHub Release asset built from the tag (rejected: nothing tracked, no browsable path); an untracked on-demand
  artifact (rejected: no release binding, no provenance a reader can check).
- **Refresh cadence**: every release tag (rejected: rewrite cost every few days); minor releases only (rejected: still
  a fixed cadence); only when the user explicitly runs the playbook (chosen: cost chosen per release).
- **Release gating**: a refreshing release fails on verification or a `docs/` mismatch (chosen); or it only warns
  (rejected).

### Handbook languages (ADR-localized-handbook-language-exception)

- **en and ko now, exception limited to `handbook/<lang>/` for non-en languages** (chosen): serves Korean readers in
  the first handbook; the exception is one path pattern.
- **en only first, ko and the exception later** (rejected): no exception yet, but the first handbook misses its Korean
  readers.
- **Keep the current state** (rejected; English only, no handbook translations): contradicts the handbook's purpose.

### Viewer reading tab (ADR-handbook-first-book-on-request)

- **Handbook first, book on request (one tab)** (chosen): the tab opens the handbook or an absence note and offers a
  "Living Spec book" control; one rail entry, no cold cost, one extra selection for the book.
- **Separate Handbook tab, Book on request** (rejected): two rail entries; the same costs, but the two reading modes
  of one question ("what is this repository") are split, and a repository without a handbook shows an empty tab.
- **Keep the book eager, add a Handbook tab** (rejected): no change for book readers; the cold cost stays for anyone
  who opens the book tab first.
- **Viewport rendering of the book** (rejected; `FB-viewer-book-rendering`): keeps the book first and cuts DOM and
  render work, but still pays the 0.6 s, 922-read index and risks jumps and heading tracking.
- **New backend endpoint for handbook pages** (rejected): a dedicated listing; duplicates `tree` and `blob`, which
  already read `handbook/` with the same path, symlink and `.git` guards, and needs a new method in every host's data
  source.

### Staleness comparison (ADR-handbook-staleness-from-version)

- **`VERSION` by version order** (chosen by the user): read `VERSION` through the existing blob read and order
  `v<VERSION>` against the manifest tag; no Git and right in both windows, but a repository without `VERSION` gets no
  comparison.
- **`VERSION` by equality** (rejected): the same read; reports every snapshot made for an upcoming release as stale
  until `just version-sync`.
- **Latest Git tag by version order** (rejected): the same ordering against the newest tag; matches "released"
  exactly but needs a Git read in an ordinary request, a new exception to `CAP-VIEW-repository-viewer` §2, and a new
  data-source method for hosts.
- **Source commit against `HEAD`** (rejected): reports whether `docs/` changed since `source_commit`; needs Git and
  reports "stale" after almost every commit, which the handbook is by design.
- **No comparison** (rejected): show the tag and generation date only; no false notes, but the reader must know the
  current release.

---

## 4. Decision Outcome

### On-request release snapshot

- The handbook is a tracked `handbook/` directory on `main`, committed during release preparation before the tag,
  because a tag then carries a browsable handbook matching its own `docs/`. (ADR-handbook-on-request-release-snapshot)
- It is refreshed only when the user explicitly runs the handbook playbook; there is no cadence. A release that does
  not refresh keeps the previous handbook, whose provenance names its older tag, because cost then follows the user's
  choice. (ADR-handbook-on-request-release-snapshot)
- `handbook/manifest.json` names the release tag the refresh targets. `scripts/release.sh` treats a release as
  refreshing exactly when that tag equals the tag being built, a fact read from committed state; it runs no generation
  or refresh. (ADR-handbook-on-request-release-snapshot)
- A refreshing release fails its build on handbook verification failure or when `docs/` at the tagged commit differs
  from `docs/` at the manifest source commit. Every other release is unaffected.
  (ADR-handbook-on-request-release-snapshot)
- The handbook is a derived view: never a source of truth and never a reconcile target; the Living Spec prevails on
  any conflict. (ADR-handbook-on-request-release-snapshot)

### Languages

- The first handbook carries `en` and `ko`. English is the pivot, synthesized from `docs/`; `ko` is translated from
  English. (ADR-localized-handbook-language-exception)
- Non-English text is allowed only under `handbook/<lang>/` for languages other than `en`. `handbook/en/`,
  `handbook/manifest.json`, `docs/`, `specs/`, guides, READMEs and agent assets stay English.
  (ADR-localized-handbook-language-exception)
- Identifiers (commands, error codes, document IDs) are never translated, and Living Spec sources linked from the
  handbook stay untranslated. (ADR-localized-handbook-language-exception)
- `AGENTS.md` names this exception next to the English-only rule. (ADR-localized-handbook-language-exception)

### Viewer: handbook first, book on request

- **Tab** (decided by the user): the rail entry keeps the `book` id; its label becomes "Read" and its title
  "Handbook and Living Spec book". (ADR-handbook-first-book-on-request)
- **Detection**: the tab reads `handbook/manifest.json` through the existing `blob` read. A rejection whose message
  matches the existing absent-path convention `/^HTTP 404(?:\b|:)/` (`scanDocuments` in `api/documents.ts`) means no
  handbook; `CAP-VIEW-repository-viewer` §6 states that a host's `blob` signals an absent file that way. A readable
  manifest with `en` in `langs` opens the handbook; any other failure shows the error and the book control.
  (ADR-handbook-first-book-on-request)
- **Read budget before the control**: with a handbook, the manifest, `VERSION` and one page; without one, the manifest
  alone. No `tree` or `blob` under `docs/` or `specs/`. No new endpoint, Git process or data-source method.
  (ADR-handbook-first-book-on-request)
- **Pages**: a page renders through the existing Markdown and DOMPurify path, without the Living Spec index.
  (ADR-handbook-first-book-on-request)
  - A relative link to another `.md` page under the same `handbook/<lang>/` opens that page in the tab; a link that
    leaves `handbook/<lang>/` is shown as unavailable and reads nothing. A missing page shows an error with the home
    entry.
  - A fragment resolves to an element whose `id` equals it, else to the prefixed heading slug, so the English
    heading slugs and the Korean raw anchors (`<a id="journeys">`) both scroll.
- **Navigation**: in handbook mode the sidebar shows a "Handbook home" entry (`README.md`), the language switch, the
  book control and the current page's headings; it needs no extra read. Every page's generated table of contents
  provides the page list. (ADR-handbook-first-book-on-request)
- **Source links** (decided by the user): `https://github.com/<repository>/blob/<tag>/<path>` links stay external
  and open in a new browsing context. (ADR-handbook-first-book-on-request)
- **Language**: the switch lists the manifest's `langs`; the viewer remembers the choice in browser storage for all
  repositories and otherwise starts with the browser language if listed, else `en`. Switching keeps the page's
  relative path, which `CAP-DLV-release-handbook` §3.1 rule 1 guarantees in every language.
  (ADR-handbook-first-book-on-request)
- **No handbook**: the tab shows that the repository has no `handbook/manifest.json` and the book control; Proposals
  and Specs are separate rail tabs and unchanged. (ADR-handbook-first-book-on-request)
- **Two gates in the shared component**: one `KnowledgeViews` instance serves Book, Proposals and Specs.
  (ADR-handbook-first-book-on-request)
  - Book rendering runs only while `view === 'book'` and the book was requested; an index loaded by Proposals or
    Specs never renders the book on its own.
  - The index runs from a latch set by the first Proposals or Specs view or by the book request; it never resets on a
    view change, so switching between the three views starts no second scan.
- **Request state**: the book request lives in `SddViewer` for its lifetime and is passed to `KnowledgeViews` as a
  bindable prop, so it survives rail switches and resets with a repository or branch switch, which the page already
  remounts. A standalone `KnowledgeViews` host binds the prop to keep it. The data follows the existing 30-second
  caches. (ADR-handbook-first-book-on-request)
- **Deep links** (decided by the user; library hosts only, since the standalone page opens on the Dashboard
  and no Dashboard card targets `book`): a host request with `initialView` `book` and an `initialPath` naming a file
  under `docs/`, not the default `docs/`, counts as the book request; a path under `handbook/` opens that page.
  `sdd:path-change` keeps `view: "book"` and carries the handbook page path in handbook mode.
  (ADR-handbook-first-book-on-request)
- **Contracts**: `CAP-VIEW-repository-viewer` §4 states the tab's default, the handbook source and the on-demand
  book, and §6 the absent-file signal; `CAP-DLV-release-handbook` §2 drops the viewer from Out-of-Scope.
  (ADR-handbook-first-book-on-request)

### Staleness from VERSION

- Chosen by the user: the handbook header compares the manifest tag with `v<VERSION>` by version order (numeric
  `major.minor.patch`; a value that does not parse counts as absent), with `VERSION` read through the existing blob
  read.
  (ADR-handbook-staleness-from-version)
  - WHEN the manifest tag is ahead of `v<VERSION>`, the header names the snapshot as prepared for the upcoming
    release `<tag>`, without a staleness note.
  - WHEN they are equal, the header shows the tag and generation date without a note.
  - WHEN the manifest tag is behind, the header shows a non-alert note naming both (for example "describes `v0.1.4`;
    this repository is at `0.1.5`") and that the Living Spec book shows the current contracts.
  - WHEN `VERSION` is absent or unparsable, the header shows the tag and date only.
- The reason is one more ordinary blob read, no Git, and no false note in release preparation.
  (ADR-handbook-staleness-from-version)

---

## 5. Consequences

- **Positive**:
  - No reconcile duty; each refreshed tag has a verified handbook matching its `docs/`; refresh cost is paid only when
    chosen. (ADR-handbook-on-request-release-snapshot)
  - Korean readers get the handbook; every other document keeps one language.
    (ADR-localized-handbook-language-exception)
  - The tab's cold load drops from about 1.1 s and 922 reads to three small reads with a handbook, or one without;
    autohub gets the handbook through its existing data source. (ADR-handbook-first-book-on-request)
  - No Git in ordinary reads; no false note between a refresh and its release. (ADR-handbook-staleness-from-version)
- **Negative / Risks**:
  - The handbook may trail several releases; readers rely on its provenance header to see how old it is.
    (ADR-handbook-on-request-release-snapshot)
  - A refresh started for one version and released under another fails no check, because the manifest tag no longer
    matches; the release then counts as non-refreshing. The playbook writes the tag from `VERSION`.
    (ADR-handbook-on-request-release-snapshot)
  - Each refresh also translates the stale English pages and needs a review of the translation.
    (ADR-localized-handbook-language-exception)
  - A reader who wants the current contracts selects the control once per viewer session; the handbook's ID citations
    are not in-page links to the book; tag-pinned source links fail until the tag is pushed.
    (ADR-handbook-first-book-on-request)
  - After the request the book costs what it costs today, and returning to the tab re-renders it (about 0.47 s);
    Proposals and Specs keep the 0.6 s index (`FB-viewer-knowledge-anchor-loading` stays open).
    (ADR-handbook-first-book-on-request)
  - After `VERSION` is bumped for the next release and before its refresh, the note names a version that is not yet a
    published tag. (ADR-handbook-staleness-from-version)
- **Follow-ups**:
  - When no refresh has run for a minor release, the user decides whether to refresh; no automation triggers it.
    (ADR-handbook-on-request-release-snapshot)
  - Adding a language adds `handbook/<lang>/`, its `terms.yaml` and a `langs` entry in the manifest, within this
    exception. (ADR-localized-handbook-language-exception)
  - `FB-viewer-book-rendering` stays open, rescoped to rendering after the request; revisit it when that rendering is
    reported as slow. (ADR-handbook-first-book-on-request)

---

## 6. Confirmation

- Release-script tests in Development: a manifest tag equal to the built tag with a differing `docs/` tree fails the
  build; a differing manifest tag skips the handbook checks and runs no handbook command that writes files.
  (ADR-handbook-on-request-release-snapshot)
- Handbook script fixture tests for the verification checks (proposal section 3.3 step 3).
  (ADR-handbook-on-request-release-snapshot)
- `RULE-cli-contract` excludes `handbook/**`; `just rules-check` stays clean after a cited command is renamed.
  (ADR-handbook-on-request-release-snapshot)
- The handbook script's parity check: every language in `manifest.json` has the English file set and a current
  `translated_from` per page. (ADR-localized-handbook-language-exception)
- Review only for non-English text outside `handbook/<lang>/`; no rule checks document language.
  (ADR-localized-handbook-language-exception)
- Frontend tests in Development (`frontend/src/lib/features/knowledge/`, `frontend/src/lib/SddViewer.test.ts`):
  (ADR-handbook-first-book-on-request)
  - a manifest opens the handbook within the read budget; its absence shows the note and the control;
  - no `tree` or `blob` under `docs/` or `specs/` and no `section.chapter` element before the control, also after
    Proposals loaded the index;
  - Book, Proposals and Book again start one index scan;
  - the request survives a Dashboard visit;
  - the computed book equals today's chapter list;
  - a handbook link leaving `handbook/<lang>/` reads nothing; a cross-page fragment scrolls in `en` and `ko`.
- Integration test (`tests/integration/features/browse/`): `handbook/` pages and the manifest read through `blob`
  keep the symlink and `..` refusals. (ADR-handbook-first-book-on-request)
- The cold-load probe of `MAT-viewer-handbook-cold-load` rerun against the change, with the tab label and readiness
  selector as arguments. (ADR-handbook-first-book-on-request)
- Frontend tests in Development: ahead, equal, behind and absent `VERSION` render the four header states.
  (ADR-handbook-staleness-from-version)
- Review only: no Git process is added to `packages/devkit-viewer/src/devkit_viewer/features/browse/`.
  (ADR-handbook-staleness-from-version)
