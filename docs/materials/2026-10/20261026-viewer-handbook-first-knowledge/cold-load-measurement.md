---
id: MAT-viewer-handbook-cold-load
title: Knowledge tab cold-load baseline before handbook-first loading
summary: "Measures the viewer's Book and Proposals tabs cold and the handbook's first read on this repository: the Book tab takes about 1.1 s, 922 blob reads and 124k DOM nodes, of which about 0.47 s is rendering; the handbook's first read takes under 10 ms."
created_at: 2026-10-26
---

# [MAT-viewer-handbook-cold-load] Knowledge tab cold-load baseline before handbook-first loading

## Setup

- Repository: this worktree at `24570e8d` (`plan-viewer-handbook-first-knowledge`), 242 Markdown files under `docs/`
  and 922 under `docs/` and `specs/` together; the handbook has 37 pages per language (`v0.1.4` manifest).
- Server: `uv run devkit viewer serve --repo <worktree> --port 8791`, the committed `static/` build.
- Client: headless Chrome 155 over the DevTools protocol, HTTP cache disabled, a fresh tab per run, 1400x900, on an
  Apple M4 Pro. The probe is [`coldload-probe.mjs`](coldload-probe.mjs); raw results are
  [`cold-load-baseline.json`](cold-load-baseline.json).
- Method: open the page, wait for the rail and 3 s more so that the Dashboard's own loading does not overlap, clear
  resource timings, select the tab, then time until the loading status is gone and the view shows content. The
  "warm" Book run returns to the Dashboard and selects Book again within the 30-second index cache, so it measures
  rendering alone. Three runs each; medians below.

## Results

| Scenario | First content | Blob reads | Transferred | DOM nodes after |
| --- | --- | --- | --- | --- |
| Book tab, cold | 1094 ms (1073-1199) | 922 | 7.19 MB | 124k |
| Book tab, index cached (render only) | 470 ms main-thread script (460-472) | 0 | 0 | 124k |
| Proposals tab, cold | 631 ms (612-707) | 922 | 7.20 MB | 1.9k |
| Handbook first read: `handbook/manifest.json` and `handbook/en/README.md` | 5 ms + 2 ms (fetch only) | 2 | 7.8 kB page | not measured |

- The Book tab renders 154 chapters synchronously right after the index arrives: first content and a quiet main
  thread coincide.
- The index (`indexDocuments` over `docs/` and `specs/`) costs about 0.6 s and is shared by Book, Proposals and
  Specs; the Book adds about 0.47 s of `renderDocument` work and 120k DOM nodes on top of it.
- A handbook page is a single document of 7.8 kB; at the Book's average of about 3 ms per chapter, its rendering
  adds a few milliseconds. The handbook read needs no index.

## What this decides

- **Q6**: computing the book only on an explicit request removes both its index and its rendering from the cold
  load of the Book tab: about 1.1 s and 922 reads become two reads where a handbook exists, and zero reads with an
  absence note where none does. Viewport rendering is not needed for the cold load; after the request the book costs
  what it costs today.
- The index remains the cold cost of Proposals and Specs (about 0.6 s, 922 reads), which anchor-first loading
  (`FB-viewer-knowledge-anchor-loading`) addresses and this proposal does not.

## Reproducing after the change

A development worker serves its worktree the same way and runs
`node coldload-probe.mjs http://127.0.0.1:<port>/ <repo-id> 3 <out.json> [<tab label>] [<readiness selector>]` from a
copy in the proposal's ignored `.probe/`. The defaults reproduce this baseline (`Book`, chapters present); the
after-run passes the new tab label and a selector for the handbook article or the absence note. The table above is the base measurement; same-machine numbers are
comparable, other machines compare blob counts and DOM nodes rather than milliseconds.

## After the change

- Repository: this worktree at `68f428d0` (`dev-viewer-handbook-first-knowledge`), served and probed the same way with
  Chrome 155 on an Apple M4 Pro, as
  `node coldload-probe.mjs http://127.0.0.1:8792/ <repo-id> 3 cold-load-after.json Read .handbook-page`. The tab is
  `Read` and readiness is the rendered handbook page; raw results are
  [`cold-load-after.json`](cold-load-after.json). Medians of three runs.

| Scenario | First content | Blob reads | Transferred | DOM nodes after |
| --- | --- | --- | --- | --- |
| Read tab, cold (handbook, no book request) | 52 ms (39-109) | 3 | 14.2 kB | 3.1k |
| Read tab, again after the Dashboard | 15 ms (14-18) | 3 | 14.2 kB | 3.1k |
| Proposals tab, cold | 720 ms (710-1428) | 927 | 7.02 MB | 1.9k |

- Against the base, the reading tab's cold load drops from 922 to 3 blob reads (`handbook/manifest.json`, `VERSION`,
  `handbook/en/README.md`), from 124k to 3.1k DOM nodes, from 154 chapters to none, and from about 1.1 s to about
  50 ms.
- Proposals still index `docs/` and `specs/` (927 reads, five more files than at the base); its time is within the
  base's range apart from one slow run, as expected, since this change leaves that index alone
  (`FB-viewer-knowledge-anchor-loading`).
- The book after the request costs what the base's Book tab cost; this change does not alter that rendering
  (`FB-viewer-book-rendering`).
