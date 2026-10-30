# Ledger and lookup evidence for feedback compaction

Planning material for `SPEC-feedback-dedup-and-compaction`, measured at base `95b8228c` in the plan worktree. Code
citations are in historical Git `eb4f48cb13e75d89d212baa4433f9feed721602d:docs/proposals/PROP-feedback-dedup-and-compaction/envelopes/scout-01.yaml`.

## Ledger

`devkit docs list feedback --history -n 0 --format json`: 242 documents, 9 `open`, 233 terminal, about 667 KB.

| Holder | open | resolved | promoted | dismissed | forwarded |
| --- | --- | --- | --- | --- | --- |
| Spec bundle `feedback/` | 9 | 108 | 55 | 35 | 2 |
| `specs/<YYYY-MM>/feedback/` | 0 | 15 | 5 | 5 | 0 |
| `docs/materials/<YYYY-MM>/<slug>/feedback/` | 0 | 7 | 0 | 1 | 0 |

- Outcomes are recorded in three forms: a `- **Disposition**:` line (114 of 233), a `## Disposition` section or a
  `disposition:` frontmatter field; for some resolved items only the resolving bundle's `reconcile.md` names the
  outcome. A compaction run reads each file and, when needed, the reconcile record; there is no single field to copy.
- `target` is free text: asset paths, capability IDs, advisory codes, command names. It does not map mechanically to a
  capability area, which supports grouping by the run's judgment with misgrouping accepted.
- Destinations named in dispositions can stop resolving: `PROP-direct-planning-procedure`,
  `PROP-envelope-record-gaps` and `PROP-integration-follow-ups` are handed off and gone (`devkit docs resolve`
  prints `DOCS_ID_UNRESOLVED`). `RULE-document-reference` rewrites a handed-off proposal reference in a current
  document to its spec with `devkit rules fix`.

## The missed duplicate

| ID | status | target |
| --- | --- | --- |
| `FB-render-stale-fix-ignores-worker-scope` | resolved | `CONFIG_LOCAL_RENDER_STALE advisory of devkit get-context` |
| `FB-local-render-fix-ignores-worker-write-scope` | dismissed (as a duplicate of the above) | `packages/devkit-dist/.../local_render.py` |
| `FB-sync-capability-render-stale-remedy-generic` | open | `CAP-DIST-sync-and-transactions` |

`devkit docs search "stale local render fix names plain devkit sync, writes outside worker scope" --kind feedback
--history -n 4` (hybrid) ranks the three at 1, 3 and 2. Scores are reciprocal-rank fusions (about 0.03) and lexical
BM25 values (about 10 to 40); neither scale supports a fixed "same observation" threshold.

## Probe: lookup after a simulated compaction

A copy of `docs/` and `specs/` under the ignored `.probe/sim/` (searched with `GIT_CEILING_DIRECTORIES` so the copy
is its own workspace) replaced 35 terminal items whose target or title concerns distribution or sync with three
records, `FB-compacted-distribution-{resolved,dismissed,promoted}` at `specs/2026-10/feedback/20261030-...md`. Each
entry kept the original title as its symptom; the records had no `summary`.

| Check | Result |
| --- | --- |
| Same query, `--mode hybrid -n 5` | the open item 1st; the dismissed and resolved records 3rd and 4th |
| Same query, `--mode lexical -n 5` | the open item 1st; the dismissed and resolved records 2nd and 3rd |
| `devkit docs resolve FB-render-stale-fix-ignores-worker-scope` | the resolved record with `alias=FB-render-stale-fix-ignores-worker-scope` |
| `devkit docs search FB-render-stale-fix-ignores-worker-scope --history` | the resolved record, `pinned=yes` |
| `devkit docs list feedback` (default) | 9 open shown, the records hidden as terminal |
| `devkit rules check` on a record | 0 errors |

The existing search finds a compacted observation in the top five in both modes, so recording needs no new lookup
command. The dense part of hybrid ranks on ID and summary only, so a record `summary` that names the area's recurring
symptoms can only help.

## Probe: worst-case record size (after `challenger-01`)

A second copy (`.probe/sim-full/`) removed eight items that cite a related earlier item (the "query" items, as if not
yet recorded) and compacted every other terminal item into one record per status: `resolved` 125 entries (33 KB),
`promoted` 60, `dismissed` 38, `forwarded` 2. This is larger than any per-area record the playbook writes. Each query
is the removed item's title; the table gives the rank of the record holding the related item (`-` = not in the top
five), against the rank of the related item's own file before compaction (query item excluded).

| Related item (status) | hybrid before | hybrid after | lexical before | lexical after |
| --- | --- | --- | --- | --- |
| `FB-render-stale-fix-ignores-worker-scope` (resolved) | 1 | 2 | 1 | 2 |
| `FB-handoff-refusals-emit-maintenance` (resolved) | 1 | 2 | 1 | 1 |
| `FB-config-template-rewrites-crlf-line-endings` (resolved) | 1 | 3 | 1 | 1 |
| `FB-challenger-round-diff-without-shell` (resolved) | 1 | 1 | 1 | 1 |
| `FB-reverify-fix-omits-reconcile-check` (resolved) | 1 | 2 | 1 | 1 |
| `FB-fixture-removal-denied` (resolved) | - | 1 | 2 | 1 |
| `FB-post-commit-rewrite-stales-the-printed-hash` (forwarded) | - | - | - | - |
| `FB-mcp-registration-pending-ignores-runtime` (promoted) | - | 2 | - | 1 |

Caveat: with only four records the compacted search has few competitors, so a top-three rank is easier than in a
per-area ledger; the result shows that record length does not push the matching record out of `-n 5`, not that
per-area ranking is better. Reading cost is the remaining limit: the recorder reads only the entries that match its
words rather than a whole record. No size limit is set now.
