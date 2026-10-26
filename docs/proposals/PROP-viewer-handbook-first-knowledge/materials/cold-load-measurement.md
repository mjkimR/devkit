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
`node coldload-probe.mjs http://127.0.0.1:<port>/ <repo-id> 3 <out.json>` from a copy in the proposal's ignored
`.probe/`. The Book scenario's readiness selector waits for chapters, so the after-run selects the book control or
replaces the selector with the handbook article. The table above is the base measurement; same-machine numbers are
comparable, other machines compare blob counts and DOM nodes rather than milliseconds.
