---
reconcile_id: REC-viewer-handbook-first-knowledge
status: pending
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-release-handbook.md
    resolution: modified
  - file: docs/development/reference/viewer.md
    resolution: modified
  - file: packages/devkit-viewer/README.md
    resolution: modified
  - file: packages/devkit-viewer/frontend/README.md
    resolution: waived
    rationale: "Outside this run's write scope. Every statement it carries stays true: the exports, the data-source methods and the initialView=\"book\" example are unchanged, and it names CAP-VIEW-repository-viewer as its contract, where §6 now states the absent-file signal and the optional bookRequested prop. The Host decides whether the consumer README mirrors them."
---
# Reconcile the handbook-first reading tab

`CAP-VIEW-repository-viewer` now holds the delivered contract. §4 names the tab **Read** (view id `book`) and points
to the new §4.3, whose rules state the handbook detection through `blob` and the absent-path convention, the read
budget before the request, the absence and manifest-failure states with the `Living Spec book` control, book
rendering only on request also after Proposals or Specs indexed, one index scan per data source and branch, the
request's lifetime and the `Handbook` return control, host deep links, page rendering, link and fragment handling,
the language switch and its memory, the staleness header, and the `sdd:path-change` location in handbook mode. Each
rule names the test that enforces it, and the serving paragraph names `tests/integration/features/browse/test_handbook.py`.
§6 states the host's absent-file signal (`HTTP 404` rejection) and the optional bindable `bookRequested` prop of
`KnowledgeViews`. The summary and the decision list name `ADR-handbook-first-book-on-request` and
`ADR-handbook-staleness-from-version`.

`CAP-DLV-release-handbook` §2 drops the viewer from its Out-of-Scope list, as `ADR-handbook-first-book-on-request`
decided; its other rules are unchanged. The command reference and the package README mirror the tab's behavior.

No endpoint, Git process or write path was added, so §2, §3, `ARCH-05-1-containers` and `ARCH-07-deployment` still
hold and no architecture document changes. No use case covers the viewer and no domain term was introduced. The two
accepted ADRs already state the decisions and need no edit.

The implementation made three choices inside the agreed scope. A `Handbook` control in the book returns to the
handbook while keeping the index, and the request holds only for the data source and branch it was made for, while a
docs/ deep link sets it again after a switch; §4.3 states both. Handbook reads are not cached (three small reads), so §4.1's cache
list stays unchanged.

## Entrypoints

Derivation proposed viewer frontend paths for `CAP-DLV-release-handbook`, rejected because that document changed only
by one Out-of-Scope line and does not own the viewer, and `tests/integration/features/browse/test_handbook.py` for
`CAP-VIEW-repository-viewer`, rejected because tests verify rather than open the capability. The existing
`packages/devkit-viewer/frontend/src/lib/` entrypoint already covers the new reader and view.

## Measurement

`MAT-viewer-handbook-cold-load` records the after-change probe beside its baseline: the reading tab's cold load reads
3 blobs instead of 922, leaves 3.1k DOM nodes instead of 124k and shows content in about 50 ms instead of about
1.1 s, on the same Apple M4 Pro with Chrome 155.

## Source feedback

- `FB-viewer-book-rendering`: kept `open` by the user's decision. This change removes the book's cold-load cost but
  not the rendering it describes, which still runs after the request (about 0.47 s per return to the tab).
- `FB-viewer-knowledge-anchor-loading`: kept `open`. Proposals and Specs still index all of `docs/` and `specs/`
  (927 reads in the after-change probe); this change does not alter that index.

No other work is deferred.
