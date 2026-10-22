---
id: UC-publish-a-weekly-report
title: Publish a Weekly Report
summary: "A developer has an AI coding agent publish an existing verified weekly report to a destination the developer selected under explicit authority, recording a verified publication outcome without altering the report or retrying blindly."
area: governance
primary_actor: Developer
supporting_actors:
  - AI coding agent running the weekly-report playbook
  - Publication destination reached through an existing authorized connector or command
status: active
capabilities:
  - CAP-DLV-weekly-report
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md
created_at: 2026-10-22
---

# [UC-publish-a-weekly-report] Publish a Weekly Report

## 1. Goal

- **Goal**: have an existing verified weekly report reach the destination the developer selected, with a verified
  publication outcome in its companion record, so that the developer can share the report knowing whether it arrived
  intact, without overwriting other content or sending it twice
- **Scope**: the publication part of the `weekly-report` playbook of the opt-in `maintenance` catalog bundle, run by an
  AI coding agent through an existing authorized connector or command; generating the report is
  `UC-inspect-weekly-repository-progress`
- **Trigger**: the developer selects a destination for an existing verified report and grants explicit authority to
  publish it
- **Preconditions**: the report was generated and verified with its recorded SHA-256
  (`UC-inspect-weekly-repository-progress`); invoking the playbook or the integration policy alone never authorizes
  publication

---

## 2. Main Success Scenario

1. The developer selects a destination for an existing verified report and grants explicit authority to publish it
   (`CAP-DLV-weekly-report`).
2. The agent reads the report's companion outcome record and resolves an existing authorized connector or command
   that reaches the selected destination (`CAP-DLV-weekly-report`).
3. The agent checks the destination for a collision with existing content (`CAP-DLV-weekly-report`).
4. The agent rechecks the local artifact's digest against the recorded SHA-256 (`CAP-DLV-weekly-report`).
5. The agent sends the report's exact bytes under its run ID through the authorized connector or command and records
   the attempt, destination and authority in the companion record (`CAP-DLV-weekly-report`).
6. The agent verifies the destination's receipt or link and that the destination's content, run and digest match the
   report (`CAP-DLV-weekly-report`).
7. The agent records publication `published` with the receipt evidence in the companion record, leaving the report
   unchanged, and gives the developer the destination and the outcome (`CAP-DLV-weekly-report`).

---

## 3. Extensions

- **\*a.** The publication is a controlled exercise: the agent labels the authority and receipts as simulated and
  claims no external publication; the use case continues.
- **2a.** The companion outcome record is missing, or it does not record a completed generation: publication is
  blocked and nothing is sent; a verified report stays intact; the use case ends.
- **2b.** No existing authorized connector or command reaches the destination, or permission is missing: publication
  stays `pending`; the agent preserves the local artifact and states what is missing; the use case ends.
- **3a.** The destination already holds content at the target (a collision): the agent replaces it only under the
  developer's explicit authority naming that target and resumes at step 4; without that authority nothing is sent
  and the use case ends.
- **4a.** The local artifact's digest no longer matches the recorded SHA-256: nothing is sent, because changed content
  is a new run that generation must produce; the use case ends.
- **5a.** The connector or command reports a confirmed failure: the companion records `failed` with the error
  evidence, and the report and its completed generation stay intact; a later retry resends the same run ID and exact
  bytes; the use case ends.
- **5b.** The publication response is lost: the companion records `unknown`, and the agent inspects the destination
  before any retry; resumes at step 6.
- **6a.** The destination holds content whose content, run or digest differs from the report: the agent treats it as
  a collision; resumes at step 3.
- **6b.** The destination cannot be verified: the companion keeps `unknown`, and the agent requests the developer's
  disposition without resending; the use case ends.
- **6c.** Inspection after a lost response confirms the report is absent from the destination: the agent retries
  within the developer's authority with the same run ID and exact bytes; resumes at step 4.

---

## 4. Postconditions

- **Success guarantee**: the companion record holds publication `published` with the destination, the authority, the
  attempts and the verified receipt or link, and the destination's content, run and digest match the report; the
  report's bytes and its generation outcome are unchanged.
- **Minimal guarantee**: publication changes only the companion record, which preserves every attempt with its
  outcome and evidence; the completed report stays intact after any failure; nothing is sent without a destination the
  developer selected and explicit authority, no target is replaced without authority naming it, changed content is
  never sent under the existing run, and an `unknown` publication is never retried before the destination is
  inspected.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Records an authorized publication only with a verified receipt
- **Covers**: main success scenario
- **Given**: a verified report, its companion record with publication `pending`, and a destination the developer
  selected with explicit authority and an existing authorized connector
- **When**: the agent publishes the report through that connector
- **Then**: the companion records `published` only after a verified receipt with matching content, run and digest,
  and the report is unchanged

### Scenario 2: Labels a controlled exercise as simulated
- **Covers**: \*a
- **Given**: a publication run as a controlled exercise with simulated authority and receipts
- **When**: the agent records the outcome
- **Then**: the authority and receipts are labeled simulated, and no external publication is claimed

### Scenario 3: Blocks publication without a companion record
- **Covers**: 2a
- **Given**: a verified report whose companion outcome record is missing
- **When**: the developer asks to publish it to a selected destination
- **Then**: nothing is sent, and the verified report stays intact

### Scenario 4: Keeps publication pending without an authorized publisher
- **Covers**: 2b
- **Given**: a selected destination that no existing authorized connector or command reaches
- **When**: the agent resolves how to publish
- **Then**: publication stays `pending`, the local artifact is preserved, and the agent states what is missing

### Scenario 5: Never replaces colliding content without naming authority
- **Covers**: 3a
- **Given**: a destination target that already holds other content, and authority that does not name that target
- **When**: the agent checks the destination before sending
- **Then**: nothing is sent, and the destination's existing content is unchanged

### Scenario 6: Sends nothing when the local digest changed
- **Covers**: 4a
- **Given**: a local artifact whose bytes no longer match the recorded SHA-256
- **When**: the agent rechecks the digest before sending
- **Then**: nothing is sent, and the changed content is left for a new run

### Scenario 7: Records a confirmed failure without touching the report
- **Covers**: 5a
- **Given**: an authorized publication attempt that the connector reports as a confirmed failure
- **When**: the agent records the outcome
- **Then**: the companion records `failed` with the error evidence, and the report and its completed generation are
  unchanged

### Scenario 8: Never retries a lost publication blindly
- **Covers**: 5b, 6c
- **Given**: a publication attempt whose response was lost
- **When**: the developer asks to retry
- **Then**: the agent inspects the destination first; a matching receipt resolves `published` without resending, and
  only confirmed absence permits a retry with the same run ID and bytes

### Scenario 9: Treats different destination content as a collision
- **Covers**: 6a
- **Given**: a publication whose destination holds content with a different run or digest than the report
- **When**: the agent verifies the destination
- **Then**: the companion does not record `published`, and the agent handles the destination as a collision

### Scenario 10: Leaves an unverifiable destination for the developer's decision
- **Covers**: 6b
- **Given**: a publication in state `unknown` whose destination cannot be verified
- **When**: the agent inspects the destination
- **Then**: the companion keeps `unknown`, nothing is resent, and the agent requests the developer's disposition
