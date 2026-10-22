---
name: weekly-report
description: Manually generate a revision-bound weekly repository progress report with delivery evidence, health gaps and prioritized actions, then separately publish only to an authorized destination.
---

# Weekly report

Run only on explicit invocation for this task, through `devkit-playbook` or exact
`devkit playbook get maintenance/weekly-report`; selecting or retrieving the playbook does not run it. Load the
returned bundle context once per agent context.

- Use existing repository tools and authorized connectors; build no scheduler, detector, history store or publisher.
- Generation runs no maintenance sweep, full test suite, automatic fix, feedback creation or proposal creation.
- Preserve unrelated edits throughout.

## 1. Capture identity and interval

1. Record a credential-free repository identity (canonical local path or configured remote), selected scope,
   inspected commit SHA, integration branch/ref and resolved SHA, generation timestamp and dirty paths.
   - Use local Git inspection, for example `git rev-parse HEAD`, `git rev-parse <integration-ref>^{commit}` and
     `git status --short`; do not fetch, switch branches or modify sources.
   - If a required identity is unavailable, generation fails. A local integration ref does not prove remote
     freshness.
2. Fix the interval:
   - Accept explicit start/end timestamps and timezone, or use the previous complete Monday 00:00 to Monday 00:00
     calendar week in the configured user timezone. If the timezone is unknown, ask for it.
   - Record inclusive start, exclusive end, timezone name and UTC offsets at both boundaries.
   - Resolve local calendar boundaries before converting to UTC: a DST week may be 167 or 169 hours.
   - An event exactly at start belongs; one exactly at end does not.
   - If the interval is reversed, ambiguous or unresolved, generation fails until it is resolved.
3. Select a local artifact location explicitly:
   - Default to the owning work unit's materials or the repository's existing materials location; if neither
     exists, ask for it.
   - Do not create a tracked report on the default branch without the user's say.
   - Keep the report an ordinary local file, not a seven-day shared artifact.
   - Record a prior report only when the user names one; do not search history for one.
4. Build a logical report key from repository identity, scope and exact interval/timezone.
5. Allocate a unique run ID, source SHA and new filename, checking collisions and creating the file exclusively. A
   rerun names any superseded run and preserves its artifact; never overwrite another run.

## 2. Gather revision-bound evidence

Default to committed content at the captured SHA (`git show <sha>:<path>`, local history and reachability checks).

- Where document lookup is installed, include completed specs with `--history`, all intended namespaces and
  every page.
- Read the available command help for actual options instead of assuming a command API.
- Resolve IDs and inspect changed ADRs, capabilities and stories, work-unit workflow records and available check
  artifacts.
- Treat checkout-only lookup output as a working-tree observation: reconcile it against the captured SHA before
  citing it as committed evidence.
- Never attribute dirty documents to committed history. Include uncommitted content only when explicitly selected,
  with a diff/artifact reference and a separate label.

Inventory each source with revision, scope, observed time, result and artifact/path citation.

- Distinguish events inside the interval from the current snapshot; snapshot evidence predating the interval is
  not a new event.
- Use Git author/committer times as discovery hints, not integration proof, and name the timestamp basis of each
  dated claim. Without established integration time, report reachable changes with that limitation, never as
  integrated in the week.
- Cite each factual claim by commit plus path/document ID, work-unit envelope or check artifact; label assessments
  separately.

Corroborate delivery:

- For completed spec work, corroborate completed status with tasks, verification/reconcile evidence and delivered
  commit reachability from the captured integration SHA (`git merge-base --is-ancestor <commit> <integration-sha>`).
- For session work, cite the change, verification report and reachability.
- An accepted proposal, checked task or commit alone proves no delivery; missing evidence lowers a claim to
  unverified. Report implementation that is complete but not verified as integrated separately from completed work.
- Never infer remote release or deployment.

After collection and before artifact verification, capture HEAD, integration ref and relevant dirty-content state
again and compare content and diffs, not only path names. If the state changed, restart against the new revisions
or mark the affected evidence unverified; never mix snapshots silently.

## 3. Assess health, comparisons and actions

Reuse available hygiene, drift and review/refactoring artifacts; a check covers only its recorded revision and
scope.

- Record missing, stale, failed and not-comparable sources explicitly with reasons.
- Cite a stale result as historical evidence, never as a current clean verdict.
- If an optional source fails, continue generation and state the limitation.

Compare only compatible scope, finding identity and supporting evidence:

- Match an existing feedback/proposal ID first, otherwise source, affected target and substantive discrepancy.
- Label first observations new and evidenced continuing findings recurring. Label a finding resolved only with
  direct resolution evidence covering that finding; absence from a report is unknown, not resolved.
- Record a missing prior report or incompatible scope as explicit non-comparability.

Rank next actions by demonstrated impact and urgency, each with its reason and concrete next step. Link matching
open feedback/proposals instead of creating duplicates; cite terminal feedback for traceability, never reopen it.

## 4. Write and verify the immutable report

Write these six sections, with evidence links and separately labeled assessments:

1. Identity: logical key, run ID, superseded run if any, repository, interval/offsets/timezone, scope, captured
   revisions, dirty state, generation timestamp and complete evidence inventory.
2. Completed work and integration evidence; separate unintegrated or unverified implementation.
3. Added/changed ADRs and significant behavior changes with document IDs and commit evidence.
4. Repository health with per-source revision, scope, observed time, result and explicit gaps.
5. Unresolved problems and prioritized next actions with reasons, steps and existing follow-up links.
6. Named prior report comparison, limitations and generation outcome; reference the companion outcome record as
   the authoritative publication status, initially pending.

Verify that the local artifact exists, its identity matches intake and each evidence link resolves or is marked
unavailable/unverified. Only then is generation completed.

- If writing, reading back or verifying identity fails, generation fails; publish nothing.
- After verification, compute a SHA-256 content digest. The report bytes are now immutable; changed content,
  including changed evidence on a rerun, needs a new run.

## 5. Record and separately publish

Create a local companion outcome record with run ID, artifact reference, SHA-256 digest, generation outcome,
publication outcome, destination, authority basis, attempts and receipt/link or error evidence.

- Publication updates this record and keeps earlier attempts; it never changes the report or its generation
  outcome.
- Without an outcome record, do not publish; the verified report stays valid.

| Publication outcome | Evidence and action |
| --- | --- |
| pending | No destination, authority, publisher or permission; preserve the local artifact and state what is missing. |
| published | Existing authorized tool returned a destination receipt/link and destination content/run/digest was verified. |
| failed | Confirmed publication failure; retain error evidence and successful generation. |
| unknown | Lost response or destination cannot be verified; retain uncertainty and do not blindly retry. |

Publish only to a destination the user selected, under the user's explicit authority, with an existing authorized
connector or command.

- Invocation or integration policy grants no publication authority; no upload, message, commit, push or other
  external mutation follows implicitly.
- Check destination collisions before sending; replace an existing target only under explicit authority naming it.
- Recheck the local digest immediately before publishing.

Retry with the same run ID and exact bytes/digest:

- Before retrying `unknown`, inspect destination state for that run and digest. On a verified match, record
  `published` without resending.
- If the state is unverifiable, leave it `unknown` and ask the user for a disposition instead of publishing again.
- After a confirmed absence, retry only within the existing publication authority.
- Treat confirmed different content as a collision, never as an implicit replacement.

Finish by naming the local artifact, generation outcome, publication outcome, evidence limitations and next
steps. In a controlled exercise, label simulated authority and receipts and imply no real external publication.
