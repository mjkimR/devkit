---
id: DOMAIN-feedback-lifecycle
title: "Feedback lifecycle"
status: active
area: delivery
summary: "Distinguishes the five feedback statuses, the actor and moment that set each, and how the recording lookup and the recurring flag act on them; rules stay with the document model, delivery and harness owners."
related_capabilities: [CAP-DOCS-document-model, CAP-DLV-delivery-workflows, CAP-HARN-agent-guidance, CAP-DLV-proposal-planning]
related_domains: [DOMAIN-delivery-relationships]
related_designs: [DESIGN-proposal-handoff]
---

# [DOMAIN-feedback-lifecycle] Feedback lifecycle

A feedback file closes in one of four ways, and the four look alike from the outside: each is terminal, each keeps
the file as traceability, and each is written by a different actor at a different moment. Readers confuse
`promoted` with `resolved` because both follow a decision to act on the observation, but only one claims that a fix
was verified. They confuse `dismissed` with `resolved` because both end the work without follow-up, and they read
`forwarded` as a draft upstream report when it means a report that was actually submitted. The statuses and their
rules are spread over the document model, the delivery and harness capabilities and the spec bundle's skills; this
entry relates them.

## Relationship overview

`CAP-DOCS-document-model` (Feedback lifecycle) names five statuses, `open`, `promoted`, `resolved`, `dismissed` and
`forwarded`, and makes only `open` actionable. The docs index treats the other four as terminal: `devkit docs list`
and `devkit docs search` hide them unless `--history` or an explicit `--status` asks for them (the `terminal_statuses`
of the feedback kind in
[kinds.py](../../../packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py)). The glossary entries
**Feedback promotion**, **Feedback resolution** and **Source feedback** in `docs/steering/glossary.md` give the short
definitions; this table separates the statuses by what each claims and who writes it.

| Concept or relationship | Distinction | Authoritative owner |
| --- | --- | --- |
| `open` | The only actionable status, and the only one capture writes. A new file starts here and stays here until a hygiene decision or a verified direct fix; capture, handoff and relocation never change it. | `CAP-DOCS-document-model` Feedback lifecycle; `CAP-HARN-agent-guidance` Feedback capture policy |
| `promoted` | Tracking moved to identified follow-up work (a rule, playbook, ADR, proposal or spec) that actually received the item. Claims nothing about a fix; it stays `promoted` when that work finishes. | `ADR-feedback-lifecycle-ledger`; `CAP-DLV-delivery-workflows` Source feedback at completion |
| `resolved` | A direct fix of an explicitly linked open source, fully addressed and verified by tests or review in a session or spec, without promotion. Partial, deferred or unverified fixes stay `open`. | `CAP-DOCS-document-model` Feedback lifecycle; `CAP-HARN-agent-guidance` Feedback capture policy |
| `dismissed` | A reasoned decline: normal behavior, obsolete, already addressed or without observed evidence. No work is routed and no fix is claimed. | `CAP-DOCS-document-model` Feedback lifecycle; spec bundle `feedback-hygiene` playbook Step 3 |
| `forwarded` | An upstream report that was actually submitted under explicit external-send authorization, with its report location. A draft report or unresolved ownership stays `open`. | `CAP-HARN-agent-guidance` Feedback capture policy; `feedback-hygiene` Step 3 |
| Promoted vs resolved | Both are terminal and both carry a Disposition. Promotion closes on routing, resolution on verification; completing promoted work never converts its source to `resolved`. | `CAP-DLV-delivery-workflows` Source feedback at completion |
| Dismissed vs resolved | Both end without follow-up work. Dismissal records a reason that nothing needs fixing; resolution records the fixing SPEC ID or session paths, the outcome and the evidence. A recurrence reopens neither: the lookup below records a new item or nothing. | `CAP-HARN-agent-guidance` Feedback capture policy |
| `recurring` | A frontmatter flag, not a status: `true` when the recorder has seen the observation before, set on a fresh item that cites a `resolved` predecessor. Hygiene orders `recurring: true` right after `critical`. | spec bundle `spec-feedback` skill step 4 and step 2; `feedback-hygiene` Step 1 |
| Recording lookup | Before writing, every recording searches feedback of every status and acts on the matched status; the matched status, not a search score, decides whether a new file is written. | `CAP-HARN-agent-guidance` Feedback capture policy; `spec-feedback` step 2 |
| Source feedback | The FB IDs a proposal or spec names in its `Source feedback` section. Handoff and drafting carry the references; only open direct-fix sources are checked at completion. Terminal sources need no disposition or re-verification. | `CAP-DLV-proposal-planning` §3.1; `CAP-DLV-delivery-workflows` Source feedback at completion |

### Who changes a status, and when

Four actors write feedback status, each at a fixed moment:

1. **Capture** (`spec-feedback`, direct or in a sweep) writes a new file with `status: open` and never changes an
   existing status (`CAP-HARN-agent-guidance` Feedback capture policy). Planning writes into the proposal's
   `feedback/`, Development into the spec's and work without a Unit into the month-level backlog.
2. **Backlog triage** (`feedback-hygiene`, in a session the user invoked or confirmed) sets `promoted`, `dismissed`
   or `forwarded` with the user's decision, and appends one `- **Disposition**:` line naming each destination ID,
   path or report location and a one-line summary or reason. Promotion here is the moment the proposal or other
   follow-up work receives the item; the destination records the source FB ID in its `Source feedback` section
   (`CAP-HARN-agent-guidance` §4.5 `feedback-hygiene`).
3. **A fixing task at completion** sets `resolved` on an explicitly linked open source it fully addressed and
   verified, at `living-spec-draft` with the outcome recorded in `reconcile.md` for a spec, or at `report-session`
   for a session, and appends a Disposition with the SPEC ID or changed paths, outcome and evidence. It may set its
   own new resolution back to `open` when later changes invalidate the evidence; it never revisits pre-existing
   terminal feedback (`CAP-DLV-delivery-workflows` Source feedback at completion; spec bundle
   `skills/spec/references/source-feedback.md`).
4. **The user-invoked `feedback-consolidation` playbook** changes form, never outcome: it deletes eligible
   `resolved` files and folds `promoted`, `dismissed` and `forwarded` files into per-area, same-status
   `FB-consolidated-<area>-<status>` records that keep the old IDs as aliases (`CAP-DLV-delivery-workflows` Source
   feedback at completion; `ADR-feedback-lifecycle-ledger`).

Handoff moves files without changing status: open files enter the new spec's `feedback/`, settled files go to the
materials directory, and the handoff preflight refuses a file with a missing or unknown status
(`CAP-DLV-proposal-planning` §3.1; `plan_open_feedback` in
[feedback.py](../../../packages/devkit-spec/src/devkit_spec/features/proposals/usecases/feedback.py)). Spec
completion never closes feedback on its own (`CAP-DOCS-document-model` Feedback lifecycle).

### What the recording lookup does with each status

`CAP-HARN-agent-guidance` (Feedback capture policy) and step 2 of the `spec-feedback` skill act on the status of a
hit that describes the same symptom of the same asset or behavior:

| Matched status | Effect on recording |
| --- | --- |
| `open` | No new file; the existing ID is named and new evidence goes into it (inside the write scope) or into the report. |
| `dismissed` | No new file, unless evidence contradicts the recorded reason; then a new file cites the ID. |
| `resolved` | A fresh file, citing the resolved ID with `recurring: true` while that ID still resolves. |
| `promoted`, `forwarded` | No new file while the destination is live; once it is completed, rejected, closed or no longer resolves, a new file cites the ID. |

A hit in a consolidated record is decided by the entry that matches the observation. A recurrence after a resolved
file was deleted by consolidation is recorded as a fresh observation (`CAP-DLV-delivery-workflows` Source feedback
at completion).

## Worked example: one observation, four outcomes

This is a nonexecuted example. During a Development run, an agent notices that a skill's lookup command misses
terminal feedback and records it in the spec's `feedback/lookup-skips-history.md` with `status: open`.

- **Promoted.** In a later hygiene session the user agrees to fix it in a new proposal. The file becomes
  `promoted` with `- **Disposition**: PROP-<slug>: route the lookup fix`, and the proposal lists the ID under
  `Source feedback`. When that work is handed off and completed, the file stays `promoted`; the completed spec
  does not touch it. If the same symptom appears while the proposal is still open, recording names the ID and writes
  nothing.
- **Resolved.** Instead, a spec that names the ID as an open direct-fix source changes the command and a test
  verifies it. At `living-spec-draft` the source becomes `resolved` with a Disposition naming the SPEC ID, outcome and
  test. If the symptom returns months later, a new file cites the resolved ID with `recurring: true`.
- **Dismissed.** Instead, hygiene finds that the command behaves as its capability states. The file becomes
  `dismissed` with that reason. A later identical observation records nothing unless it brings evidence against the
  reason.
- **Forwarded.** Instead, the command belongs to an installed upstream tool. Hygiene drafts a report; the file stays
  `open` until the user authorizes the submission, then becomes `forwarded` with the report location.

## Authority boundary

This entry relates statuses; it sets no status, adds no transition and defines no term. `CAP-DOCS-document-model`
(Feedback lifecycle) owns the status set, terminality and the closing semantics. `CAP-HARN-agent-guidance` (Feedback
capture policy and §4.5) owns capture, scope, the recording lookup and the hygiene and consolidation playbook
contracts. `CAP-DLV-delivery-workflows` (Source feedback at completion) owns completion dispositions and
consolidation. `CAP-DLV-proposal-planning` §3.1 owns Planning feedback, its handoff routing and retirement.
`ADR-feedback-lifecycle-ledger` records the decision behind all of them. The spec bundle's `spec-feedback` skill,
`feedback-hygiene` playbook and `skills/spec/references/source-feedback.md` hold the procedures; the glossary holds
the definitions.

## Maintenance and next action

Update this entry when a status is added or removed, when an actor gains or loses the right to change a status, or
when the recording lookup changes its action for a status. To record an observation, read the `spec-feedback`
skill; to triage open items, the `feedback-hygiene` playbook; to close a source your task fixed,
`skills/spec/references/source-feedback.md`. For how feedback moves at handoff, read `CAP-DLV-proposal-planning` §3.1
or `DESIGN-proposal-handoff`.
