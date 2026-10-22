---
id: UC-inspect-weekly-repository-progress
title: Inspect Weekly Repository Progress
summary: "A developer has an AI coding agent produce a bounded, revision-bound weekly report of verified work, decisions, health gaps and next actions, without implicitly publishing it or running maintenance."
area: governance
primary_actor: Developer
supporting_actors:
  - AI coding agent running the weekly-report playbook
  - Publication destination reached through an authorized connector or command
status: active
capabilities:
  - CAP-DLV-weekly-report
entrypoints:
  - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md
---

# [UC-inspect-weekly-repository-progress] Inspect Weekly Repository Progress

## 1. Goal

- **Goal**: obtain a revision-bound report of one week of repository progress, so that the developer can tell
  verified delivery from incomplete evidence, understand health limitations and choose useful next actions
- **Scope**: the `weekly-report` playbook of the opt-in `maintenance` catalog bundle, run by an AI coding agent with
  the repository's existing tools
- **Trigger**: the developer explicitly invokes the weekly-report playbook
- **Preconditions**: the `maintenance` bundle is installed; the developer supplies the scope and may supply the
  timezone or interval, the artifact location and a prior report; generation needs neither maintenance artifacts nor
  an external destination

---

## 2. Main Success Scenario

1. The developer explicitly invokes the weekly-report playbook with the report's scope (`CAP-DLV-weekly-report`).
2. The agent records the repository identity, the inspected and integration revisions, the generation time and the
   dirty state with local Git only, and resolves the interval: by default the previous complete Monday-to-Monday week
   in the developer's timezone, with inclusive start, exclusive end and each endpoint's UTC offset
   (`CAP-DLV-weekly-report`).
3. The agent gathers evidence from committed content at the captured revision, completed specs, all intended
   namespaces and every page included, and cites each factual claim by commit and path, document ID, envelope or
   check artifact (`CAP-DLV-weekly-report`).
4. The agent reports work as delivered only with its completion, verification and reachability evidence, and reports
   the rest as unverified (`CAP-DLV-weekly-report`).
5. The agent inventories health sources, compares findings with a prior report the developer named, and ranks next
   actions, linking existing open follow-ups without creating any (`CAP-DLV-weekly-report`).
6. The agent rechecks the inspected revision, the integration ref and the relevant dirty content before writing
   (`CAP-DLV-weekly-report`).
7. The agent writes the report to a new, exclusively created local artifact keyed by identity, scope and interval,
   reads it back, verifies its identity and evidence links, and records its SHA-256 (`CAP-DLV-weekly-report`).
8. The agent creates the companion outcome record with publication `pending` and gives the developer the artifact,
   both outcomes, the limitations and next steps (`CAP-DLV-weekly-report`).

---

## 3. Extensions

- **2a.** The developer's timezone is unknown: the agent asks for it; resumes at step 2.
- **2b.** The repository identity is missing, or the interval is reversed, ambiguous or unresolved: generation fails;
  the use case ends.
- **2c.** Neither the owning unit's materials nor a repository materials location exists: the agent asks for the
  artifact location and never silently creates a tracked report on the default branch; resumes at step 3.
- **3a.** A source is missing, stale, failed or not comparable: the agent records it with its reason as a limitation;
  an optional source's failure does not stop generation; resumes at step 4.
- **4a.** Work lacks integration time or verification evidence: the agent reports reachable changes as snapshot
  evidence and lowers unproven claims to unverified; resumes at step 5.
- **5a.** No prior report was named, or its scope is incompatible: the agent states that no comparison was made;
  resumes at step 6.
- **6a.** The revision, the integration ref or relevant dirty content changed during collection: the agent
  re-collects the affected evidence or marks it unverified; resumes at step 7.
- **7a.** A report for the same key already exists: the agent writes a new run with its own ID that names the run it
  supersedes and preserves the earlier bytes; resumes at step 8.
- **7b.** The readback, identity or required artifact verification fails: generation fails and nothing is published;
  an unavailable evidence link alone is marked unverified instead; the use case ends.
- **8a.** The developer selects a destination and grants authority to publish: the agent checks collisions, rechecks
  the digest and publishes through an existing authorized connector or command; the companion records `published`
  only with a verified receipt and matching content, run and digest, or `failed` on a confirmed failure, leaving the
  report intact; the use case ends.
- **8b.** The publication response is lost or the destination cannot be verified: the companion records `unknown`;
  the agent inspects the destination before any retry, records `published` on a verified match, keeps `unknown` for
  the developer's decision when it stays unverifiable, retries with the same run ID and bytes on confirmed absence,
  and treats different content as a collision; the use case ends.

---

## 4. Postconditions

- **Success guarantee**: an immutable, verified report exists at a new local artifact with its digest; every factual
  claim cites its evidence, and health gaps, unverified work and comparison limits are explicit; the companion record
  holds the generation and publication outcomes.
- **Minimal guarantee**: generation fetches nothing, switches no branch, changes no source, runs no maintenance,
  check or fix, and creates no follow-up work; a rerun never overwrites an earlier report; nothing external is
  mutated without the developer's explicit authority, and a failed publication leaves the completed report intact.

---

## 5. Acceptance Criteria (Given / When / Then)

### Scenario 1: Reports delivery with its evidence
- **Covers**: main success scenario
- **Given**: completed and unintegrated work, changed decisions and available verification artifacts
- **When**: the weekly report is generated for a captured revision and a half-open, timezone-aware interval
- **Then**: completed claims carry status, verification and reachability evidence; actions link existing follow-ups
  without creating work, and publication stays `pending` without a destination and authority

### Scenario 2: Fails on an unresolved interval
- **Covers**: 2b
- **Given**: an explicit interval whose end precedes its start
- **When**: the agent resolves the interval
- **Then**: generation fails and no report artifact is created

### Scenario 3: Keeps health gaps explicit
- **Covers**: 3a
- **Given**: a missing check artifact and a check result recorded for an older revision
- **When**: evidence is collected
- **Then**: both appear as health limitations with their reasons, and neither is reported as clean

### Scenario 4: Keeps unproven integration as snapshot evidence
- **Covers**: 4a
- **Given**: changes reachable from the captured integration SHA without a known integration time
- **When**: the agent classifies the week's work
- **Then**: the changes are reported as snapshot evidence, not as delivery within the week

### Scenario 5: States an incompatible prior report
- **Covers**: 5a
- **Given**: a named prior report whose scope differs from this run's
- **When**: findings are compared
- **Then**: the report states that the prior report is not comparable, and the absence of a finding is never read as
  resolved

### Scenario 6: Separates changing and dirty evidence
- **Covers**: 6a
- **Given**: dirty working-tree content, and an integration ref that moves during collection
- **When**: the agent rechecks before writing
- **Then**: dirty observations are labeled separately from committed evidence, and the changed evidence is
  re-collected or marked unverified, never silently mixed

### Scenario 7: Preserves the predecessor on a rerun
- **Covers**: 7a
- **Given**: a verified report for the same repository, scope and interval
- **When**: the developer reruns the playbook
- **Then**: a new artifact with a new run ID names the superseded run, and the earlier artifact's bytes are unchanged

### Scenario 8: Fails generation when verification fails
- **Covers**: 7b
- **Given**: a written report whose readback does not match the recorded identity
- **When**: the agent verifies the artifact
- **Then**: generation fails and nothing is published

### Scenario 9: Records an authorized publication outcome
- **Covers**: 8a
- **Given**: a verified report, a companion record, and a destination the developer selected with explicit authority
- **When**: the agent publishes through an existing authorized connector
- **Then**: the companion records `published` only after a verified receipt with matching content, run and digest, or
  `failed` on a confirmed failure, and the report is unchanged either way

### Scenario 10: Never retries a lost publication blindly
- **Covers**: 8b
- **Given**: a publication attempt whose response was lost
- **When**: the developer asks to retry
- **Then**: the agent inspects the destination first; a matching receipt resolves `published` without resending, an
  unverifiable state stays `unknown` for the developer's decision, and only confirmed absence permits a retry with the
  same run ID and bytes
