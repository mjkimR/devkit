---
reconcile_id: REC-viewer-adr-summary-wording
status: resolved
targets:
  - file: docs/decisions/2026-11/20261104-viewer-namespace-roadmap-discovery.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-viewer-indexed-decision-supersession.md
    resolution: modified
formal_docs:
  design: "none: wording-only change to two ADR summaries; no viewer source or mechanism changed"
  domain: "none: no domain concept, identity or lifecycle is introduced or renamed"
  operations: "none: no runbook, symptom or action owner is affected"
---

# Reconciliation: `SPEC-viewer-adr-summary-wording`

## Contract comparison

- `ADR-viewer-namespace-roadmap-discovery` (AC-01): the summary's concern drops "across local and library sources"
  and now reads "For viewer roadmap discovery". The decision (structural global and namespace roadmap paths without
  the namespace registry), the quality (reader independence) and the downside (unregistered directories can appear)
  are unchanged and still match the body, its history notes and `CAP-VIEW-repository-viewer` section 5.
- `ADR-viewer-indexed-decision-supersession` (AC-02): the summary's quality "to retain one read-only viewer across
  hosts" now reads "to keep the viewer read-only without running each repository's Python environment", which
  restates its Decision Drivers and selected option and fits `ADR-internal-repository-viewer`, under which
  `devkit viewer serve` is the only host. The concern, decision and downside are unchanged.
- AC-03: `git diff main -- docs/decisions/` changes only the two `summary:` lines; no body, Decision Outcome,
  `status` or `supersedes` field changed, so no capability restatement needs an update.
- Capabilities, use cases, architecture and glossary: unaffected; the change states no new behavior.

## Source feedback

- `FB-viewer-adr-summaries-name-library-hosts`: resolved; both summaries are reworded as proposed and verified by
  the checks above. Disposition appended to its file.
