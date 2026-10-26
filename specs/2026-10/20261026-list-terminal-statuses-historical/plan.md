---
id: PLAN-list-terminal-statuses-historical
spec: SPEC-list-terminal-statuses-historical
---

# Technical Plan: `SPEC-list-terminal-statuses-historical` Terminal statuses are historical in document browsing

## 1. Constitution & Invariant Review

- `CAP-DOCS-document-lookup` records "Feedback defaults" as out of scope, from Non-Goal 1 of
  `SPEC-feedback-list-filters`. Reversing it is a lasting policy change: `ADR-terminal-statuses-are-historical`
  records it.
- `CAP-DOCS-document-model` rule 7 (historical documents) is extended: the existing historical set and the rules'
  use of it stay as they are (`SPEC-list-terminal-statuses-historical` Non-Goal 1).

## 2. Architecture Overview & Impact

- `devkit_spec.features.documents.repositories.index`: a `TERMINAL_STATUSES` table (kind to lower-cased statuses),
  `DocumentIndex.is_terminal(document)` and `DocumentIndex.is_browsing_historical(document)` (historical or
  terminal). `DocumentIndex.historical` and `is_historical` keep their meaning, so the governance rules are
  untouched.
- `usecases/browse.py` (`ListDocumentsUseCase`): the history filter uses `is_browsing_historical` and is skipped when
  `--history` or `--status` is given; the use case also returns `hidden`, the count of documents that pass every
  other filter but were left out as historical. The per-document `historical` field uses the browsing notion.
- `cli/commands.py` (`list`): its own page lines, since `utils/output.py` is outside the write scope and `refs`
  keeps `echo_page`: `[PAGE: ... hidden=<n>]`, `[NEXT_CMD: ...]` as before, then `[HISTORY_CMD: ...]` when
  `hidden > 0`; JSON gains `hidden`. The `--history` help names terminal statuses.
- `usecases/search.py`, `cli/search.py`: candidates use `is_browsing_historical`; help text updated.
- Bundle text: `adr-compaction` and `milestone-completion` pass `--history`; `scout.md` names terminal statuses.
  `--status open` call sites stay (spec assumption).
- Living Spec: `CAP-DOCS-document-model` rule 7 and library snippet, `CAP-DOCS-document-lookup` (scope note
  removed, `--history`, `--status`, paging and JSON keys), `CAP-DOCS-document-search` rule 1.

## 3. Component & Interface Design

```text
[PAGE: total=<n> offset=<n> limit=<n> count=<n> next=<n|-> hidden=<n>]   # list; hidden always present
[NEXT_CMD: devkit spec list ... --limit <n> --offset <n>]                 # when more pages follow
[HISTORY_CMD: devkit spec list ... --history [-w <root>] [--limit <n>]]   # only when hidden > 0
```

JSON `list`: `"hidden": <int>` beside `total`.

## 5. Error Handling & Edge Cases

- `--status` with a value no document carries keeps its `SPEC_LIST_STATUS_UNKNOWN` notice; `hidden=0`.
- Feedback inside a completed bundle stays current while open and becomes historical once its own status is
  terminal.
- A draft proposal shown as `reviewing` is not terminal.

## 6. Verification & Test Plan

- Integration tests in `packages/devkit-spec/tests/integration/features/documents/test_terminal_history.py` for
  AC-01 to AC-07; existing list and search tests updated where they assert the page line or a terminal status.
- `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`, `just rules-check`.
- Before/after `uv run devkit spec list feedback` and `list decision` counts in this repository.
