---
id: PROP-feedback-dedup-and-compaction
title: Feedback lookup before recording and compaction of closed feedback
summary: Search existing feedback of every status before recording a new item, and compact closed feedback into short symptom, response and reason records that keep the retired IDs as aliases, so the ledger stays searchable without hundreds of full files.
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-30
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/capabilities/delivery/
    - docs/capabilities/documents/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-feedback/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/
    - packages/devkit-spec/tests/
    - specs/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-feedback-dedup-and-compaction] Feedback lookup before recording and compaction of closed feedback

## 1. Background & Hypothesis

The feedback ledger holds 242 files, 233 of them closed (130 `resolved`, 60 `promoted`, 41 `dismissed`, 2
`forwarded`). `ADR-feedback-lifecycle` and `CAP-DLV-weekly-report` keep terminal feedback as traceability, so nothing
ever leaves the ledger. Browsing hides closed items, but every full file stays in repository searches, where agents
read them as if they were current.

Recording does not look at that ledger first. The `spec-feedback` sweep deduplicates only against open items with an
equal `target` string, and a direct recording checks nothing. In the 2026-10-30 run,
`FB-local-render-fix-ignores-worker-write-scope` duplicated `FB-render-stale-fix-ignores-worker-scope` because their
`target` values were worded differently. `devkit docs search "<observation>" --kind feedback --history` returned both
in its top three hits, so the lookup already exists; the procedure does not use it.

Hypothesis: if recording searches every status first, and closed feedback is periodically compacted into short
records that keep the retired IDs as aliases, the ledger stays a useful memory of what was fixed, routed or declined,
at a fraction of its size. Compaction mirrors the `adr-compaction` playbook: it never changes an outcome, only its
form.

## 2. Technical Spike Questions

- **Q1**: Compact record shape and location: one record per target area or per topic (like ADR compaction groups),
  where it lives (a `feedback/` directory under `specs/` or `docs/`), and how each entry carries the retired ID, the
  outcome and its destination in three short fields (symptom, response, reason).
- **Q2**: Which statuses compact and when: `resolved` and `dismissed` at once; `promoted` only after its destination
  completes, or at once with the destination named; `forwarded` only after an upstream answer.
- **Q3**: Lookup: is `devkit docs search --kind feedback --history` (hybrid; lexical without the search extra) enough
  for recording, or does it need a thin command that also reports matches inside compact records by their aliases?
  What score or rule decides "same observation"?
- **Q4**: Traceability after compaction: live references (a proposal's `Source feedback`) resolve through aliases;
  history (`reconcile.md` of completed specs) is not checked; the weekly report's terminal-feedback reading
  (`CAP-DLV-weekly-report`) must still work over compact records.
- **Q5**: ADR candidates: how the compaction run flags an entry whose reason is a lasting policy (a repeated
  dismissal reason, a rule of thumb) for the user to raise as an ADR, without writing ADRs on its own.

## 3. Proposed Design & Impact

1. **Search before recording.** Both the direct recording procedure and the sweep search existing feedback of every
   status with the observation's own words before writing. By the matched status:
   - `open`: do not record; name the existing ID (and add new evidence to it when the observation adds some).
   - `dismissed`: do not record unless there is new evidence against the recorded reason; then record and cite it.
   - `resolved`: record as a regression that cites the resolved ID.
   - `promoted` or `forwarded`: do not record; name the destination.
   The equal-`target` deduplication of the sweep is replaced by this lookup.
2. **Compaction playbook.** A user-invoked playbook (never automatic, like `adr-compaction`) groups closed feedback,
   writes one compact record per group with `aliases:` listing every retired ID, and per entry only:
   - **Symptom**: what was observed, one line.
   - **Response**: the outcome (`resolved` by `SPEC-...`, `promoted` to `PROP-...`, `dismissed`, `forwarded` to ...).
   - **Reason**: why, one line.
   It then deletes the originals and runs `devkit rules fix` so live references move to the record. It changes no
   outcome and reopens nothing. Git history keeps the full originals.
3. **ADR candidates.** The run lists entries whose reason reads as lasting policy for the user's decision; only the
   user raises one as an ADR, through the normal decision procedure.
4. **Contract.** A new ADR refines `ADR-feedback-lifecycle`: terminal feedback stays traceable through compact
   records, aliases and Git history rather than as full files. Impact: `spec-feedback` skill and its sweep reference,
   `source-feedback.md`, the `feedback-hygiene` playbook, the new playbook, `CAP-DLV-delivery-workflows` (feedback
   lifecycle), `CAP-DLV-weekly-report` if Q4 needs it, and `CAP-DOCS-document-model` only if the record needs a
   document-model change.

Out of scope: changing feedback statuses or the hygiene triage itself, and automatic compaction.

## 4. Lifecycle & Retirement Criteria

- On Acceptance: recorded with `devkit spec proposal accept` after Planning; handed off to a spec bundle on
  `dev-feedback-dedup-and-compaction`; the proposal is deleted there and its decisions become ADRs. The first
  compaction run over the existing 233 closed items is a separate, user-invoked run of the new playbook after
  integration.
- On Rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes the
  rejection ADR and deletes the proposal.
