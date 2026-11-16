# Observed case timeline and option assessment

Evidence for `FB-draft-precedence-claim-unenforced`, read in this worktree (branch `plan-proposal-precedence-edges`).

## Timeline (2026-11-16, +0900)

| Time | Commit | Event |
| --- | --- | --- |
| 17:37:18 | `c30d5b859` | `PROP-design-document-lifecycle` and `PROP-design-document-viewer` queued; both later `accepted` with `depends_on` naming only `SPEC-formal-document-kinds`. |
| 19:46:37 | `7df4a6396` | `spec: hand off design-document-lifecycle to Development` (on `dev-design-document-lifecycle`). |
| 19:48:50 | `f32b831f7` | `spec: hand off design-document-viewer to Development` (on `dev-design-document-viewer`). |
| 19:51:11 | `7fa1ce56a` | `PROP-design-bundle-layout` drafted. Its body claims its handoff precedes both handoffs and argues the change is cheap because neither has a spec yet (`proposal.md:60,83,109,133` at that commit). |

At `7fa1ce56a` the base still lists both proposals as `status: accepted`: handoff commits live on `dev-<slug>` until
integration, so a base or HEAD read cannot tell an accepted proposal from one already handed off.

## What would have caught it

- A handoff-time check (reverse `depends_on` or a `precedes:` field read by `devkit spec proposal handoff`) could not:
  both handoffs ran before the draft and its claim existed.
- A check at the moment the claim is written (draft authoring) would have: both `dev-` branches existed at 19:51.
  The check must include local and fetched `dev-<slug>` branches, not only the base `status`.
- The same check at the first Planning turn catches a claim that went stale while the draft waited in Backlog.

## Option assessment

| Option | Catches observed case | Cost and conflicts |
| --- | --- | --- |
| `precedes:` field on the draft, checked by handoff | No (timing) | New reference field in `devkit-docs` (excluded), reverses the successor-declared edge choice of `ADR-roadmap-and-milestones-ledger` (the `after`-style edge was rejected as reading both ways). |
| Reverse `depends_on` added to accepted dependents + handoff notice | No (timing) | Edits an accepted proposal, which `ADR-proposal-acceptance` forbids, and needs a rule 13 exception in `CAP-DLV-proposal-planning`. |
| Status report in `devkit spec proposal check` | Partly | The command is the Backlog editability guard; it refuses once Planning starts, so it cannot report at Planning start. Prose claims carry no mechanical edge to read. |
| Guidance: verify named proposals (base `status` plus `dev-<slug>` branches) at authoring and at the first Planning turn | Yes | Two bundle reference edits, one capability sentence, one bundle-text test. |

## Handoff noise sample (challenger, `challenger-01.yaml` finding 5)

Of 81 `spec: hand off` commits, 16 carried `depends_on`; only `7264bb43d` and `b671dd684` (both 2026-10-28) handed off
with an unfinished prerequisite. A handoff-time prerequisite notice would be rare and duplicates the pickup override
of the direct unit prerequisite procedure.
