---
id: PLAN-viewer-decision-supersession
spec: SPEC-viewer-decision-supersession
---

# Technical Plan: `SPEC-viewer-decision-supersession`

## 1. Constitution & Invariant Review

No invariant conflict. `ADR-repository-viewer` keeps parsing in the browser and both source hosts share tree/blob interfaces.
`ADR-viewer-indexed-decision-supersession` selects this design. The generic source API, backend and package graph remain unchanged.

## 2. Architecture Overview & Impact

Add pure relation extraction and a shared summary component under the viewer's document feature. Files owns a lazy
index lifecycle; KnowledgeViews supplies its existing checkout index to Read and PADR chapters. No new dependency.

## 3. Component & Interface Design

`deriveSupersession(subject, documents)` returns outgoing/incoming relation rows with written ID, canonical target,
status, whole/partial scope and nullable source text. A dedicated canonical lookup includes aliases and refuses ambiguity.
The subject replaces the same-path indexed copy before derivation. A visible-line parser mirrors Python statement rules.

The summary accepts a subject, index/loading/errors and navigation/reload callbacks. It emits ordinary focusable
links, escaped source text and explicit loading/empty/incomplete/error states. ChapterSection places it after the
header. DocumentViewer receives Files state from SddViewer and never requests an index itself.

## 4. Storage & State Management

Use existing source/ref document caches. Relation reload invalidates the source cache and replaces only related
index data. Abort controllers and generation guards prevent older source/ref/path work publishing new state.
KnowledgeViews reload uses its existing index lifecycle. Files derives its subject from the displayed raw body.

## 5. Error Handling & Edge Cases

Keep successful relations on partial read failure, list failed paths and offer reload. Missing/ambiguous identities
remain nonlinks. PADRs are proposed outgoing only. Whole status requires reciprocal superseded_by and status.
No statement is synthesized. Empty partial incoming scans do not claim None recorded.

## 6. Verification & Test Plan

AC-01–03: pure parser/alias/classification fixtures plus summary component tests.
AC-04–06: Read/Files/PADR integration tests, exact-subject TTL/reload, source switch/abort and request budgets.
AC-07: hostile text rendering fixtures. AC-08: document rules and generated artifact check.
Run `just viewer install`, `just viewer lint`, `just viewer check`, `just viewer test`, `just viewer pack`,
`just viewer build`, `uv run devkit generated check viewer-assets`, required rules and
`just test-affected --base b04b5ac8b4349f083a42707567dae964d4b06e98 --tier all`, preserving full fallback.
