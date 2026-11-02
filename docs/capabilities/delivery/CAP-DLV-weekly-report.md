---
id: CAP-DLV-weekly-report
title: Evidence-based Weekly Reporting
summary: "An explicitly invoked or confirmed maintenance playbook produces immutable revision-bound weekly reports with delivery evidence, health limitations and prioritized actions, keeping authorized publication outcomes separate."
area: delivery
status: active
usecases:
  - UC-inspect-weekly-repository-progress
  - UC-publish-a-weekly-report
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md
---

# [CAP-DLV-weekly-report] Evidence-based Weekly Reporting

## 1. Scope and Invocation

The opt-in maintenance bundle supplies weekly-report independently of drift/upkeep. Explicit invocation through
`devkit-playbook`, exact `devkit playbook get maintenance/weekly-report` or the user's confirmation of a `spec`
intake offer follows
`CAP-DIST-context-and-playbooks`; selection/retrieval MUST NOT execute it. Generation SHOULD reuse available tools and
artifacts. It MUST NOT automatically run checks, maintenance or fixes, or create follow-ups. No scheduler,
detector, runtime publisher, history backend or standalone skill is included. Publication MUST have separate
authority. Rules that bind an agent, a host or a playbook step are checked by review only unless they name a check.

## 2. Intake and Evidence

Intake MUST record credential-free repository identity, scope, inspected SHA, local integration ref and resolved
SHA, generation timestamp and dirty state. The playbook MUST NOT fetch, switch branches or change source content
implicitly. The default interval MUST be the previous complete Monday-to-Monday calendar week in the configured user
timezone. IF the timezone is unknown, THEN the playbook MUST ask for it. The playbook MUST accept explicit endpoints.
It MUST record inclusive start, exclusive end, timezone and each endpoint's UTC offset; DST weeks need not be 168
hours. IF an interval is unresolved or ambiguous, THEN the playbook MUST reject it. The playbook MUST NOT treat a
local ref as proof of remote freshness.

Committed content at the captured revision MUST be the default evidence. Checkout lookup is a working-tree
observation reconciled against that SHA; explicitly selected uncommitted content MUST have a preserved diff/artifact
reference. The playbook MUST recheck HEAD, integration ref and relevant dirty content after collection and before
final verification. Changed evidence MUST be re-collected or marked unverified; it MUST NOT be silently mixed. The
playbook MUST preserve unrelated edits.

The playbook SHOULD use existing Git inspection, document lookup including completed specs/history, all intended
namespaces and complete pagination, changed ADRs/capabilities/use cases, workflow records and check artifacts. Every
factual claim MUST cite commit plus path/document ID, envelope or check artifact; assessments MUST be kept separate.
Dated claims MUST identify the timestamp basis. The playbook MUST NOT treat Git timestamps as integration proof; they
are discovery hints. IF integration time is unavailable, THEN the report MUST present reachable changes as snapshot
evidence rather than claiming weekly delivery. The report MUST NOT extend check results beyond their recorded
revision and scope. The playbook MUST NOT infer remote release or deployment.

A completed spec work claim MUST have completed status, checked tasks, verification/reconcile evidence and delivered
commits reachable from the captured integration SHA. A session work claim MUST have change, verification report and
reachability. The playbook MUST NOT treat proposals, checkboxes or commits alone as proof of delivery. IF evidence is
missing, THEN the report MUST lower the claim to unverified. Implementation without verified integration MUST be
reported separately.

## 3. Health, Comparison and Actions

The report MUST inventory sources with revision, scope, observed time, result and citation. Missing, stale, failed
and not-comparable sources MUST remain explicit; the report MUST NOT present none as clean. IF an optional source
fails, THEN generation MAY proceed with limitations. The playbook MUST compare only compatible scope, finding identity
and evidence. It MUST match feedback/proposal ID first, otherwise source, affected target and substantive
discrepancy. First observations MUST be marked new and evidenced continuing items recurring. A resolution MUST have
direct evidence; absence MUST be reported as unknown. An absent prior report or incompatible scope MUST be stated
explicitly. The playbook MUST prioritize actions by demonstrated impact and urgency with reasons and concrete next
steps. It MUST link existing open follow-ups; terminal feedback remains traceability and MUST NOT be reopened.
Generation MUST NOT create follow-up work.

## 4. Artifact and Outcome Contract

The playbook MUST select a local location explicitly, defaulting to owning-unit materials or an existing repository
materials location; otherwise it MUST resolve the location at invocation. It MUST NOT silently create a tracked
report on the default branch. The logical key is repository identity, scope and exact interval/timezone. Each run
MUST have a unique ID and source SHA, and its artifact MUST be collision-checked and exclusively created. Reruns
MUST name superseded runs and preserve earlier bytes. No seven-day TTL or automatic history discovery applies
(`ADR-mcp-runtime-and-shared-artifacts`).

Reports MUST contain identity/evidence inventory; completed and unintegrated work; decisions/behavior changes;
repository health; unresolved problems/prioritized actions; and prior comparison, limitations and outcomes.
Generation MUST complete only after artifact readback, identity and evidence-link verification, with unavailable
links marked unverified. IF required identity/interval or artifact verification fails, THEN generation MUST fail.
The playbook MUST compute SHA-256 after verification and MUST keep content immutable; changed content is a new run.

A separate local companion record MUST store run ID, artifact, digest, generation outcome, publication outcome,
destination, authority, attempts and receipt/error evidence. It MUST preserve attempts and changes without altering
the report. IF the companion is missing, THEN publication MUST be blocked; a missing companion MUST NOT erase a
verified report. Publication is:

- pending without destination, authority, publisher or permission;
- published only after verified destination receipt/link and matching content/run/digest;
- failed for confirmed failure;
- unknown for lost response or unverifiable destination.

The playbook MUST use only an existing authorized connector/command for an explicitly user-selected destination.
Invocation and integration policy MUST NOT authorize upload, message, commit, push or other external mutation. The
playbook MUST check destination collisions, require explicit authority for replacement and recheck the local digest
before send. A retry MUST retain run ID and exact bytes. The playbook MUST inspect unknown destination state first: a
matching receipt resolves published without resending; unverifiable stays unknown and requests disposition;
confirmed absence permits retry within authority. A mismatched destination MUST be treated as a collision. A
publication failure MUST leave completed generation intact. Controlled exercises MUST label simulated
authority/receipts and MUST NOT claim external publication.
