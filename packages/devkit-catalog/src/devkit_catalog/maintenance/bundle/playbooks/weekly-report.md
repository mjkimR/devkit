---
name: weekly-report
description: Manually generate a revision-bound weekly repository report with evidence, health gaps and prioritized actions, then separately publish only to an authorized destination.
aliases: [weekly maintenance report, repository progress report, weekly delivery evidence]
---

# Weekly report

Run only on explicit invocation for this task, through `devkit-playbook` or exact
`devkit playbook get maintenance/weekly-report`. Load the returned bundle context once per agent context.

- Selection and retrieval never execute this procedure.
- Use existing repository tools and authorized connectors; this content adds no scheduler, detector, history
  backend or publisher.
- Generation runs no maintenance sweep, full test suite, automatic fix, feedback creation or proposal creation.

## 1. Capture identity and interval

Follow repository instructions and permissions.

1. Record a credential-free repository identity (canonical local path or configured remote), selected scope,
   inspected commit SHA, integration branch/ref and resolved SHA, generation timestamp and dirty paths.
   - Use local Git inspection, for example `git rev-parse HEAD`, `git rev-parse <integration-ref>^{commit}` and
     `git status --short`; do not fetch, switch branches or modify sources.
   - An unavailable required identity fails generation. A local integration ref does not prove remote freshness.
2. Fix the interval:
   - Accept explicit start/end timestamps and timezone, or use the previous complete Monday 00:00 to Monday 00:00
     calendar week in the configured user timezone. If the timezone is unknown, require it at invocation.
   - Record inclusive start, exclusive end, timezone name and UTC offsets at both boundaries.
   - Resolve local calendar boundaries before converting to UTC: a DST week may be 167 or 169 hours.
   - Reject reversed or ambiguous endpoints until resolved.
   - An event exactly at start belongs; one exactly at end does not.
   - An invalid or unresolved interval fails generation.
3. Select a local artifact location explicitly:
   - Default to the owning work unit's materials or the repository's existing materials location; if neither
     exists, resolve it at invocation.
   - Do not silently create a tracked report on the default branch.
   - Record an optional named prior report. No history discovery service or seven-day TTL applies.
4. Build a logical report key from repository identity, scope and exact interval/timezone.
5. Allocate a unique run ID, source SHA and new filename, checking collisions and creating exclusively. A rerun
   names any superseded run and preserves its artifact; never overwrite another run.

## 2. Gather revision-bound evidence

Default to committed content at the captured SHA (`git show <sha>:<path>`, local history and reachability checks).

- Where document lookup is installed, include completed specs with `--history`, all intended namespaces and
  every page.
- Inspect available command help for actual options; do not invent a command API.
- Resolve IDs and inspect changed ADRs, capabilities and stories, work-unit workflow records and available check
  artifacts.
- Treat checkout-only lookup output as a working-tree observation: reconcile it against the captured SHA before
  citing it as committed evidence.
- Dirty documents are never attributed to committed history. Include uncommitted content only when explicitly
  selected, preserving a diff/artifact reference and labeling it separately.

Inventory each source with revision, scope, observed time, result and artifact/path citation.

- Distinguish events inside the interval from the current snapshot.
- Git author/committer times are discovery hints, not integration proof. Each dated claim names its timestamp
  basis.
- Without established integration time, report reachable changes with that limitation; never claim they
  integrated in the week.
- Snapshot evidence predating the interval stays a snapshot, not a new event.
- Cite each factual claim using commit plus path/document ID, work-unit envelope or check artifact; label
  assessments separately.

Corroborate delivery:

- For completed spec work, corroborate completed status with tasks, verification/reconcile evidence and delivered
  commit reachability from the captured integration SHA (`git merge-base --is-ancestor <commit> <integration-sha>`).
- For session work, cite the change, verification report and reachability.
- An accepted proposal, checked task or commit alone proves no delivery.
- Separate implementation complete but integration unverified from completed work; missing evidence lowers the
  claim to unverified.
- Never infer remote release or deployment.

After collection and before artifact verification, capture HEAD, integration ref and relevant dirty-content state
again. Compare content/diffs, not only path names. If state changed, restart against new captured revisions or
mark affected evidence unverified; do not mix snapshots silently. Preserve unrelated edits.

## 3. Assess health, comparisons and actions

Reuse available hygiene, drift and review/refactoring artifacts; checks cover only their recorded revision and
scope.

- Record missing, stale, failed and not-comparable explicitly with reasons.
- A stale result can be historical evidence but never a current clean verdict.
- Optional source failure permits generation with limitations.

Compare only compatible scope, finding identity and supporting evidence:

- Match an existing feedback/proposal ID first, otherwise source, affected target and substantive discrepancy.
- Label first observations new and evidenced continuing findings recurring. Label a finding resolved only with
  direct resolution evidence covering that finding.
- Absence from a report is unknown, not resolved.
- Record a missing prior report or incompatible scope as explicit non-comparability.

Rank next actions by demonstrated impact and urgency; state the reason and concrete next step. Link matching open
feedback/proposals instead of creating duplicates. Terminal feedback is traceability, never reopened by history.

## 4. Write and verify the immutable report

Include these six sections, with evidence links and separately labeled assessments:

1. Identity: logical key, run ID, superseded run if any, repository, interval/offsets/timezone, scope, captured
   revisions, dirty state, generation timestamp and complete evidence inventory.
2. Completed work and integration evidence; separate unintegrated or unverified implementation.
3. Added/changed ADRs and significant behavior changes with document IDs and commit evidence.
4. Repository health with per-source revision, scope, observed time, result and explicit gaps.
5. Unresolved problems and prioritized next actions with reasons, steps and existing follow-up links.
6. Named prior report comparison, limitations and generation outcome; reference the companion publication outcome
   record as the authoritative mutable status, with publication initially pending.

Verify that the local artifact exists, its identity matches intake and each evidence link resolves or is
explicitly marked unavailable/unverified. Only then is generation completed.

- If writing, reading back or verifying identity fails, generation fails; do not publish an incomplete artifact.
- After verification, compute a content digest (SHA-256). Report bytes are now immutable.
- Changed content needs a new run, including changed evidence on a rerun.

## 5. Record and separately publish

Create a local companion outcome record containing run ID, artifact reference, SHA-256 digest, generation outcome,
publication outcome, destination, authority basis, attempts and receipt/link or error evidence.

- Preserve earlier attempts.
- Publication changes this record, never the report bytes.
- A missing outcome record prevents publication; it does not erase an already verified report.
- Generation and publication outcomes remain independent.

| Publication outcome | Evidence and action |
| --- | --- |
| pending | No destination, authority, publisher or permission; preserve the local artifact and state what is missing. |
| published | Existing authorized tool returned a destination receipt/link and destination content/run/digest was verified. |
| failed | Confirmed publication failure; retain error evidence and successful generation. |
| unknown | Lost response or destination cannot be verified; retain uncertainty and do not blindly retry. |

Publish only to an explicitly user-selected destination under explicit authority, using an existing authorized
connector/command.

- Invocation or integration policy grants no publication authority. No upload, message, commit, push or other
  external mutation follows implicitly.
- Check destination collisions before sending; replacement requires explicit authority identifying the existing
  target.
- Recheck the local digest immediately before publishing.

Retry with the same run ID and exact bytes/digest:

- Before retrying `unknown`, inspect destination state for that run and digest. A verified match records
  `published` without resending.
- If the state is unverifiable, leave it `unknown` and request a disposition instead of duplicating publication.
- A confirmed absence permits retry only within the existing publication authority.
- Confirmed different content is a collision, never an implicit replacement.

Finish by naming the local artifact, generation outcome, publication outcome, evidence limitations and next
steps. A publication failure never changes completed generation. Controlled exercises label simulated authority
and receipts and never imply a real external publication.
