---
name: weekly-report
description: Manually generate a revision-bound weekly repository progress report with delivery evidence, health gaps and prioritized actions, then separately publish only to an authorized destination.
---

# Weekly report

Run only when the user invoked or confirmed this playbook (`devkit-playbook`, `devkit playbook get
maintenance/weekly-report` or a confirmed intake offer); load the returned bundle context once. Use existing tools and authorized connectors only. Generation runs no maintenance
sweep, full test suite, automatic fix, feedback or proposal creation, and changes no source.

## 1. Capture identity and interval

1. Record a credential-free repository identity, scope, HEAD SHA, integration ref and its SHA, generation time and
   dirty paths with local Git only (`git rev-parse HEAD`, `git rev-parse <ref>^{commit}`, `git status --short`); do
   not fetch or switch branches. A missing identity fails generation; a local ref does not prove remote freshness.
2. Use the user's start, end and timezone, or the previous complete Monday 00:00 to Monday 00:00 week in the user's
   timezone (ask if it is unknown). Record inclusive start, exclusive end, timezone and both UTC offsets; resolve
   local boundaries before converting (a DST week has 167 or 169 hours). A reversed, ambiguous or unresolved
   interval fails generation.
3. Write to the owning work unit's materials or the repository's materials location (ask if neither exists) as an
   ordinary local file: not a seven-day shared artifact, and not a tracked file on the default branch without the
   user's say. Use a prior report only when the user names one.
4. Key the report by identity, scope and exact interval. Give each run a unique ID and a new, exclusively created
   file; a rerun names the run it supersedes and never overwrites it.

## 2. Gather evidence

Read committed content at the captured SHA (`git show <sha>:<path>`). Where document lookup is installed, include
historical documents (`--history`: completed specs, superseded ADRs, settled feedback), all namespaces and every
page, and check command help for actual options. Treat checkout-only lookup output as a working-tree observation
until reconciled with the SHA; include uncommitted content only when selected, labeled separately.

- Inventory each source with revision, scope, observed time, result and citation. Cite each claim by commit and
  path or ID; label assessments.
- Separate events inside the interval from the current snapshot. Git author and committer times are hints: name
  each dated claim's timestamp basis, and never call a change integrated in the week without integration evidence.
- Count spec work as delivered only with tasks, verification or reconcile evidence and reachability from the
  integration SHA (`git merge-base --is-ancestor <commit> <integration-sha>`); session work needs the change, its
  verification and reachability. Report the rest as unverified, and never infer release or deployment.
- Before writing, recapture HEAD, integration ref and dirty content; if they changed, restart or mark the affected
  evidence unverified.

## 3. Assess health, comparisons and actions

- Reuse hygiene, drift and review artifacts for their recorded revision and scope. Record missing, stale, failed or
  not-comparable sources with reasons; a stale result is never a current clean verdict, and a failed optional source
  is a limitation.
- Compare with the named prior report only on compatible scope, matching by feedback or proposal ID, else by source,
  target and discrepancy. Label findings new, recurring or, with direct evidence, resolved; absence is unknown.
- Rank next actions by demonstrated impact and urgency, each with its reason and step. Link open feedback and
  proposals instead of duplicating them; never reopen terminal ones.

## 4. Write and verify the report

Write six sections: identity and evidence inventory; completed and integrated work, then unverified work; changed
ADRs and behavior with IDs and commits; health per source with gaps; problems and ranked actions; prior comparison,
limitations, generation outcome and a link to the outcome record.

Read the file back and check its identity and every evidence link, or mark the link unavailable. Only then is
generation complete; otherwise it fails and nothing is published. Record its SHA-256; changed content needs a new run.

## 5. Record and publish

Create a companion outcome record: run ID, artifact, digest, generation outcome, publication outcome, destination,
authority, attempts and evidence. Publication changes only this record.

| Publication outcome | Evidence and action |
| --- | --- |
| pending | No destination, authority, publisher or permission; preserve the local artifact and state what is missing. |
| published | An authorized tool returned a receipt or link, and the destination's content, run and digest were verified. |
| failed | Confirmed failure; retain the error evidence and the successful generation. |
| unknown | Lost response or unverifiable destination; do not retry blindly. |

Publish only to a destination the user selected, under the user's explicit authority, with an existing connector or
command; nothing external happens implicitly. Check collisions first, replace a target only with authority naming
it, and recheck the digest. Retry with the same run ID and bytes. Before retrying `unknown`, inspect the
destination: a verified match is `published`, an unverifiable state stays `unknown` for the user to decide, and
different content is a collision.

Finish by naming the artifact, both outcomes, limitations and next steps; in an exercise, label simulated authority
and receipts.
