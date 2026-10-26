---
reconcile_id: REC-list-terminal-statuses-historical
status: pending
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
    resolution: modified
  - file: docs/decisions/2026-10/20261026-terminal-statuses-are-historical.md
    resolution: modified
  - file: docs/usecases/documents/UC-find-the-right-documents.md
    resolution: waived
    rationale: "Its success guarantee (line 73) says completed spec bundles stay out of results unless history is asked; that still holds, and CAP-DOCS-document-model rule 8 owns the added terminal-status rule. docs/usecases/ is outside this run's write scope, so naming terminal statuses there is left to the Host at integration."
---
# Reconcile terminal statuses as historical

`CAP-DOCS-document-model` gains rule 8: feedback `resolved`, `promoted`, `dismissed` and `forwarded`, decision
`superseded` and proposal `rejected` are historical for browsing and search whatever bundle holds them, while the
rules keep checking them; its status field row and library snippet name `is_terminal` and `is_browsing_historical`.
Rule 7 and `DocumentIndex.historical` are unchanged, so no governance capability changes.

`CAP-DOCS-document-lookup` drops the "Feedback defaults" scope note, extends `--history` to terminal statuses,
states that a given `--status` replaces the default hiding, and adds `hidden=` to the `list` page line, the
`[HISTORY_CMD: ...]` line (paging rule 4), the JSON `hidden` key and the usage and output examples.
`CAP-DOCS-document-search` rule 1 names the same historical set for candidates. `CAP-SRCH-document-search` states no
history rule and is unchanged.

`ADR-terminal-statuses-are-historical` records the reversal of Non-Goal 1 of `SPEC-feedback-list-filters`; that
completed spec stays as history.

Call sites: `adr-compaction` and `milestone-completion` pass `--history`, the scout role names terminal statuses, and
the catalog `weekly-report` playbook (which already passed `--history`) names what it now brings back. Call sites
that want current items (`spec-next`, `next-work`, `spec-plan`, completion, the feedback sweep, `feedback-hygiene`,
`envelope.md`) keep their commands; `--status open` stays explicit and correct. No architecture document, glossary
term or entrypoint changes: the touched code lies under the existing entrypoints of the three capabilities. No work
is deferred and the spec carries no source feedback.
