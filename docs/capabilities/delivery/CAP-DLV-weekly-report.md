---
id: CAP-DLV-weekly-report
title: Evidence-based Weekly Reporting
summary: "An explicitly invoked maintenance playbook produces immutable revision-bound weekly reports with delivery evidence, health limitations and prioritized actions, keeping authorized publication outcomes separate."
area: delivery
status: active
usecases:
  - UC-inspect-weekly-repository-progress
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md
---

# [CAP-DLV-weekly-report] Evidence-based Weekly Reporting

## 1. Scope and Invocation

The opt-in maintenance bundle supplies weekly-report independently of drift/upkeep. Explicit invocation through
`devkit-playbook` or exact `devkit playbook get maintenance/weekly-report` follows
`CAP-DIST-context-and-playbooks`; selection/retrieval never executes it. Generation reuses available tools and
artifacts without automatically running checks, maintenance, fixes or creating follow-ups. No scheduler,
detector, runtime publisher, history backend or standalone skill is included. Publication needs separate authority.

## 2. Intake and Evidence

Record credential-free repository identity, scope, inspected SHA, local integration ref and resolved SHA,
generation timestamp and dirty state. Never fetch, switch branches or change source content implicitly.
The default interval is the previous complete Monday-to-Monday calendar week in the configured user timezone;
unknown timezone requires input, and explicit endpoints are accepted. Record inclusive start, exclusive end,
timezone and each endpoint's UTC offset; DST weeks need not be 168 hours. Reject unresolved/ambiguous intervals.
A local ref does not prove remote freshness.

Committed content at the captured revision is default. Checkout lookup is a working-tree observation reconciled
against that SHA; explicitly selected uncommitted content needs a preserved diff/artifact reference. Recheck
HEAD, integration ref and relevant dirty content after collection and before final verification; changed evidence
must be re-collected or marked unverified, never silently mixed. Preserve unrelated edits.

Use existing Git inspection, document lookup including completed specs/history, all intended namespaces and
complete pagination, changed ADRs/capabilities/use cases, workflow records and check artifacts. Every factual claim
cites commit plus path/document ID, envelope or check artifact; assessments are separate. Dated claims identify
the timestamp basis. Git timestamps are discovery hints, never integration proof. Without integration time,
report reachable changes as snapshot evidence rather than claiming weekly delivery. Check results cover only
their recorded revision and scope. Never infer remote release or deployment.

Completed spec work requires completed status, checked tasks, verification/reconcile evidence and delivered
commits reachable from the captured integration SHA. Session work needs change, verification report and
reachability. Proposals, checkboxes and commits alone prove no delivery; missing evidence lowers claims to
unverified and implementation without verified integration is separate.

## 3. Health, Comparison and Actions

Inventory sources with revision, scope, observed time, result and citation. Missing, stale, failed and
not-comparable remain explicit; none means clean. Optional-source failure permits generation with limitations.
Compare only compatible scope, finding identity and evidence. Match feedback/proposal ID first, otherwise source,
affected target and substantive discrepancy. First observations are new, evidenced continuing items recurring,
and resolution needs direct evidence; absence is unknown. Absent prior report or incompatible scope is explicit.
Prioritize actions by demonstrated impact and urgency with reasons and concrete next steps. Link existing open
follow-ups; terminal feedback remains traceability and is not reopened. Generation creates no follow-up work.

## 4. Artifact and Outcome Contract

Select a local location explicitly, defaulting to owning-unit materials or an existing repository materials
location; otherwise resolve it at invocation. Never silently create a tracked report on the default branch.
The logical key is repository identity, scope and exact interval/timezone. Each run has a unique ID and source
SHA; use a collision-checked exclusively created artifact. Reruns name superseded runs and preserve earlier bytes.
No seven-day TTL or automatic history discovery applies (`ADR-mcp-runtime-and-shared-artifacts`).

Reports contain identity/evidence inventory; completed and unintegrated work; decisions/behavior changes;
repository health; unresolved problems/prioritized actions; and prior comparison, limitations and outcomes.
Generation completes only after artifact readback, identity and evidence-link verification, with unavailable
links marked unverified. Required identity/interval or artifact verification failure fails generation. Compute
SHA-256 after verification and keep content immutable; changed content is a new run.

A separate local companion record stores run ID, artifact, digest, generation outcome, publication outcome,
destination, authority, attempts and receipt/error evidence. It preserves attempts and changes without altering
the report. Missing companion blocks publication but does not erase a verified report. Publication is:

- pending without destination, authority, publisher or permission;
- published only after verified destination receipt/link and matching content/run/digest;
- failed for confirmed failure;
- unknown for lost response or unverifiable destination.

Use only an existing authorized connector/command for an explicitly user-selected destination. Invocation and
integration policy never authorize upload, message, commit, push or other external mutation. Check destination
collisions, require explicit authority for replacement and recheck local digest before send. Retrying retains
run ID and exact bytes. Inspect unknown destination state first: a matching receipt resolves published without
resending; unverifiable stays unknown and requests disposition; confirmed absence permits retry within authority.
A mismatched destination is a collision. Publication failure leaves completed generation intact. Controlled
exercises label simulated authority/receipts and make no claim of external publication.
